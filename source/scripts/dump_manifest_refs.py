import re, struct, subprocess
from pathlib import Path

SO = "libFIFAMobileNeon.so.original"
OUT = Path("source/dumps/manifest")
RANGES = [
    ("parse_static_resources", 0x558bca0, 0x558c600),
    ("manifest_queue_dl",      0x556e680, 0x556ef80),
    ("resource_mgr_lookup",    0x1276b90, 0x1276f00),
    ("sqlite_row_reader",      0x128d8f0, 0x128dae0),
]

data = Path(SO).read_bytes()
e_phoff = struct.unpack_from("<Q", data, 32)[0]
e_phentsize, e_phnum = struct.unpack_from("<HH", data, 54)
segs = []
for i in range(e_phnum):
    p_type, _, p_offset, p_vaddr, _, p_filesz, p_memsz, _ = struct.unpack_from("<IIQQQQQQ", data, e_phoff + i * e_phentsize)
    if p_type == 1:
        segs.append((p_vaddr, p_vaddr + p_filesz, p_offset))

def va2off(va):
    for s, e, o in segs:
        if s <= va < e:
            return o + (va - s)
    return None

def read_str(va):
    off = va2off(va)
    if off is None: return None
    # Try direct C-string, then +8 HXCPP literal header
    for delta in (0, 8):
        chunk = data[off+delta:off+delta+96].split(b"\x00", 1)[0]
        if len(chunk) >= 3 and all(32 <= b < 127 for b in chunk):
            s = chunk.decode("ascii")
            return s if delta == 0 else f"[hx+8] {s}"
    return None

summary = []
for name, start, stop in RANGES:
    asm_path = OUT / f"{name}.asm"
    if not asm_path.exists():
        res = subprocess.run(
            ["llvm-objdump", "-d", f"--start-address={hex(start)}", f"--stop-address={hex(stop)}", SO],
            capture_output=True, text=True, check=True
        )
        asm_path.write_text(res.stdout)
    lines = asm_path.read_text().splitlines()
    summary.append(f"=== {name} ({hex(start)}..{hex(stop)}, {len(lines)} lines) ===")
    pages = {}
    for line in lines:
        m = re.search(r'^\s*([0-9a-f]+):.*\badrp\s+(x\d+),\s*#?0x([0-9a-fA-F]+)', line)
        if m:
            pages[m.group(2)] = int(m.group(3), 16)
            continue
        m = re.search(r'^\s*([0-9a-f]+):.*\badd\s+(x\d+),\s*(x\d+),\s*#(0x[0-9a-fA-F]+|\d+)', line)
        if m and m.group(3) in pages:
            va = pages[m.group(3)] + int(m.group(4), 0)
            s = read_str(va)
            if s: summary.append(f"  0x{m.group(1)}: {hex(va)} -> {s!r}")
        m = re.search(r'^\s*([0-9a-f]+):.*\bldr\s+([xw]\d+),\s*\[(x\d+)(?:,\s*#(0x[0-9a-fA-F]+|\d+))?\]', line)
        if m and m.group(3) in pages:
            imm = int(m.group(4), 0) if m.group(4) else 0
            va = pages[m.group(3)] + imm
            off = va2off(va)
            val = struct.unpack_from("<Q", data, off)[0] if off is not None else 0
            s = read_str(val) or read_str(va)
            summary.append(f"  0x{m.group(1)}: [{hex(va)}] (val={hex(val)}) -> {s!r}")
        m = re.search(r'^\s*([0-9a-f]+):.*\bbl\s+#?0x([0-9a-fA-F]+)', line)
        if m:
            summary.append(f"  0x{m.group(1)}: bl 0x{m.group(2)}")

out_txt = "\n".join(summary)
(OUT / "summary.txt").write_text(out_txt)
print(out_txt)
