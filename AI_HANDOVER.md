# AI Handover & Zero-Context Onboarding

Read this file completely before suggesting commands, code edits, or diagnoses.

## 1. Strict Rules
1. Never confuse **Confirmed** facts with **Hypotheses** or **Unknowns**.
2. Do not repeat completed work (APKM extraction, JADX decompilation, Stage 1 `config.ini` diagnosis, and Stage 2 byte-decoder/checksum reversing are DONE).
3. Keep Termux commands short (user works on an Android phone) and save large outputs to `source/dumps/` or `logs/`.
4. Always run `llvm-objdump` / `llvm-readelf` on `libFIFAMobileNeon.so.original`, NOT `libFIFAMobileNeon.so`.
5. Document every breakthrough in `discoveries/`.
6. Never commit `.apk`, `.apkm`, `.so*`, `jadx-out/`, `logs/`, `server/data/captures/`, or the generated `server/data/responses/manifest.db`.

## 2. Current State of Progress (Confirmed)
- **Stage 1 (HostName Fetch):** RESOLVED. Client connects to `http://127.0.0.1:8080/config/Android/18.1.03/config.ini`. INI section must be `[default]`.
- **Stage 2 (Batch Protobuf):** RESOLVED. Client sends `POST /g/game/batch`. Response uses `BatchResponseCollection` groups (wire type 3/4), trailer `b"\x00"*5 + b"\x00\x00\x00\x01" + b"\x00"*5` (`w2=1`), and `BatchResponse` field 3 CRC32 checksum with `BATCH_CHECKSUM_SECRET = 22ecd02d437fdc88`.
- **Stage 3 (Asset Download & Manifest):**
  - Client receives `pf_config_assets_manifest_url_db` / `_xml`, requests `GET /assets/manifest.db`, opens it with `sqlite3_open_v2`, rekeys in-place with `aes256:mcryan` (`sqlite3_rekey_v2`), and reaches 85% (`KICKING OFF.....`).
  - Client then shows `Error_Resource_Header` (`RESOURCE DOWNLOAD ERROR`) without requesting any `.xml` or `.big` files over HTTP.
  - The old `server/data/responses/manifest.db` had table `resources(name TEXT PRIMARY KEY, src TEXT, length INTEGER, crc INTEGER)` with **0 rows**.
  - `DeviceManifestService` (`0x5568000..0x5596000`) field layout confirmed via `__Visit` (`0x558d200..0x558d740`): `+0x58` is `_manifestLoadOp`, `+0x60` is `_assetErrorPublisher`, `+0x68` is `_staticResources`.
  - `0x556e654` (`Error_Resource_Header`) is the error callback (`_onAssetError` at `0x5572104 -> 0x556e654`; closure `0x556e49c` bound at `0x556e260` / `0x558a9e0`). At `0x556e77c..0x556e790`, it checks `_manifestLoadOp` (`[x20, #0x58]`).
  - `_parseStaticResources` (`0x558bca0..0x558bcdc`) is a 16-instruction wrapper calling `0x5585ae4`, which parses `manifest_cache_static` / `manifest_paths` / `manifest_cache_static_path_index`.
  - `_loadAllManifests` (`0x5589b68 -> 0x5585eb8`) checks `pf_manifest_url_*`, `pf_config_assets_manifest_url_*`, and `optools_manifest_url_*`. Currently `default-config.ini` and `server/modules/batch.py` only set `pf_config_assets_manifest_url_*` (not `pf_manifest_url_db` or `manifest_paths`).
  - Native `MaddenSocial::ManifestManager` (`0x1275000..0x128e000`) wraps `SELECT src,length,crc FROM resources WHERE name = ?` (`0x128d8f0`) via `0x1276b94`, and `0x127761c` resolves `src` (checking `http` prefix or formatting `%s%s` + `%cplatform=%s`).
  - Bundled APK `.big` inventory: only `apk/base_extract/assets/Data/FIFA/icfiles.big` exists locally (plus 1,047 files in `DynamicAssets/android/`). `icfiles_loader` (`0x123c850`) loads `Data/DynamicAssets/android/` + `icfiles.big`; `shader_loader` (`0x2135ad0`) loads `shader*.big` and `shaderboot*.big` via `0x1196998` / `0x217c50c`.
  - **Stage 3 fix implemented (discovery 005):** `server/modules/manifest.py` regenerates `manifest.db` from `server/data/assets/` (measured `length`/`crc`, absolute `src` URLs) and seeds the nine startup names from `.rodata`; `server/main.py` serves `GET /assets/<rel>` with `Content-Length`, suffix content types, `Range` support and a containment check, logging `[ASSET MISS]` for absent bundles. `manifest.db` is git-ignored and rebuilt at startup (`ensure_manifest()`) when missing/corrupt/empty, so the served DB always lists 9 rows.

## 3. Exact Current Blocker & Next Investigation Step
1. **Run the client** and read the new `[ASSET MISS] <name>` lines in the server log (`server/data/captures/` also records the `404`s). Those names are the authoritative startup manifest keys — replace/extend `SEED_RESOURCES` in `server/modules/manifest.py` with them, since the current nine come from `.rodata` string refs, not an observed lookup.
2. **Copy the real bundles** from `base.apk/assets/Data/` into `server/data/assets/` (`shader*.big`, `shaderboot*.big`, `icfiles.big`, `data/attribdbgameplay/gameplayattribdb.big`, `setplaydata/setplaysbig.big`) and restart the server (or run `python3 server/modules/manifest.py`) for measured rows.
3. **If rows exist and the client still raises `Error_Resource_Header`:** disassemble the crc path (`0x556ec44` `crc_file_corrupt`, lookup caller `0x127998c`) to confirm CRC32 is the expected algorithm and whether `length` must match a header field inside the `.big`; also re-check whether `pf_manifest_url_db` / `manifest_paths` must be set for `_loadAllManifests` (`0x5589b68`).
4. Do **not** re-add `/assets` routing or a `manifest.db` skeleton — both exist now (`server/main.py`, generated at startup).
