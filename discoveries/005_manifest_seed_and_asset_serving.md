# Discovery 005: Seeded `manifest.db` Rows + `/assets` Serving

## 1. Problem Restated (Confirmed)
- Client reaches 85% (`KICKING OFF.....`), downloads `GET /assets/manifest.db` (`12KB/12KB`), then shows `Error_Resource_Header` (`RESOURCE DOWNLOAD ERROR : ...`).
- No `.xml` or `.big` request is ever made between the `manifest.db` download and the error.
- `server/data/responses/manifest.db` contained the correct schema but **0 rows**:
  `CREATE TABLE resources (name TEXT PRIMARY KEY, src TEXT, length INTEGER, crc INTEGER)`.
- Discovery 003/004 explain why that is fatal: `0x556e77c..0x556e790` loads `_manifestLoadOp` (`[x20,#0x58]`), reads its entry count (`[x8,#0xc]`), and only takes the download branch when `count > 0` (`b.gt 0x556edac`). With an empty `resources` table the manifest resolves nothing, the queue stays at 0, and the generic `Error_Resource_Header` dialog is raised.
- Secondary gap: `server/main.py` had **no** `/assets/<file>` handler, so even with rows the client had nowhere to fetch bundles from (`_getUrlForName` at `0x558acb0` accepts absolute `http://`/`https://`/`file://` `src` or resolves relative names through `manifest_paths`).

## 2. Changes Implemented
### `server/modules/manifest.py` (new)
- Regenerates `server/data/responses/manifest.db` from files in `server/data/assets/`.
- For each file: `name` = POSIX relative path, `src` = `http://127.0.0.1:8080/assets/<name>` (absolute, so `_getUrlForName`'s `http://` branch applies and `manifest_paths` is not required), `length` = file size in bytes, `crc` = zlib CRC32.
- Seeds the startup resource names confirmed in `.rodata` (discovery 003) when the bundle is absent, with `length=0, crc=0`, so the queue is never empty again:
  `icfiles.big`, `shaderboot.big`, `shaderboot_low.big`, `shaderboot_verylow.big`, `shader.big`, `shader_low.big`, `shader_verylow.big`, `data/attribdbgameplay/gameplayattribdb.big`, `setplaydata/setplaysbig.big`.
- Usage: `python3 server/modules/manifest.py` (options `--db`, `--assets`, `--base-url`, `--no-seed`).

### `manifest.db` is now a generated artifact
- `server/data/responses/manifest.db` is listed in `.gitignore` and rebuilt by the server at startup via `ensure_manifest()` (`server/main.py`) whenever it is missing, unreadable, or has 0 rows. Starting the server is therefore enough to get a consistent manifest; `python3 server/modules/manifest.py` remains available to rebuild it by hand.
- Rationale: a committed binary drifts from whatever `server/data/assets/` holds, and a stale/empty/corrupt DB reproduces the exact 85% failure this fix targets.

### `server/main.py`
- New `GET /assets/<relative path>` handler with:
  - strict path containment (`resolve()` + `relative_to(ASSET_DIR)`), so `..` traversal cannot escape `server/data/assets/`;
  - `Content-Length` and `Content-Type` by suffix (`.big` / `.xml` / `.db` / `.zip`);
  - HTTP `Range: bytes=a-b` support (`206` + `Content-Range`, `416` past EOF);
  - `[ASSET MISS] <name>` on the server log and a `404` JSON body for absent bundles.
- `/assets/manifest.db` still resolves through `routes.json` (`application/x.binary`), so its behaviour is unchanged.
- Asset requests are served before the capture writer, so large bundle downloads do not create one JSON capture per request.

### `server/data/assets/README.md` (new)
- Explains that the folder is intentionally empty (real bundles are APK-local and git-ignored) and lists the files to drop in, plus the command to re-measure rows.

### `server/test_server.py`
- Added `GET /assets/manifest.db` to the suite; binary (`application/x.binary`) responses are now checked for the `SQLite format 3\0` header instead of being UTF-8 decoded (the old decode crashed on the database bytes).

## 3. Verification (Local, No Device)
With a synthetic 26-byte `server/data/assets/shader.big`:

| Check | Result |
|---|---|
| `python3 server/modules/manifest.py` | `9 rows (1 measured, 8 seeded)` |
| `GET /assets/manifest.db` | `200`, `application/x.binary`, `12288` bytes, `resources` = 9 rows, `shader.big -> src=http://127.0.0.1:8080/assets/shader.big, length=26, crc=3204942770` |
| `GET /assets/shader.big` | `200`, `application/octet-stream`, 26 bytes |
| `GET /assets/shader.big` + `Range: bytes=0-3` | `206`, 4 bytes (`0 1 2 3`), `Content-Range` correct |
| `GET /assets/does-not-exist.big` | `404` + `[ASSET MISS] does-not-exist.big` |
| `GET /assets/../../main.py` | rejected by containment check (falls through to `202 captured`, no file served) |
| `python3 server/test_server.py` | 22/22 pass (after the binary-body fix) |
| delete `manifest.db`, start server | rebuilt (`[MANIFEST] rebuilt manifest.db (missing or unreadable)...`), served DB has 9 rows |
| overwrite `manifest.db` with garbage, start server | rebuilt (`0 rows`/unreadable path), served DB has 9 rows |

`manifest.db` stays on a single 12 KB page after seeding, so the client's `12KB/12KB` download size is unchanged.

## 4. Confirmed vs Hypothesis vs Unknown
- **Confirmed:** `/assets` serving, Range handling, containment, seeded DB contents, 12 KB page size, test suite, startup rebuild on missing/corrupt/empty DB.
- **Hypothesis:** CRC32 (zlib) is the algorithm the client validates `crc` against (`crc_file_corrupt` at `0x556ec44`); it is the only CRC in the codebase (`0x57015c0`), but the file-crc path itself is not yet disassembled.
- **Unknown:** the exact resource **names** the client queries at startup. The nine seeded names come from `.rodata` string refs, not from an observed lookup.
- **Unknown:** whether the client treats `length=0` as "skip download" or as an immediate failure; this is the first thing to watch when the device is retried.

## 5. Next Steps
1. Run the client: anything queried but not present now appears as `[ASSET MISS] <name>` in the server log (and as `404` in `server/data/captures/`). That list is the real startup manifest key set — replace/extend `SEED_RESOURCES` with it.
2. Copy the real bundles from `base.apk/assets/Data/` into `server/data/assets/` (shader/shaderboot family, `icfiles.big`, `data/attribdbgameplay/gameplayattribdb.big`, `setplaydata/setplaysbig.big`) and re-run the builder for measured `length`/`crc`.
3. If the client still errors with rows present, disassemble the crc check (`0x556ec44` `crc_file_corrupt`, `0x127998c` lookup caller) to confirm the algorithm and whether `length` must match a header field inside the `.big`.
