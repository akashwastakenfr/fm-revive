# AI Handover & Zero-Context Onboarding

Read this file completely before suggesting commands, code edits, or diagnoses.

## 1. Strict Rules
1. Never confuse **Confirmed** facts with **Hypotheses** or **Unknowns**.
2. Do not repeat completed work (APKM extraction, JADX decompilation, Stage 1 `config.ini` diagnosis, and `0x4e69764` byte-decoder reversing are DONE).
3. Keep Termux commands short (user works on an Android phone) and save large outputs to `source/dumps/` or `logs/`.
4. Always run `llvm-objdump` / `llvm-readelf` on `libFIFAMobileNeon.so.original`, NOT `libFIFAMobileNeon.so`.
5. Document every breakthrough in `discoveries/`.
6. Never commit `.apk`, `.apkm`, `.so*`, `jadx-out/`, `logs/`, or `server/data/captures/`.

## 2. Confirmed Facts (Do Not Re-Investigate)
- **Target APK:** `com.ea.gp.fifamobile` v18.1.03 (40214), `FifaMainActivity`, Target SDK 33, Min SDK 21. `assets/Data/FIFA/icfiles.big` is 24 KB (bootstrap client).
- **Stage 1 (`Error_HostName_Message` — RESOLVED):**
  - `"Unable to access the configuration of current build..."` is `Error_HostName_Message` in `assets/Data/DynamicAssets/android/lang_BOOTSTRAP_EN_US.properties`.
  - Patched client connects to `http://127.0.0.1:8080` and requests `GET /config/Android/18.1.03/config.ini`.
  - `ConfigService._config_verifyFifaMobileHostNameFetch` (`0x129a57c` -> `0x118f8e8`) parses the INI via `0x1269058(..., "", "")` -> `0x12687f8` and checks `0x126a744(map, "hostName")` (`0x8380030` -> `0x6862770`). No RSA/HMAC signature is checked.
  - `0x12687f8` (`0x1268a18`–`0x1268af8`) ONLY reads `[default]`, `[platform]`, and a 6-byte section (`0x686b02a`), ignoring `[FIFAMobileApp]`.
  - Changing `[FIFAMobileApp]` to `[default]` in `server/data/responses/default-config.ini` resolved Stage 1 completely.
- **Stage 2 (`POST /g/game/batch` — IN PROGRESS):**
  - Client sends binary protobuf RPC batches to `POST /g/game/batch` (`User-Agent: ProtoHttp 1.3/DS 15.1.3.0.4 (Android)`, `Content-Type: application/x.binary`).
  - `BatchResponseCollection` uses protobuf group (wire type 3/4, field 1, `vtable+0x190` at `0x4b15b94`) wrapping `BatchResponse` (field 1 varint `status`, field 2 bytes `payload`, field 3 double `checksum`).
  - `0x56f30c0` checks `BatchResponse.status == 200` (`0xc8`). `get_checksum()` is unused in `0x56f3024..0x56f3360`.
  - On first `status=200` `BatchResponse`, `0x56f39f8..0x56f3af8` strips `2*[0x886a928] + 4 = 14` bytes from the end of `payload`, feeds 4 seed bytes + `ldrb [0x886a8f0]` into `0x4e68fdc`, caches `[0x886a910]`, and decodes payload bytes via `0x4e69764`.
  - `0x4e69764` (`0x4e69868..0x4e69884`): if `ldrb w8, [x20, #0x8]` is `0`, returns byte unchanged; else returns `([x20 + 0xc] * byte) & 0xff`.
  - `server/main.py` is wired to `server/modules/batch.py` (`handle_batch`). Live Termux runs show `[BATCH] id=1 endpoints=['game/system/settings']` ... `id=6 endpoints=['game/telemetry/logNonSessionEvent', 'game/system/settings']`.

## 3. Current Blocker & Exact Next Steps
Even with `server/modules/batch.py` returning `status=200` and `SystemSettings` protobuf groups, the client retries `game/system/settings` (`id=1..6`) until `Error_RpcTimeout` (`SERVER CONNECTION ISSUE : Your connection with EA servers has been lost...`).

**Next checks in order:**
1. Inspect `is_retry` and `payload_hex` in the latest `/g/game/batch` captures in `server/data/captures/` to confirm whether `id=2..6` are retries of `id=1` (`is_retry=1`) or distinct calls.
2. Inspect `source/dumps/batch_rpc/sysset-mergefrom.txt` (lines 105–185) and the completion callback called at `0x56f3220` (`SettingsService._onGetInitialSettingsComplete`) in `libFIFAMobileNeon.so.original` to confirm:
   - Whether `SystemSettings` expects wire type 3/4 groups (`0x0b..0x0c`) or wire type 2 messages (`0x0a`),
   - Whether `0x56f3a24..0x56f3af8` accepted the `b"\x00" * 14` trailer cleanly on `id=1`,
   - Which keys/values `SettingsService` requires before moving on to `system/getServerTime`, `content/init`, and `user/login`.
---

## 4. Additive Update (Stage 2 Checksum Resolved -> Stage 3 Reached)
- **Confirmed (`0x57017cc`, `0x57015c0`, `0x719f110`):** `BatchResponse` field `3` (`checksum`) is a 32-bit varint (`wire type 0`, not double). `RpcService._validateResponse` requires `CRC32(raw_payload + bytes.fromhex("22ecd02d437fdc88")) & 0xFFFFFFFF` whenever `[x19, #0xf8]` (`batch_checksum_enabled`) is `1`.
- **Live Result:** With `field 3` added in `server/modules/batch.py`, the client passed `game/system/settings`, showed and accepted the birthdate age-gate, and reached `0KB/0KB GETTING WARMED UP.....` (`RESOURCE DOWNLOAD ERROR`).
- **Next Steps (Stage 3):**
  1. Fix/neutralize the `b"\x00" * 14` first-response trailer so `0x4e68fdc` does not obfuscate `id=1+` request endpoints (notice `id=1` arrived as `\x00\x00...` when seed was all-zeros, or `0x4e69764`-encoded bytes).
  2. Inspect the latest `server/data/captures/*.json` from this run and implement `content/init` / resource download responses.
