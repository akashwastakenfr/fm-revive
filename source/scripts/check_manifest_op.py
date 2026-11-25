import re, struct
from pathlib import Path

SO = "libFIFAMobileNeon.so.original"
DMS = Path("source/dumps/manifest/device_manifest_service.asm").read_text().splitlines()
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
        c = data[off+d:off+d+100].split(b"\x00", 1)[0]
        if len(c) >= 2 and all(32 <= b < 127 for b in c):
            return c.decode("ascii")
    return None

def dump(title, lo, hi):
    print(f"\n=== {title} ({hex(lo)}..{hex(hi)}) ===")
    pages = {}
    for l in DMS:
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
        clean = re.sub(r'\s+<[^>]+>', '', l.strip())
        print(f"  {clean}{note}")

dump("556c318_onAssetError", 0x556c318, 0x556c500)
dump("556d9b0_op",           0x556d9b0, 0x556da60)
dump("5586fe0_op_clear",     0x5586fe0, 0x5587190)
dump("55720b0_to_556e654",   0x55720b0, 0x55721a0)
