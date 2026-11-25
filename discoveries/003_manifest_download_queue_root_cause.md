# Discovery 003: Manifest Resource Queue Analysis & 85% ("Kicking Off") Blocker

## 1. Context & Progression
- Client progressed past Stage 1 (HostName INI fetch) and Stage 2 (Protobuf `/g/game/batch` with `w2=1` identity trailer).
- Client presented the in-game update prompt: `"Note : Client requires a Content Update..."`.
- Tapping **CONFIRM DOWNLOAD** triggered `DeviceManifestService._downloadConfirmAccepted` -> `DeviceManifestServieDoubleCheckConfirmFlow`.
- Client downloaded `GET /assets/manifest.db` (`12KB/12KB` green progress bar) and reached 85% (`Splash_85_Percent = "KICKING OFF....."`).
- It then immediately threw `Error_Resource_Header` (`RESOURCE DOWNLOAD ERROR : Please make sure you are connected to the Internet or free up more local storage.`).

## 2. Root Cause Analysis (`libFIFAMobileNeon.so.original`)
- **Lookup Query:**
  - `0x128d8f0`: `SELECT src,length,crc FROM resources WHERE name = ?`
  - Sole caller: `0x1276dc0` inside `ResourceManager` (`0x1276b94`).
- **The Empty Manifest Blocker:**
  - `server/data/responses/manifest.db` had table `resources` created, but `SELECT * FROM resources` returned **0 rows**.
  - `DeviceManifestService` disassembly at `0x556e77c..0x556e790`:
    - `0x556e77c`: `ldr x8, [x20, #0x58]` (loads the list of resources to download).
    - `0x556e788`: `ldr w8, [x8, #0xc]` (reads list length).
    - `0x556e78c`: `cmp w8, #0x0`
    - `0x556e790`: `b.gt 0x556edac` (if `length > 0`, it branches to start the asset downloader).
    - Because the manifest has 0 entries, `length == 0`. The branch is NOT taken, and execution falls through to `0x556e7bc`, triggering `Error_Resource_Header`!
- **Core Startup Resources Found in Binary:**
  - `icfiles.big` (bundled in base APK, 24 KB)
  - `shaderboot.big`, `shaderboot_low.big`, `shaderboot_verylow.big`
  - `shader.big`, `shader_low.big`, `shader_verylow.big`
  - `data/attribdbgameplay/gameplayattribdb.big`
  - `/setplaydata/setplaysbig.big`
- **Method Dispatcher Identified:**
  - `DeviceManifestService._parseStaticResources` mapped at `0x558c4ac` (entry point stub at `0x558bca0`).

## 3. Next Action
- Inspect `0x558bca0` (`_parseStaticResources`) to extract the exact list of resource keys expected at startup.
- Populate `server/data/responses/manifest.db` with the required startup rows so `[x8, #0xc] > 0` and the asset loader can resolve or download the bundles.
