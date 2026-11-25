# AI Handover & Zero-Context Onboarding

Read this file completely before suggesting commands, code edits, or diagnoses.

## 1. Strict Rules
1. Never confuse **Confirmed** facts with **Hypotheses** or **Unknowns**.
2. Do not repeat completed work (APKM extraction, JADX decompilation, Stage 1 `config.ini` diagnosis, and Stage 2 byte-decoder reversing are DONE).
3. Keep Termux commands short (user works on an Android phone) and save large outputs to `source/dumps/` or `logs/`.
4. Always run `llvm-objdump` / `llvm-readelf` on `libFIFAMobileNeon.so.original`, NOT `libFIFAMobileNeon.so`.
5. Document every breakthrough in `discoveries/`.
6. Never commit `.apk`, `.apkm`, `.so*`, `jadx-out/`, `logs/`, or `server/data/captures/`.

## 2. Current State of Progress (Confirmed)
- **Stage 1 (HostName Fetch):** RESOLVED. Client connects to `http://127.0.0.1:8080/config/Android/18.1.03/config.ini`. INI section must be `[default]`.
- **Stage 2 (Batch Protobuf):** RESOLVED. Client sends `POST /g/game/batch`. Response uses `BatchResponseCollection` groups (wire type 3/4). Trailer is `b"\x00"*5 + b"\x00\x00\x00\x01" + b"\x00"*5` (`w2=1` identity). `game/system/settings` and `game/loginvideo/getCurrentVideo` pass cleanly.
- **Stage 3 (Asset Download & Manifest):**
  - Client requests `GET /assets/manifest.db`.
  - Client opens it via `sqlite3_open_v2` and encrypts it with `aes256:mcryan` (`sqlite3_rekey_v2`).
  - Client reaches 85% (`Splash_85_Percent = "KICKING OFF....."`).
  - Client throws `Error_Resource_Header` (`RESOURCE DOWNLOAD ERROR`) because `resources` table in `manifest.db` is currently empty.
  - At `0x556e78c..0x556e790`, `DeviceManifestService` checks if resource download queue length is `> 0`. With 0 rows, it takes the failure branch directly into `Error_Resource_Header`.

## 3. Exact Current Blocker & Next Investigation Step
The game needs startup resource rows in `server/data/responses/manifest.db`:
- Lookup query: `SELECT src,length,crc FROM resources WHERE name = ?` (caller at `0x1276dc0`).
- Disassemble `0x558bca0` (the target of `_parseStaticResources` dispatch at `0x558c4ac..0x558c4d4`) to determine the exact keys queried during startup.
- Populate `resources` table in `manifest.db` with matching rows (e.g. `icfiles.big`, `shaderboot.big`).
