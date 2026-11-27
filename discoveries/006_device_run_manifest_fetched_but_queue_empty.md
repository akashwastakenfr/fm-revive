# Discovery 006: `manifest.db` Is Fetched Twice and Still Yields an Empty Queue

## 1. What the Device Run Showed (Confirmed)
After deploying discovery 005 to `akashwastakenfr/fm-revive@test` and running the client on-device
(Termux, `python3 server/main.py`), the server log and `server/data/captures/` record:

```text
[MANIFEST] rebuilt manifest.db (missing or unreadable): 9 rows (0 measured, 9 seeded)
[BATCH] id=0 endpoints=['game/system/settings']
[BATCH] id=1 endpoints=['game/loginvideo/getCurrentVideo']
[BATCH] id=2 endpoints=['game/telemetry/logNonSessionEvent', 'game/telemetry/logNonSessionEvent', 'game/system/settings']
[BATCH] id=3 endpoints=['game/telemetry/logNonSessionEvent', 'game/system/settings']
[BATCH] id=4 endpoints=['game/system/settings']
[BATCH] id=5 endpoints=['game/system/settings']
[BATCH] id=6 endpoints=['game/system/settings']
```

Captured requests (from `server/data/captures/`):

| time (UTC) | request | notes |
|---|---|---|
| 04:45:34.681 | `POST /g/game/batch` | `game/system/settings` (`id=5`) |
| 04:45:34.717 | `GET /assets/manifest.db` | `Accept: application/xml,image/png`, `User-Agent: ProtoHttp 1.3/DS 15.1.3.0.4 (Android)` |
| 04:45:36.112 | `GET /assets/manifest.db` | identical request, 1.4 s later |
| 04:45:36.128 | `POST /g/game/batch` | `game/system/settings` (`id=6`) |

Facts that follow:

1. The seeded `manifest.db` **is** served (`200`, `application/x.binary`, 12288 bytes, 9 valid rows) and the client **does** fetch it - twice.
2. No `/assets/<bundle>` request follows, so the new `/assets` handler is never exercised and `[ASSET MISS]` never appears.
3. The client then retries `game/system/settings` and raises `Error_Resource_Header` again.
4. Therefore the previous theory ("0 rows -> empty queue") was **incomplete**: a non-empty `resources` table alone is not enough to start the asset downloader at 85%.

## 2. What This Rules Out / Leaves Open
- **Ruled out:** "the manifest is not being delivered" and "the manifest has no rows" - both are fixed and observed on-device.
- **Still unproven:** that the nine `.rodata` names (`icfiles.big`, `shader*.big`, ...) are the `name` keys the client binds. If the startup lookup uses different keys, every `SELECT ... WHERE name = ?` returns `SQLITE_DONE`, the queue stays empty, and the generic error is raised - identical symptom, no asset request.
- **Also possible:** the queue is built before any row lookup, from the config-side static list (`_parseStaticResources` -> `0x5585ae4` reading `manifest_cache_static` / `manifest_paths` / `manifest_cache_static_path_index`), which `default-config.ini` and `server/modules/batch.py` still do not set. In that case rows are irrelevant until those keys exist.

## 3. Instrumentation Added
`server/main.py` now logs every request so a device run is diagnosable from the terminal alone:

- `[REQ] <METHOD> <path>` for every captured (non-asset) request;
- `[ROUTE] <route> -> <template> (<bytes>)` when a `routes.json` template is served, including `/assets/manifest.db`;
- `[ASSET] <name> <bytes>` on a successful bundle download (alongside the existing `[ASSET MISS]`).

Logging is `flush=True`, so lines appear immediately even when output is redirected.

## 4. Next Investigation Step (needs the device)
1. Re-run the client with logging in place and confirm the exact order:

   ```bash
   python3 server/main.py
   ```

2. In a second Termux session, capture the client's own log while reproducing:

   ```bash
   adb logcat -c && adb logcat | grep -iE "manifest|asset|resource|Error_Resource|Splash"
   ```

   The binary logs `Manifest: ` (`0x5587ae4`) and the manifest error strings (`0x556e654` region); that output names the failing step and often the resource key.
3. If logcat shows no key names, disassemble the static-resource parser to recover the expected config format:

   ```bash
   llvm-objdump -d --start-address=0x5585ae4 --stop-address=0x5585eb0 libFIFAMobileNeon.so.original
   ```

   The split characters and the shape of `manifest_cache_static` / `manifest_paths` are in this function; they decide whether config keys must be added before rows can matter.
4. Alternative probe (cheap, no RE): add the missing config keys and watch whether `[ASSET]` requests appear:

   ```ini
   manifest_paths=http://127.0.0.1:8080/assets/
   manifest_cache_static=icfiles.big,shader.big,shader_low.big,shader_verylow.big
   ```

   Treat this as a hypothesis test, not a confirmed format - if the parser expects a different separator the client will simply behave as it does now.
