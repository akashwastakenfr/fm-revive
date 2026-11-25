# Project Status & Phase Checklist

Last updated: 2026-11-25

## Phase Checklist
- [x] **Phase 1 — Archive Extraction & Inventory:** Original `.apkm` (31 files), `base.apk`, `arm64.apk`, `armv7.apk`, `libFIFAMobileNeon.so.original`, and JADX output (`jadx-out/`) extracted and preserved.
- [x] **Phase 2 — Java / Manifest / Synergy Mapping:** Manifest `live` config, Nimble/Synergy startup flow (`SynergyEnvironmentUpdater`), `P4Info.ini`, `base_settings.xml`, and `lang_BOOTSTRAP_EN_US.properties` documented.
- [x] **Phase 3 — Stage 1 Bootstrap Blocker (`Error_HostName_Message`):** Local server connected; INI parser `[default]` requirement discovered (`0x12687f8`); `default-config.ini` verified and accepted by client.
- [/] **Phase 4 — Stage 2 Binary RPC (`/g/game/batch`):** `BatchCollection` / `BatchResponseCollection` / `SystemSettings` and `0x4e69764` byte decoder reversed; `server/modules/batch.py` wired into `server/main.py`. **Open:** resolve why `game/system/settings` retries (`id=1..6`) until `Error_RpcTimeout`.
- [ ] **Phase 5 — Stage 2/3 Remaining RPCs & ContentService:** Implement responses for `game/telemetry/*`, `system/getServerTime`, `system/session/create`, `content/init`, `user/login`, `user/load`, etc. as triggered.
- [ ] **Phase 6 — Main Menu & Offline Preservation:** Verify main-menu entry and offline gameplay.