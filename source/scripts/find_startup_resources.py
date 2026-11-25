import re, struct, array
from pathlib import Path

SO = "libFIFAMobileNeon.so.original"
DMS = Path("source/dumps/manifest/device_manifest_service.asm").read_text().splitlines()
data = Path(SO).read_bytes()

print("=== DMS method addresses (0x558bfd0..0x558c5d0) ===")
for l in DMS:
    m = re.match(r'^\s*([0-9a-f]+):', l)
    if m and 0x558bfd0 <= int(m.group(1), 16) <= 0x558c5d0:
        if re.search(r'\b(adrp|add|b|bl)\b', l):
            print(" ", re.sub(r'\s+<[^>]+>', '', l.strip()))

targets = {
    0x686a239: "icfiles.big",
    0x68cf372: "shader_verylow.big",
    0x68cf385: "shader.big",
    0x68cf39c: "shaderboot_low.big",
    0x68cf3af: "shaderboot_verylow.big",
    0x68cf3c6: "shaderboot.big",
    0x6d1585d: "gameplayattribdb.big",
    0x68f69c7: "setplaysbig.big",
}
# Also resolve exact VAs for shaderboot strings in case offsets differ by 1-2 bytes
for k in [b"shaderboot.big", b"shader.big", b"icfiles.big", b"gameplayattribdb.big", b"setplaysbig.big"]:
    pos = data.find(k)
    if pos != -1:
        targets[pos] = k.decode()
        targets[pos - 8] = "[hx]" + k.decode()

pages = {va & ~0xFFF for va in targets}
text_va, text_sz = 0x0cf7000, 0x5b661a8
insns = array.array("I")
insns.frombytes(data[text_va:text_va + text_sz])

print("\n=== .text xrefs to startup .big strings ===")
for i, w in enumerate(insns):
    if (w & 0x9F000000) == 0x90000000:
        imm = (((w >> 5) & 0x7FFFF) << 2) | ((w >> 29) & 3)
        if imm & 0x100000: imm -= 0x200000
        pc = text_va + i * 4
        page = (pc & ~0xFFF) + (imm << 12)
        if page in pages:
            rd = w & 0x1F
            for j in range(1, min(6, len(insns) - i)):
                w2 = insns[i + j]
                if (w2 & 0xFFC00000) == 0x91000000 and ((w2 >> 5) & 0x1F) == rd:
                    va = page + ((w2 >> 10) & 0xFFF)
                    if va in targets:
                        print(f"  {hex(pc)}: {targets[va]} ({hex(va)})")
