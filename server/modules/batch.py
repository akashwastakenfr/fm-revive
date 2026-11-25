import zlib

BATCH_CHECKSUM_SECRET = bytes.fromhex("22ecd02d437fdc88")

_first_response_pending = True


def reset_session():
    global _first_response_pending
    _first_response_pending = True


def encode_varint(n: int) -> bytes:
    out = bytearray()
    n &= 0xFFFFFFFFFFFFFFFF
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            break
    return bytes(out)


def encode_field_varint(field_no: int, val: int) -> bytes:
    return encode_varint((field_no << 3) | 0) + encode_varint(val)


def encode_field_bytes(field_no: int, data: bytes) -> bytes:
    return encode_varint((field_no << 3) | 2) + encode_varint(len(data)) + data


def encode_group(field_no: int, inner: bytes) -> bytes:
    return encode_varint((field_no << 3) | 3) + inner + encode_varint((field_no << 3) | 4)


def _read_varint(buf: bytes, pos: int):
    val = 0
    shift = 0
    while pos < len(buf):
        b = buf[pos]
        pos += 1
        val |= (b & 0x7F) << shift
        if not (b & 0x80):
            return val, pos
        shift += 7
    raise ValueError("Truncated varint")


def _parse_fields(buf: bytes, end_group_tag: int | None = None):
    pos = 0
    fields = []
    while pos < len(buf):
        tag, pos = _read_varint(buf, pos)
        field_no = tag >> 3
        wire = tag & 0x7
        if wire == 4:
            if end_group_tag is not None and field_no == end_group_tag:
                return fields, pos
            return fields, pos
        elif wire == 0:
            val, pos = _read_varint(buf, pos)
            fields.append((field_no, wire, val))
        elif wire == 1:
            fields.append((field_no, wire, buf[pos:pos + 8]))
            pos += 8
        elif wire == 2:
            ln, pos = _read_varint(buf, pos)
            fields.append((field_no, wire, buf[pos:pos + ln]))
            pos += ln
        elif wire == 3:
            sub, consumed = _parse_fields(buf[pos:], end_group_tag=field_no)
            pos += consumed
            fields.append((field_no, wire, sub))
        elif wire == 5:
            fields.append((field_no, wire, buf[pos:pos + 4]))
            pos += 4
        else:
            raise ValueError(f"Unknown wire type {wire}")
    return fields, pos


def decode_batch_collection(raw: bytes) -> dict:
    try:
        top, _ = _parse_fields(raw)
    except Exception as e:
        return {"parse_error": str(e), "items": []}

    batch_id = None
    items = []
    for fno, wire, val in top:
        if fno == 2 and wire == 0:
            batch_id = val
        elif fno == 1 and wire == 3:
            item = {"endpoint": "", "payload_hex": "", "id": None, "is_retry": None}
            for sfno, swire, sval in val:
                if sfno == 1 and swire == 2:
                    item["endpoint"] = sval.decode("utf-8", errors="replace")
                elif sfno == 2 and swire == 2:
                    item["payload_hex"] = sval.hex()
                elif sfno == 3 and swire == 0:
                    item["id"] = sval
                elif sfno == 4 and swire == 0:
                    item["is_retry"] = sval
            items.append(item)
    return {"batch_id": batch_id, "items": items}


def encode_system_settings(settings: dict[str, str]) -> bytes:
    out = bytearray()
    for name, value in settings.items():
        entry = (
            encode_field_bytes(1, name.encode("utf-8"))
            + encode_field_bytes(2, value.encode("utf-8"))
        )
        out.extend(encode_group(1, entry))
    return bytes(out)


def build_rpc_payload(endpoint: str) -> bytes:
    if endpoint == "game/system/settings":
        return encode_system_settings({
            "obfuscation_enabled": "false",
            "batch_checksum_enabled": "false",
            "http_keepalive_enabled": "false",
        })
    return b""


def handle_batch(raw: bytes) -> tuple[bytes, dict]:
    global _first_response_pending
    decoded = decode_batch_collection(raw)
    items = decoded.get("items") or [{"endpoint": "unknown"}]

    collection = bytearray()
    for item in items:
        endpoint = item.get("endpoint", "")
        payload = build_rpc_payload(endpoint)
        if _first_response_pending:
            payload = payload + (b"\x00" * 14)
            _first_response_pending = False

        checksum = zlib.crc32(payload + BATCH_CHECKSUM_SECRET) & 0xFFFFFFFF
        resp_msg = (
            encode_field_varint(1, 200)
            + encode_field_bytes(2, payload)
            + encode_field_varint(3, checksum)
        )
        collection.extend(encode_group(1, resp_msg))

    print(f"[BATCH] id={decoded.get('batch_id')} endpoints={[i.get('endpoint') for i in items]}")
    return bytes(collection), decoded
