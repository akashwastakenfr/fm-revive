# Discovery 004: `DeviceManifestService` Field Map, Error Callback Flow & Native `ManifestManager`

## 1. `DeviceManifestService` Architecture (`0x5568000..0x5596000`, Confirmed)
- **Field Offsets (`0x558d200..0x558d740` `__Visit` & `0x558bcf0..0x558beec` `__Mark`):**
  - `+0x08`: `_cacheService`
  - `+0x10`: `_paths`
  - `+0x18`: `_platform`
  - `+0x28`: `_resourceMap`
  - `+0x30`: `_loadUrlMap`
  - `+0x38`: `_daoDisposeLog`
  - `+0x48`: `_suffixes`
  - `+0x50`: `_manifestInitSuccess`
  - `+0x58`: `_manifestLoadOp`
  - `+0x60`: `_assetErrorPublisher`
  - `+0x68`: `_staticResources`
- **Correction to Discovery 003:** `0x556e654..0x556ef80` is the **manifest/asset error handler** (entered via `_onAssetError` `0x5572104 -> 0x556e654` or closure `0x556e49c` bound at `0x556e260` / `0x558a9e0`), not the download queue launcher. At `0x556e77c..0x556e790`, it checks whether `_manifestLoadOp` (`[x20, #0x58]->[+0x10]`) has remaining entries; when `0`, it displays `Error_Resource_Header`.
- **`_parseStaticResources` (`0x558bca0..0x558bcdc`):** Wrapper around `0x5585ae4`, which parses `manifest_cache_static` / `manifest_paths` / `manifest_cache_static_path_index` (split into >=3 fields). (`0x558bf3c..0x558c5d0` is `DeviceManifestService_obj::__Field`, which dispatches `_parseStaticResources` to `0x558bca0`.)
- **Config Keys Read (`0x55688a0..0x5568e50`, `0x5586064..0x5586114`):** `manifest_paths`, `pf_manifest_url_db`, `pf_manifest_url_zip_db`, `pf_manifest_url_xml`, `manifest_crc`, `pf_config_assets_manifest_url_db`, `pf_config_assets_manifest_url_xml`, `optools_manifest_url_db`, `optools_manifest_url_xml`, `optools_manifest_db_crc`, `manifest_cache_static`. Currently `default-config.ini` and `batch.py` only set `pf_config_assets_manifest_url_db` / `_xml`.
- **URL Resolution (`0x558acb0..0x558b060`):** `_getUrlForName` checks `src` for `http://`, `https://`, or `file://`; if relative, it indexes `manifest_paths[pathIndex]`.

## 2. Native `ManifestManager` & Bundled `.big` Loaders (Confirmed)
- `MaddenSocial::ManifestManager` (`0x1275084..0x1275680`) manages `currManifest.txt` (`manifest`), `configAssetsManifest.txt` (`configAssetsManifest`), and `increManifest.txt` (`incrementalManifest`).
- `0x128c300..0x128c6b8` downloads/opens plain `manifest.db`, rekeys in-place (`aes256:mcryan`), and prepares `SELECT src,length,crc FROM resources WHERE name = ?`.
- `0x1276b94` wraps `0x128d8f0` (called at `0x1277110`, `0x12773c0`, `0x1277668`, `0x12777d4`, `0x1277808`, `0x127998c`). `0x127761c` checks `http` prefix or formats `%s%s` + `%cplatform=%s`.
- Only `apk/base_extract/assets/Data/FIFA/icfiles.big` exists as a `.big` inside the APK (plus 1,047 files in `DynamicAssets/android/`). `0x123c850` loads `Data/DynamicAssets/android/` + `icfiles.big`; `0x2135ad0` references `shader*.big` and `shaderboot*.big` via `0x1196998` / `0x217c50c`.
- Live captures confirm zero HTTP requests occur between `GET /assets/manifest.db` and `Error_Resource_Header`.

## 3. Analysis Scripts & Dumps Added (`source/scripts/` & `source/dumps/manifest/`)
- **Scripts (`source/scripts/`):**
  - `dump_manifest_refs.py`: Disassembles `0x558bca0..0x558c600`, `0x556e680..0x556ef80`, `0x1276b90..0x1276f00`, `0x128d8f0..0x128dae0` and resolves string/call refs (`summary.txt`).
  - `scan_manifest_svc.py`: Disassembles `DeviceManifestService` (`0x5568000..0x5596000`) and filters asset/manifest string refs (`scan_out.txt`).
  - `trace_manifest_flow.py` / `trace_manifest_flow2.py` / `trace_manifest_flow3.py` / `trace_manifest_flow4.py` / `trace_manifest_flow5.py`: Traces `_parseStaticResources`, `manifest_init_keys`, `src_url_resolver`, `_loadAllManifests`, `_onManifestLoadComplete`, `__Visit` field offsets, `.text` BL callers, and native `ManifestManager` (`trace_out.txt`..`trace5.txt`).
  - `find_startup_resources.py` / `inspect_85pct.py` / `check_manifest_op.py` / `check_lookup_flow.py`: Maps `DeviceManifestService` method addresses, `.text` xrefs to `icfiles.big`/`shader*.big`, `icfiles_loader`, `shader_loader`, `_manifestLoadOp` lifecycle, and `loadAsset`/`resolveAsset`/`RM_manifest_db_init` (`startup_refs.txt`, `inspect85.txt`, `manifest_op.txt`, `lookup_flow.txt`).
- **Dumps (`source/dumps/manifest/`):**
  - Disassembly: `parse_static_resources.asm`, `manifest_queue_dl.asm`, `resource_mgr_lookup.asm`, `sqlite_row_reader.asm`, `device_manifest_service.asm`, `resource_mgr_full.asm`.
  - Reports: `local_big_files.txt`, `summary.txt`, `scan_out.txt`, `trace_out.txt`, `trace2.txt`..`trace5.txt`, `startup_refs.txt`, `inspect85.txt`, `manifest_op.txt`, `lookup_flow.txt`.

## 4. Unknowns / Immediate Next Steps
- Check `0x128c570..0x128c6b8` (`RM_manifest_db_init`), `0x55688a0..0x5568e10`, and `0x217c50c` (`shader_loader`) to isolate whether `Error_Resource_Header` fires due to missing `pf_manifest_url_db`/`manifest_paths` or an empty `resources` table lookup.
- Add `/assets/...` static route handling in `server/main.py` and populate `manifest.db` + missing config keys.
