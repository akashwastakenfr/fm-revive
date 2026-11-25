import struct

FILE = "libFIFAMobileNeon.so"
TEXT_START = 0x0cf7000
TEXT_SIZE = 0x5b661a8

TARGETS = {
    0x7162a12: "HOST_NAME_DOWNLOAD_ERROR",
    0x7162a39: "HOST_NAME_DOWNLOAD_NULL",
    0x7162a6e: "HOST_NAME_CONFIG_LENGTH_ZERO",
    0x7162a99: "HOST_NAME_VERIFY_FAILED",

    0x6b960f6: "initializeHostNameFetch",
    0x6b9614a: "_doInitializeHostNameFetch",
    0x6b96165: "ConfigService_doInitializeHostNameFetch",
    0x6b961c6: "_doInitializeHostNameFetchDefault",
    0x6b9620c: "_oninitializeHostNameFetch",

    0x6b983a1: "_config_getFifaMobileHostNameFetchUrl",
    0x6b983c7: "_config_verifyFifaMobileHostNameFetch",
}

with open(FILE, "rb") as f:
    f.seek(TEXT_START)
    code = f.read(TEXT_SIZE)

if len(code) != TEXT_SIZE:
    raise RuntimeError("Could not read the complete .text section")

pages = {}
for addr, name in TARGETS.items():
    pages.setdefault(addr & ~0xfff, []).append((addr, name))

hits = []

for off in range(0, len(code) - 32, 4):
    insn = struct.unpack_from("<I", code, off)[0]

    # AArch64 ADRP
    if (insn & 0x9f000000) != 0x90000000:
        continue

    immlo = (insn >> 29) & 3
    immhi = (insn >> 5) & 0x7ffff
    imm = (immhi << 2) | immlo

    if imm & (1 << 20):
        imm -= 1 << 21

    pc = TEXT_START + off
    page = (pc & ~0xfff) + (imm << 12)

    if page not in pages:
        continue

    base_reg = insn & 31

    # Look for ADD immediate using the ADRP register.
    for j in range(1, 5):
        nxt = struct.unpack_from("<I", code, off + j * 4)[0]

        if (nxt & 0x7f000000) != 0x11000000:
            continue

        rn = (nxt >> 5) & 31

        if rn != base_reg:
            continue

        rd = nxt & 31
        value = (nxt >> 10) & 0xfff

        if (nxt >> 22) & 1:
            value <<= 12

        address = page + value

        for target, name in TARGETS.items():
            if address == target:
                hits.append((
                    pc,
                    pc + j * 4,
                    target,
                    name,
                    rd
                ))

out = "source/hostname-exact-references.txt"

with open(out, "w") as f:
    for adrp, add, target, name, reg in hits:
        f.write(
            f"ADRP=0x{adrp:x} "
            f"ADD=0x{add:x} "
            f"TARGET=0x{target:x} "
            f"NAME={name} "
            f"REG=x{reg}\n"
        )

print("Exact ADRP+ADD candidates:", len(hits))
print("Saved:", out)

for adrp, add, target, name, reg in hits:
    print(
        f"ADRP=0x{adrp:x} "
        f"ADD=0x{add:x} "
        f"TARGET=0x{target:x} "
        f"NAME={name} "
        f"REG=x{reg}"
    )
