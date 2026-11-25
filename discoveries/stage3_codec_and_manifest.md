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

## 3. `manifest.db` Live Test & SQLite Schema (`0x128c514..0x128c678`)
- **Confirmed (`0x128c5a4..0x128c678`):**
  - Client downloads `GET /assets/manifest.db` and opens it directly via `sqlite3_open_v2` (`0x128c5c4`, raw SQLite—not gzipped).
  - Prepares `SELECT src,length,crc FROM resources WHERE name = ?` (`0x686cb5f` -> `0x128c514..0x128c570`).
- **Live Result:**
  - Created `server/data/responses/manifest.db` with `CREATE TABLE resources (name TEXT PRIMARY KEY, src TEXT, length INTEGER, crc INTEGER)` and mapped `GET /assets/manifest.db` (`content_type: application/x.binary`) in `server/config/routes.json`.
  - Client downloaded `12KB/12KB` (100% green bar) and advanced from `GETTING WARMED UP.....` to `KICKING OFF.....`, then threw `RESOURCE DOWNLOAD ERROR` because `resources` has 0 rows and no `.big` / `DynamicAssets` files exist on device (`/sdcard/Android/data/com.ea.gp.fifamobile/files/external` only) or in the workspace.

## 4. SQLCipher Key (`aes256:mcryan`), Bundled Assets, & `manifest.db` Row Lookup
- **SQLCipher / `wxSQLite3` Key (`0x127ae24`, `0x1271754`):**
  - `0x6d52789` (13 bytes) XOR `0x6d44cf5` (13 bytes) = `b"aes256:mcryan"`.
  - `0x128c5c4..0x128c600`: Downloads plain SQLite `manifest.db`, opens with `sqlite3_open_v2`, and encrypts in-place via `0x21ad9c4` (`sqlite3_rekey_v2`, `zDb=NULL`).
  - `0x128c348..0x128c370`: Opens cached `manifest.db` with `0x21ac714` (`sqlite3_key`) and prepares `SELECT src,length,crc FROM resources WHERE name = ?` (`0x128c570`).
- **Row Lookup (`0x128d960..0x128da14`):**
  - `0x128d9b0`: `sqlite3_bind_text` (arg `name`)
  - `0x128d9c4`: `sqlite3_step` (`100`/`0x64` = `SQLITE_ROW`, `101`/`0x65` = `SQLITE_DONE` -> `0x128da68` not-found)
  - `0x128d9e8..0x128da14`: reads `src` (col 0), `length` (col 1), `crc` (col 2).
- **Bundled Assets & Error Key:**
  - `apk/base_extract/assets/Data/` already contains `83 MB` (`1,047` files in `DynamicAssets/android/` + `FIFA/icfiles.big` 24 KB).
  - `lang_BOOTSTRAP_EN_US.properties`: `Splash_85_Percent=KICKING OFF...`, `Error_Resource_Header=RESOURCE DOWNLOAD ERROR`.
