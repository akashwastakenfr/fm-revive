# `server/data/assets/`

Files here are served by `GET /assets/<relative/path>` (`server/main.py`) and are
the targets of the `src` URLs written into `manifest.db` by
`server/modules/manifest.py`.

Empty on purpose: the real bundles live in the APK on-device and are **not**
committed (see `.gitignore` / the working rules in `readme.md`).

## To restore the startup assets

Copy the bundles out of `base.apk` → `assets/Data/` into this folder, e.g.:

```text
server/data/assets/
├── icfiles.big
├── shader.big
├── shader_low.big
├── shader_verylow.big
├── shaderboot.big
├── shaderboot_low.big
├── shaderboot_verylow.big
├── data/attribdbgameplay/gameplayattribdb.big
└── setplaydata/setplaysbig.big
```

Then regenerate the manifest so `length` and `crc` match the served bytes:

```bash
python3 server/modules/manifest.py
```

Rows the client asks for that are still missing will appear in the server log as
`[ASSET MISS] <name>` (and as a `404` in `server/data/captures/`).
