# Project Status & Phase Checklist

Last updated: 2026-11-25

## Phase Checklist
- [x] **Phase 1 — Archive Extraction & Inventory:** Original `.apkm` (31 files), `base.apk`, `arm64.apk`, `armv7.apk`, `libFIFAMobileNeon.so.original`, and JADX output (`jadx-out/`) extracted and preserved.
- [x] **Phase 2 — Java / Manifest / Synergy Mapping:** Manifest `live` config, Nimble/Synergy startup flow (`SynergyEnvironmentUpdater`), `P4Info.ini`, `base_settings.xml`, and `lang_BOOTSTRAP_EN_US.properties` documented.
- [x] **Phase 3 — Stage 1 Bootstrap Blocker (`Error_HostName_Message`):** Local server connected; INI parser `[default]` requirement discovered (`0x12687f8`); `default-config.ini` verified and accepted by client.
- [x] **Phase 4 — Stage 2 Binary RPC (`/g/game/batch`):** `BatchCollection` / `BatchResponseCollection` / `SystemSettings` reversed; identity trailer `w2=1` implemented. System settings and login video RPCs now complete with status 200.
- [/] **Phase 5 — Stage 3 Content Update & Manifest (`manifest.db`):** 
  - [x] Client triggered Content Update and requested `GET /assets/manifest.db`.
  - [x] SQLite3 `manifest.db` served, rekeyed with `aes256:mcryan`, and downloaded (`12KB/12KB`).
  - [x] Splash screen reached 85% (`KICKING OFF.....`).
  - [ ] **Active Blocker:** `resources` table in `manifest.db` has 0 rows; `DeviceManifestService` checks `length > 0` at `0x556e78c`, failing into `Error_Resource_Header` (`RESOURCE DOWNLOAD ERROR`). Reversing `_parseStaticResources` (`0x558bca0`) to populate required startup rows.
- [ ] **Phase 6 — Main Menu & Offline Preservation:** Verify main-menu entry and offline gameplay.
