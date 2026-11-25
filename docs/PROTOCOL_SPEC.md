# FIFA Mobile 23 Client–Server Protocol Specification

*(Strictly separates **Confirmed** facts from **In Progress / Unverified** items.)*

## Stage 1: Bootstrap Configuration (Confirmed)

### Request
- Primary URL (`0x118ee00..0x118f1c4`): `GET /config/Android/<version>/config.ini?<uint64>` (observed live: `GET /config/Android/18.1.03/config.ini`)
- Fallback URL (`0x118f484..0x118f800`): `GET /config/Android/default/config.ini?<uint64>`
- Optional notice check observed live: `GET /config/`

### INI Verification & Parsing Rules (`0x118f8e8`, `0x1269058`, `0x12687f8`)
1. No RSA/HMAC signature is verified inside `config_verifyFifaMobileHostNameFetch__2` (`0x118f8e8`).
2. `0x12687f8` (`0x1268a18`–`0x1268af8`) **only** parses three section names:
   - `[default]` (7 bytes, `0x686ae1d`) — always loaded into map 1 (`[x20+0x58]`)
   - `[platform]` (8 bytes, `"platform"`) — filtered by platform arg `x2`
   - 6-byte section (`0x686b02a`) — filtered by arg `x3`
   *(Other sections like `[FIFAMobileApp]` are ignored when `x3=""`/`x4=""`.)*
3. Verification passes iff `"hostName"` (`0x8380030` -> `0x6862770`) exists in the parsed map (`0x126a744`).
4. On failure, `0x53c42d0` logs `HOST NAME VERIFY FAILED. url:` and displays `Error_HostName_Message` with `0x0000...hs=<sha1_of_body>, len=<byte_len>,`.

### Working Local Fixture (`server/data/responses/default-config.ini`)
```ini
[default]
hostName=http://127.0.0.1:8080
alternateHostName=http://127.0.0.1:8080
current_contents_version=18.1.03
current_server_version=18.1.03
client_version_override=
replay_version=1
latency_metrics_log_enabled=false
latency_metrics_log_sample_batch_size=1
latency_metrics_log_sample_size=1
batch_checksum_enabled=false
obfuscation_enabled=false
```

---

## Stage 2: Binary Protobuf RPC Batching (Confirmed + In Progress)

### Transport (Confirmed from Captures)
- **Endpoint:** `POST /g/game/batch`
- **Headers:** `User-Agent: ProtoHttp 1.3/DS 15.1.3.0.4 (Android)`, `Content-Type: application/x.binary`, `Accept: application/x.binary`

### Request Schema (`BatchCollection`) — Confirmed
- Field `1` (wire type 3/4 group, repeated): `Batch` item
  - Field `1` (bytes/string): `endpoint` (e.g. `"game/system/settings"`, `"game/telemetry/logNonSessionEvent"`)
  - Field `2` (bytes): `payload`
  - Field `3` (varint): `id`
  - Field `4` (varint): `isRetry`
- Field `2` (varint): `batchId`

### Response Schema (`BatchResponseCollection`) — Confirmed (`0x4b15a74`, `0x4b13ea4`, `0x56f30b8`)
- Field `1` (wire type 3/4 group, repeated): `BatchResponse`
  - Field `1` (varint): `status` (`200` / `0xc8` required at `0x56f30c0`)
  - Field `2` (bytes): `payload`
  - Field `3` (wire 64-bit double): `checksum` (unused in `0x56f3024..0x56f3360`)

### First-Response Trailer & Byte Decoder (`0x56f39f8..0x56f3af8`, `0x4e69764`) — Confirmed
- Global `[0x886a928]` = `5`.
- On first `status=200` response while `[0x886a910]` is null, client strips `2*5 + 4 = 14` bytes from the end of `payload`, extracts 4 big-endian bytes + `ldrb w1, [0x886a8f0]` into `0x4e68fdc`, caches `[0x886a910]`, and decodes payload bytes via `0x4e69764`.
- `0x4e69764`: if `ldrb [x20, #0x8] == 0`, returns byte unchanged; else returns `([x20 + 0xc] * byte) & 0xff`.

### `SystemSettings` (`game/system/settings`) — Under Investigation
- `SystemSettings`: Field `1` = `SystemSetting` list (`settingsList`)
- `SystemSetting`: Field `1` (string) = `name`, Field `2` (string) = `value`
- **Open Issue:** Server encodes `SystemSettings` field 1 as wire type 3/4 group and returns `obfuscation_enabled=false`, `batch_checksum_enabled=false`, `http_keepalive_enabled=false`, yet the client retries `game/system/settings` (`id=1..6`) until `Error_RpcTimeout`. Wire type (`0x0a` vs `0x0b`), trailer bytes, or missing settings keys are under investigation.

---

## Stage 2/3 Cataloged Endpoints (From `.rodata`, Unverified Live)
Mapped in `server/config/routes.json` (JSON stubs; live Stage 2/3 client behavior uses `/g/game/batch` protobufs for at least `system/settings` and `telemetry`):
- `system/getServerTime`, `system/settings`, `system/settings/authenticated`, `system/loc/get-client-overrides`, `system/session/create`, `system/ksession/create`
- `content/init`, `content/records`, `versionupdate/version`
- `user/age/get`, `user/login`, `user/load`, `user/settings`, `user/roster`, `user/inventory`, `user/isVeteran`, `user/lineup/`
- `unlockkey/getallkeys`, `stats/get`, `loginvideo/getCurrentVideo`, `loginbonus/status`
- Nimble/Synergy (`Java`): `/director/api/android/getDirectionByPackage`, `/user/api/android/getDeviceID`, `/user/api/android/validateDeviceID`, `/user/api/android/getAnonUid`