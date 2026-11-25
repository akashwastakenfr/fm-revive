# FIFA Mobile 23 Revival (`fm-revive`)

Research, reverse-engineering, and independent local server preservation project for **FIFA Mobile 23 Android** (`com.ea.gp.fifamobile`, v18.1.03, versionCode `40214`).

> **For AIs starting with 0 context:** Read `AI_HANDOVER.md` first, then `docs/PROTOCOL_SPEC.md`, `docs/BINARY_MAP.md`, and `discoveries/`.

## Current Status (2026-11-25)
- **Stage 1 (Bootstrap Config Fetch):** **RESOLVED.** Client connects to `http://127.0.0.1:8080`, fetches `/config/Android/18.1.03/config.ini`, passes `_config_verifyFifaMobileHostNameFetch`, and clears `Error_HostName_Message`.
- **Stage 2 (`/g/game/batch` Binary Protobuf RPC):** **ACTIVE BLOCKER.** Server decodes `POST /g/game/batch` via `server/modules/batch.py` (`game/system/settings`, `game/telemetry/logNonSessionEvent`) and returns `status=200` `BatchResponseCollection` protobufs, but the client retries `game/system/settings` (`id=1..6`) until `Error_RpcTimeout` (`SERVER CONNECTION ISSUE`).
- **Stage 3 (User / Content / Main Menu / Offline Gameplay):** Not yet reached.

## Repository Structure
```text
.
├── README.md                  # Project overview, repo map, and rules
├── AI_HANDOVER.md             # Zero-context AI onboarding & exact next steps
├── .gitignore                 # Excludes APKs, .so binaries, jadx-out/, logs/, raw captures/
├── discoveries/               # Chronological breakthroughs & root causes
│   ├── 001_config_ini_default_section.md
│   └── 002_batch_rpc_and_byte_decoder.md
├── docs/
│   ├── PROJECT_STATUS.md      # Phase checklist & milestones
│   ├── PROTOCOL_SPEC.md       # Stage 1 INI & Stage 2 protobuf wire specs
│   ├── BINARY_MAP.md          # ELF addresses (libFIFAMobileNeon.so.original) & Java classes
│   └── archive/               # Historical project logs
├── server/                    # Independent local Python HTTP & protobuf server (127.0.0.1:8080)
│   ├── main.py                # HTTP router, capture logger, /g/game/batch hook
│   ├── modules/batch.py       # Pure-Python protobuf wire codec & RPC responder
│   ├── config/routes.json     # Static/JSON/INI route mappings
│   ├── data/responses/        # Response templates (default-config.ini, JSON fixtures)
│   └── test_server.py         # Synthetic endpoint tests
└── source/
    ├── scripts/               # Analysis tools (find_config_refs.py)
    └── dumps/                 # Categorized disassembly, rodata, xref, and JADX dumps
        ├── config_service/
        ├── batch_rpc/
        ├── synergy_java/
        └── misc/
```

*(Original APKs, `libFIFAMobileNeon.so.original`, `jadx-out/`, `logs/`, and `server/data/captures/` live locally in Termux and are ignored by Git.)*

## Working Rules
- **Platform:** Android + Termux + ADB + Python 3 + `llvm-objdump` / `llvm-readelf` + JADX 1.5.7.
- **Native binary to inspect:** Always use **`libFIFAMobileNeon.so.original`** (ARM64 ELF64, Build ID `5b68aef6cae0402e472aaae084aaa1367661b788`). Do not use `libFIFAMobileNeon.so` in root (its section table causes `section table goes past the end of file`).
- **Evidence rule:** Always separate Confirmed facts from Hypotheses and Unknowns.
- **Logging rule:** Log every breakthrough in `discoveries/` and update `AI_HANDOVER.md` + `docs/PROJECT_STATUS.md` before pushing.

## Run Local Server
```bash
python3 server/main.py
```
Listens on `http://127.0.0.1:8080`.