import re, struct, array
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

def show_annotated(title, lo, hi):
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

show_annotated("field_offsets_Visit", 0x558d200, 0x558d740)
show_annotated("err_fn_head", 0x556e49c, 0x556e650)
show_annotated("err_caller_in_DMS", 0x558a7a0, 0x558aa50)

print("\n=== #0x58 accesses in DeviceManifestService ===")
for l in DMS:
    if "#0x58]" in l:
        print(" ", re.sub(r'\s+<[^>]+>', '', l.strip()))

print("\n=== Callers in .text (BL targets) ===")
targets = {0x1276b94, 0x1276dc0, 0x556e49c, 0x556e0e8, 0x556e654}
text_va, text_sz = 0x0cf7000, 0x5b661a8
insns = array.array("I")
insns.frombytes(data[text_va:text_va + text_sz])
for i, w in enumerate(insns):
    if (w >> 26) == 0x25:
        imm = w & 0x03FFFFFF
        if imm & 0x02000000: imm -= 0x04000000
        pc = text_va + i * 4
        tgt = pc + (imm << 2)
        if tgt in targets:
            print(f"  {hex(pc)} -> bl {hex(tgt)}")

print("\n=== Sample DynamicAssets/android files ===")
da = Path("apk/base_extract/assets/Data/DynamicAssets/android")
if da.exists():
    files = sorted(str(p.relative_to("apk/base_extract/assets/Data")) for p in da.rglob("*") if p.is_file())
    print(f"  total={len(files)}, first 15: {files[:15]}")
