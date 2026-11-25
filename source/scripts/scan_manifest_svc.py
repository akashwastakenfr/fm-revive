import re, struct, subprocess
from pathlib import Path

SO = "libFIFAMobileNeon.so.original"
OUT = Path("source/dumps/manifest")
FULL_ASM = OUT / "device_manifest_service.asm"

if not FULL_ASM.exists():
    res = subprocess.run(
        ["llvm-objdump", "-d", "--start-address=0x5568000", "--stop-address=0x5596000", SO],
        capture_output=True, text=True, check=True
    )
    FULL_ASM.write_text(res.stdout)

data = Path(SO).read_bytes()
e_phoff = struct.unpack_from("<Q", data, 32)[0]
e_phentsize, e_phnum = struct.unpack_from("<HH", data, 54)
segs = [
    (pv, pv + pf, po)
    for i in range(e_phnum)
    for pt, _, po, pv, _, pf, _, _ in [struct.unpack_from("<IIQQQQQQ", data, e_phoff + i * e_phentsize)]
    if pt == 1
]

def va2off(va):
    for s, e, o in segs:
        if s <= va < e:
            return o + (va - s)
    return None

def read_str(va):
    off = va2off(va)
    if off is None: return None
    for d in (0, 8):
        c = data[off+d:off+d+120].split(b"\x00", 1)[0]
        if len(c) >= 3 and all(32 <= b < 127 for b in c):
            return c.decode("ascii")
    return None

def show_slice(path, lo, hi):
    print(f"=== {path.name} {hex(lo)}..{hex(hi)} ===")
    for l in path.read_text().splitlines():
        m = re.match(r'^\s*([0-9a-f]+):', l)
        if m and lo <= int(m.group(1), 16) <= hi:
            print(l)

show_slice(OUT / "manifest_queue_dl.asm", 0x556e740, 0x556e7d0)
show_slice(OUT / "manifest_queue_dl.asm", 0x556ed30, 0x556ee50)
show_slice(OUT / "parse_static_resources.asm", 0x558c480, 0x558c5d0)

print("=== asset/manifest strings in 0x5568000..0x5596000 ===")
kw = re.compile(r'big|xml|shader|manifest|resource|asset|http|crc|zip|db|icfiles|setplay|attrib|url|cache|static', re.I)
pages = {}
for l in FULL_ASM.read_text().splitlines():
    m = re.search(r'^\s*([0-9a-f]+):.*\badrp\s+(x\d+),\s*#?0x([0-9a-fA-F]+)', l)
    if m:
        pages[m.group(2)] = int(m.group(3), 16)
        continue
    m = re.search(r'^\s*([0-9a-f]+):.*\badd\s+(x\d+),\s*(x\d+),\s*#(0x[0-9a-fA-F]+|\d+)', l)
    if m and m.group(3) in pages:
        s = read_str(pages[m.group(3)] + int(m.group(4), 0))
        if s and kw.search(s):
            print(f"  0x{m.group(1)}: {s!r}")
