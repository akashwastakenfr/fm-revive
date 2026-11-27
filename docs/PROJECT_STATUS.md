# Project Status & Phase Checklist

Last updated: 2026-11-25

## Phase Checklist
- [x] **Phase 1 — Archive Extraction & Inventory:** Original `.apkm` (31 files), `base.apk`, `arm64.apk`, `armv7.apk`, `libFIFAMobileNeon.so.original`, and JADX output (`jadx-out/`) extracted and preserved.
- [x] **Phase 2 — Java / Manifest / Synergy Mapping:** Manifest `live` config, Nimble/Synergy startup flow (`SynergyEnvironmentUpdater`), `P4Info.ini`, `base_settings.xml`, and `lang_BOOTSTRAP_EN_US.properties` documented.
- [x] **Phase 3 — Stage 1 Bootstrap Blocker (`Error_HostName_Message`):** Local server connected; INI parser `[default]` requirement discovered (`0x12687f8`); `default-config.ini` verified and accepted by client.
- [x] **Phase 4 — Stage 2 Binary RPC (`/g/game/batch`):** `BatchCollection` / `BatchResponseCollection` / `SystemSettings` reversed; identity trailer `w2=1` and `BatchResponse` field 3 CRC32 checksum implemented.
- [/] **Phase 5 — Stage 3 Content Update & Manifest (`manifest.db`):**
  - [x] Client triggered Content Update and requested `GET /assets/manifest.db`.
  - [x] SQLite3 `manifest.db` served, rekeyed with `aes256:mcryan`, and downloaded (`12KB/12KB`).
  - [x] Splash screen reached 85% (`KICKING OFF.....`).
  - [x] Mapped `DeviceManifestService` fields, `_parseStaticResources` (`0x558bca0 -> 0x5585ae4`), `_loadAllManifests` (`0x5589b68`), `_getUrlForName` (`0x558acb0`), error handler (`0x556e654`), and native `ManifestManager` (`0x1275000..0x128e000`).
  - [x] **Root cause confirmed (discovery 005):** empty `resources` table → manifest load op has 0 entries (`0x556e77c..0x556e790` only takes the download branch when `count > 0`) → `Error_Resource_Header`.
  - [x] `server/modules/manifest.py` regenerates `manifest.db` from `server/data/assets/` (measured `length` + CRC32, absolute `src` URLs) and seeds the nine `.rodata` startup names; DB now has 9 rows and still fits one 12 KB page.
  - [x] `GET /assets/<rel>` serving added to `server/main.py` (containment check, `Range`/`206`, `416`, `[ASSET MISS]` logging); `server/test_server.py` covers `/assets/manifest.db` (22/22 pass).
  - [x] `manifest.db` is now a generated artifact (`.gitignore`) rebuilt at startup by `ensure_manifest()` when missing, corrupt, or empty.
  - [ ] **Active Blocker:** the real startup bundles are not in the repo (APK-local, git-ignored), so seeded rows carry `length=0`/`crc=0`. Next: run the client, collect `[ASSET MISS]` names, copy the `.big` files into `server/data/assets/`, re-run the builder.
- [ ] **Phase 6 — Main Menu & Offline Preservation:** Verify main-menu entry and offline gameplay.
