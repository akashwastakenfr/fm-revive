# Discovery 002: Stage 2 `/g/game/batch` Protobuf Protocol, Trailer & Byte Decoder

- **Context:** After fixing Stage 1 (`[default]` in `default-config.ini`), the client cleared `Error_HostName_Message`, entered the intro video, and displayed `Error_RpcTimeout` (`SERVER CONNECTION ISSUE : Your connection with EA servers has been lost`).
- **Confirmed Wire Protocol:**
  - Client sends binary protobuf batches to `POST /g/game/batch` (`User-Agent: ProtoHttp 1.3/DS 15.1.3.0.4 (Android)`, `Content-Type: application/x.binary`, `Accept: application/x.binary`).
  - First observed RPC endpoint inside `BatchCollection`: `game/system/settings`, followed in later batches by `game/telemetry/logNonSessionEvent`.
- **Confirmed Native Protobuf & Handler Behavior (`libFIFAMobileNeon.so.original`):**
  - `BatchResponseCollection` (`0x4b15a74..0x4b15ba0`): field 1 is a protobuf group (`vtable+0x190`) of `BatchResponse`.
  - `BatchResponse` (`0x4b13ea4..0x4b142f4`): field 1 (varint) = `status`, field 2 (bytes) = `payload`, field 3 (double on wire) = `checksum`.
  - `0x56f30b8..0x56f30d0`: checks `BatchResponse.get_status() == 200` (`0xc8`); non-200 branches to `0x56f3228` -> `Error_RpcTimeout`. `get_checksum()` is unused in this loop.
  - `0x56f39f8..0x56f3af8`: on the first `status=200` response (when `[0x886a910]` is null), strips `2 * [0x886a928] + 4 = 14` bytes (`[0x886a928] = 5`) from the end of `BatchResponse.payload`, extracts 4 seed bytes + `ldrb w1, [0x886a8f0]` into `0x4e68fdc`, caches `[0x886a910]`, and passes the stripped buffer to `0x4e69bcc`.
  - `0x4e69764` (`0x4e69868..0x4e69884`): byte decoder checks `ldrb w8, [x20, #0x8]`. If `0`, returns byte unchanged; if non-zero, returns `([x20 + 0xc] * byte) & 0xff`.
  - `0x56f3220`: invokes the per-item RPC completion callback (`vtable+0xd8`).
- **Server Wiring Update:**
  - Wired `POST /g/game/batch` in `server/main.py` to `server/modules/batch.py:handle_batch(raw)` (and `reset_session()` on `config.ini` fetch).
  - Live test confirmed Termux receives and decodes `id=1..6` (`game/system/settings`, `game/telemetry/logNonSessionEvent`), though `game/system/settings` still retries—under active investigation.