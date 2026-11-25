import re, struct, subprocess
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

def dump_lines(title, lines, lo=0, hi=1<<64):
    print(f"\n=== {title} ===")
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
        if note or re.search(r'\b(bl|b\.\w+|cbz|cbnz|tbz|tbnz|cmp|ret)\b', l):
            print(" ", re.sub(r'\s+<[^>]+>', '', l.strip()) + note)

def disasm(lo, hi):
    return subprocess.run(
        ["llvm-objdump", "-d", f"--start-address={hex(lo)}", f"--stop-address={hex(hi)}", SO],
        capture_output=True, text=True, check=True
    ).stdout.splitlines()

dump_lines("icfiles_loader (0x123c850..0x123ca20)", disasm(0x123c850, 0x123ca20))
dump_lines("shader_loader (0x2135ad0..0x2135ec0)", disasm(0x2135ad0, 0x2135ec0))
dump_lines("_loadAllManifests (0x5589700..0x5589b90)", DMS, 0x5589700, 0x5589b90)
dump_lines("_getUrlForName (0x558b350..0x558b690)", DMS, 0x558b350, 0x558b690)

# Check Splash_85_Percent xref
pos = data.find(b"Splash_85_Percent")
print("\nSplash_85_Percent rodata:", hex(pos) if pos != -1 else None)
