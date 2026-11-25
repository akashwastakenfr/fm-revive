# Stage 2/3 Breakthrough: Identity Codec Trailer (`w2=1`) & `manifest.db` Trigger

## 1. Byte-Codec Identity Fix (`0x56f3a54`, `0x56f3a78..0x56f3aec`, `0x4e691d8`)
- **Why `id=1+` endpoints arrived garbled (`\x00...` or `mult=102`):**
  - `0x56f3a54` checks `len(payload) > 14` (strictly greater than). When `id=0` began with `game/telemetry/logNonSessionEvent` (`0` bytes + `14` trailer = `14`), the client skipped it and initialized `0x4e68fdc` from `game/system/settings` instead (reading `'f'` = `0x66` = `102` from `"false"` as the multiplier).
  - `0x56f3a78..0x56f3adc` reads a 4-byte **big-endian** integer `w2` at bytes `[5:9]` of the 14-byte trailer (`[5 pad] + [4 BE uint32] + [5 pad]`) and stores `w2` into `[x20 + 0xc]` (`0x4e691d8`).
- **Fix in `server/modules/batch.py`:**
  - Consume `_first_response_pending` only when `len(payload) > 0`.
  - Use trailer `b"\x00" * 5 + b"\x00\x00\x00\x01" + b"\x00" * 5` (`w2 = 1`, identity `1 * byte == byte`).
- **Live Result:** `id=1` (`game/loginvideo/getCurrentVideo`) and `id=2` (`game/telemetry/logNonSessionEvent`, `game/system/settings`) now arrive in clean plaintext.

## 2. Stage 3 Asset Manifest Discovery (`pf_config_assets_manifest_url_db`)
- **Confirmed strings (`libFIFAMobileNeon.so.original`):**
  - `0x711f7f3`: `pf_config_assets_manifest_url_db`
  - `0x711f81c`: `pf_config_assets_manifest_url_xml`
  - `0x686cb5f`: `SELECT src,length,crc FROM resources WHERE name = ?` (adjacent to `Tmp`, `Parsed`, `Unz`).
- **Live Result:**
  - Adding `pf_config_assets_manifest_url_db=http://127.0.0.1:8080/assets/manifest.db` and `pf_config_assets_manifest_url_xml=http://127.0.0.1:8080/assets/manifest.xml` to `default-config.ini` and `SystemSettings` (`batch.py`) triggered the in-game `"Note : Client requires a Content Update..."` prompt.
  - Tapping **CONFIRM DOWNLOAD** made the client send `GET /assets/manifest.db` (`Accept: application/xml,image/png`, `User-Agent: ProtoHttp 1.3/DS 15.1.3.0.4 (Android)`) to `127.0.0.1:8080`.
- **Next Step:** Serve a valid SQLite `manifest.db` with table `resources(name, src, length, crc)` on `GET /assets/manifest.db` (and check if `Unz` means gzip/zip-wrapped).
