import re, struct, subprocess
from pathlib import Path

SO = "libFIFAMobileNeon.so.original"
OUT = Path("source/dumps/manifest")
RM_ASM = OUT / "resource_mgr_full.asm"
if not RM_ASM.exists():
    RM_ASM.write_text(subprocess.run(
        ["llvm-objdump", "-d", "--start-address=0x1275000", "--stop-address=0x128f000", SO],
        capture_output=True, text=True, check=True
    ).stdout)

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
        if s <= va < e: return o + (va - s)
    return None

def read_str(va):
    off = va2off(va)
    if off is None: return None
    for d in (0, 8):
        c = data[off+d:off+d+120].split(b"\x00", 1)[0]
        if len(c) >= 3 and all(32 <= b < 127 for b in c):
            return c.decode("ascii")
    return None

def scan_asm(title, lines, lo, hi, show_all=False):
    print(f"\n=== {title} ({hex(lo)}..{hex(hi)}) ===")
    pages = {}
    for l in lines:
        m = re.match(r'^\s*([0-9a-f]+):', l)
        if not m: continue
        addr = int(m.group(1), 16)
        if not (lo <= addr <= hi): continue
        note = ""
        m_a = re.search(r'\badrp\s+(x\d+),\s*#?0x([0-9a-fA-F]+)', l)
        if m_a: pages[m_a.group(1)] = int(m_a.group(2), 16)
        m_add = re.search(r'\badd\s+(x\d+),\s*(x\d+),\s*#(0x[0-9a-fA-F]+|\d+)', l)
        if m_add and m_add.group(2) in pages:
            s = read_str(pages[m_add.group(2)] + int(m_add.group(3), 0))
            if s: note = f"  ; {s!r}"
        if show_all or note or re.search(r'\b(bl|b\.\w+|cbz|cbnz|tbz|tbnz|cmp|ret)\b', l):
            clean = re.sub(r'\s+<[^>]+>', '', l.strip())
            print(f"  {clean}{note}")

DMS = (OUT / "device_manifest_service.asm").read_text().splitlines()
RM  = RM_ASM.read_text().splitlines()

scan_asm("manifest_loader_dispatch", DMS, 0x5585f00, 0x5587200)
scan_asm("on_manifest_load_complete", DMS, 0x5589b00, 0x558a180)
scan_asm("before_error_dialog", DMS, 0x556df00, 0x556e450)
scan_asm("resource_mgr_strings", RM, 0x1275000, 0x128f000)

print("\n=== .rodata matches for startup .big names ===")
for pat in [b"icfiles.big", b"shaderboot", b"gameplayattribdb", b"setplaysbig", b"manifest.db", b"manifest.xml"]:
    idx = 0
    hits = []
    while len(hits) < 6:
        idx = data.find(pat, idx)
        if idx == -1: break
        s = data[max(0, idx-32):idx+64]
        hits.append((hex(idx), repr(s)))
        idx += len(pat)
    print(f"  {pat.decode()}: {hits}")
