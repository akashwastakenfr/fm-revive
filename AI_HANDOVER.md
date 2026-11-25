# AI Handover & Zero-Context Onboarding

Read this file completely before suggesting commands, code edits, or diagnoses.

## 1. Strict Rules
1. Never confuse **Confirmed** facts with **Hypotheses** or **Unknowns**.
2. Do not repeat completed work (APKM extraction, JADX decompilation, Stage 1 `config.ini` diagnosis, and Stage 2 byte-decoder/checksum reversing are DONE).
3. Keep Termux commands short (user works on an Android phone) and save large outputs to `source/dumps/` or `logs/`.
4. Always run `llvm-objdump` / `llvm-readelf` on `libFIFAMobileNeon.so.original`, NOT `libFIFAMobileNeon.so`.
5. Document every breakthrough in `discoveries/`.
6. Never commit `.apk`, `.apkm`, `.so*`, `jadx-out/`, `logs/`, or `server/data/captures/`.

## 2. Current State of Progress (Confirmed)
- **Stage 1 (HostName Fetch):** RESOLVED. Client connects to `http://127.0.0.1:8080/config/Android/18.1.03/config.ini`. INI section must be `[default]`.
- **Stage 2 (Batch Protobuf):** RESOLVED. Client sends `POST /g/game/batch`. Response uses `BatchResponseCollection` groups (wire type 3/4), trailer `b"\x00"*5 + b"\x00\x00\x00\x01" + b"\x00"*5` (`w2=1`), and `BatchResponse` field 3 CRC32 checksum with `BATCH_CHECKSUM_SECRET = 22ecd02d437fdc88`.
- **Stage 3 (Asset Download & Manifest):**
  - Client receives `pf_config_assets_manifest_url_db` / `_xml`, requests `GET /assets/manifest.db`, opens it with `sqlite3_open_v2`, rekeys in-place with `aes256:mcryan` (`sqlite3_rekey_v2`), and reaches 85% (`KICKING OFF.....`).
  - Client then shows `Error_Resource_Header` (`RESOURCE DOWNLOAD ERROR`) without requesting any `.xml` or `.big` files over HTTP.
  - `server/data/responses/manifest.db` has table `resources(name TEXT PRIMARY KEY, src TEXT, length INTEGER, crc INTEGER)` with **0 rows**.
  - `DeviceManifestService` (`0x5568000..0x5596000`) field layout confirmed via `__Visit` (`0x558d200..0x558d740`): `+0x58` is `_manifestLoadOp`, `+0x60` is `_assetErrorPublisher`, `+0x68` is `_staticResources`.
  - `0x556e654` (`Error_Resource_Header`) is the error callback (`_onAssetError` at `0x5572104 -> 0x556e654`; closure `0x556e49c` bound at `0x556e260` / `0x558a9e0`). At `0x556e77c..0x556e790`, it checks `_manifestLoadOp` (`[x20, #0x58]`).
  - `_parseStaticResources` (`0x558bca0..0x558bcdc`) is a 16-instruction wrapper calling `0x5585ae4`, which parses `manifest_cache_static` / `manifest_paths` / `manifest_cache_static_path_index`.
  - `_loadAllManifests` (`0x5589b68 -> 0x5585eb8`) checks `pf_manifest_url_*`, `pf_config_assets_manifest_url_*`, and `optools_manifest_url_*`. Currently `default-config.ini` and `server/modules/batch.py` only set `pf_config_assets_manifest_url_*` (not `pf_manifest_url_db` or `manifest_paths`).
  - Native `MaddenSocial::ManifestManager` (`0x1275000..0x128e000`) wraps `SELECT src,length,crc FROM resources WHERE name = ?` (`0x128d8f0`) via `0x1276b94`, and `0x127761c` resolves `src` (checking `http` prefix or formatting `%s%s` + `%cplatform=%s`).
  - Bundled APK `.big` inventory: only `apk/base_extract/assets/Data/FIFA/icfiles.big` exists locally (plus 1,047 files in `DynamicAssets/android/`). `icfiles_loader` (`0x123c850`) loads `Data/DynamicAssets/android/` + `icfiles.big`; `shader_loader` (`0x2135ad0`) loads `shader*.big` and `shaderboot*.big` via `0x1196998` / `0x217c50c`.

## 3. Exact Current Blocker & Next Investigation Step
1. Confirm why `0x556e654` (`Error_Resource_Header`) fires right after `GET /assets/manifest.db`:
   - Check `0x128c570..0x128c6b8` (`RM_manifest_db_init`) and `0x55688a0..0x5568e10` (`manifest_init_keys`) to see whether missing `pf_manifest_url_db` / `manifest_paths` or an empty `resources` lookup fails first.
   - Check `0x217c50c` (`shader_loader`) and `0x12770e0..0x1277820` callers to identify the exact startup `name` keys queried in `manifest.db` and expected `src`/archive format.
2. Add `/assets/...` prefix routing in `server/main.py` and populate `server/data/responses/manifest.db` + missing config keys (`pf_manifest_url_db`, `manifest_paths`).
