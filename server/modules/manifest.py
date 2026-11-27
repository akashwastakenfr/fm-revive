"""manifest.db builder for Stage 3 (asset manifest).

The client downloads ``GET /assets/manifest.db``, rekeys it in-place with
``aes256:mcryan`` and runs ``SELECT src,length,crc FROM resources WHERE name = ?``.
An empty ``resources`` table makes the manifest load op complete with a zero
length queue, which falls through to ``Error_Resource_Header`` at 85%
(``KICKING OFF.....``) -- see ``discoveries/003`` and ``discoveries/005``.

This module regenerates ``server/data/responses/manifest.db`` so every file
present in ``server/data/assets/`` gets a row whose ``length`` and ``crc`` match
the bytes the server actually serves from ``/assets/<name>``.

Usage (from the repo root or from ``server/``):

    python3 server/modules/manifest.py
    python3 server/modules/manifest.py --assets server/data/assets --no-seed

Drop the real ``.big`` bundles (``shader*.big``, ``shaderboot*.big``,
``data/attribdbgameplay/gameplayattribdb.big``, ...) into
``server/data/assets/`` and re-run to get measured rows.
"""

import argparse
import sqlite3
import zlib
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB = SERVER_DIR / "data" / "responses" / "manifest.db"
DEFAULT_ASSETS = SERVER_DIR / "data" / "assets"
DEFAULT_BASE_URL = "http://127.0.0.1:8080/assets/"

SCHEMA = (
    "CREATE TABLE IF NOT EXISTS resources ("
    "name TEXT PRIMARY KEY, src TEXT, length INTEGER, crc INTEGER)"
)

# Startup resources confirmed in .rodata of libFIFAMobileNeon.so.original
# (discoveries/003). Seeded with length=0/crc=0 when the bundle is absent so
# the client's manifest queue is non-empty and the requested names show up in
# the server capture log instead of failing silently.
SEED_RESOURCES = (
    "icfiles.big",
    "shaderboot.big",
    "shaderboot_low.big",
    "shaderboot_verylow.big",
    "shader.big",
    "shader_low.big",
    "shader_verylow.big",
    "data/attribdbgameplay/gameplayattribdb.big",
    "setplaydata/setplaysbig.big",
)


def crc32_of(path):
    """CRC32 of a file's bytes, chunked so large .big files stay cheap."""
    crc = 0
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            crc = zlib.crc32(chunk, crc)
    return crc & 0xFFFFFFFF


def collect_rows(asset_dir, base_url):
    """Map name -> (src, length, crc) for every file under asset_dir."""
    asset_dir = Path(asset_dir)
    rows = {}
    if not asset_dir.is_dir():
        return rows

    for path in sorted(asset_dir.rglob("*")):
        if not path.is_file():
            continue
        name = path.relative_to(asset_dir).as_posix()
        if name.endswith(".md") or name.startswith("."):
            continue
        rows[name] = (base_url + name, path.stat().st_size, crc32_of(path))
    return rows


def build(db_path=DEFAULT_DB, asset_dir=DEFAULT_ASSETS, base_url=DEFAULT_BASE_URL, seed=True):
    """Rewrite db_path from asset_dir; returns (rows, measured, seeded)."""
    files = collect_rows(asset_dir, base_url)

    rows = dict(files)
    seeded = 0
    if seed:
        for name in SEED_RESOURCES:
            if name not in rows:
                rows[name] = (base_url + name, 0, 0)
                seeded += 1

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = db_path.with_name(db_path.name + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()

    connection = sqlite3.connect(tmp_path)
    try:
        connection.execute(SCHEMA)
        connection.executemany(
            "INSERT OR REPLACE INTO resources (name, src, length, crc) VALUES (?, ?, ?, ?)",
            [(name, src, length, crc) for name, (src, length, crc) in sorted(rows.items())],
        )
        connection.commit()
    finally:
        connection.close()

    tmp_path.replace(db_path)
    return len(rows), len(files), seeded


def main():
    parser = argparse.ArgumentParser(description="Rebuild manifest.db resources rows.")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="output SQLite path")
    parser.add_argument("--assets", default=str(DEFAULT_ASSETS), help="directory of served assets")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="url prefix written into src")
    parser.add_argument("--no-seed", action="store_true", help="only emit rows for files that exist")
    args = parser.parse_args()

    total, measured, seeded = build(
        db_path=args.db,
        asset_dir=args.assets,
        base_url=args.base_url,
        seed=not args.no_seed,
    )
    print(f"manifest.db: {total} rows ({measured} measured, {seeded} seeded) -> {args.db}")
    print(f"asset dir:   {args.assets} (base {args.base_url})")
    if measured == 0:
        print("note: no asset files found; seeded rows have length=0/crc=0 and will 404 until files land.")


if __name__ == "__main__":
    main()
