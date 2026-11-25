
libFIFAMobileNeon.so.original:	file format elf64-littleaarch64

Disassembly of section .text:

0000000001225268 <_ZNSt6__ndk117bad_function_callD0Ev>:
 1276b90: 97fc2b31     	bl	0x1181854 <_ZnwmRKSt9nothrow_t+0x5c>
 1276b94: d10203ff     	sub	sp, sp, #0x80
 1276b98: a90367fa     	stp	x26, x25, [sp, #0x30]
 1276b9c: a9045ff8     	stp	x24, x23, [sp, #0x40]
 1276ba0: a90557f6     	stp	x22, x21, [sp, #0x50]
 1276ba4: a9064ff4     	stp	x20, x19, [sp, #0x60]
 1276ba8: a9077bfd     	stp	x29, x30, [sp, #0x70]
 1276bac: 9101c3fd     	add	x29, sp, #0x70
 1276bb0: aa0103f5     	mov	x21, x1
 1276bb4: aa0003f4     	mov	x20, x0
 1276bb8: 91070013     	add	x19, x0, #0x1c0
 1276bbc: 944545df     	bl	0x23c8338 <Java_com_ea_EAIO_EAIO_Shutdown+0x234dc>
 1276bc0: 79439688     	ldrh	w8, [x20, #0x1ca]
 1276bc4: aa0003f6     	mov	x22, x0
 1276bc8: 340000e8     	cbz	w8, 0x1276be4 <_ZNSt6__ndk117bad_function_callD0Ev+0x5197c>
 1276bcc: 320003e8     	orr	w8, wzr, #0x1
 1276bd0: c85ffe69     	ldaxr	x9, [x19]
 1276bd4: b50000c9     	cbnz	x9, 0x1276bec <_ZNSt6__ndk117bad_function_callD0Ev+0x51984>
 1276bd8: c809fe68     	stlxr	w9, x8, [x19]
 1276bdc: 35ffffa9     	cbnz	w9, 0x1276bd0 <_ZNSt6__ndk117bad_function_callD0Ev+0x51968>
 1276be0: 14000029     	b	0x1276c84 <_ZNSt6__ndk117bad_function_callD0Ev+0x51a1c>
 1276be4: 91074288     	add	x8, x20, #0x1d0
 1276be8: 14000019     	b	0x1276c4c <_ZNSt6__ndk117bad_function_callD0Ev+0x519e4>
 1276bec: d5033f5f     	clrex
 1276bf0: f940ea88     	ldr	x8, [x20, #0x1d0]
 1276bf4: eb16011f     	cmp	x8, x22
 1276bf8: 91074288     	add	x8, x20, #0x1d0
 1276bfc: 54000280     	b.eq	0x1276c4c <_ZNSt6__ndk117bad_function_callD0Ev+0x519e4>
 1276c00: 79439689     	ldrh	w9, [x20, #0x1ca]
 1276c04: b4000249     	cbz	x9, 0x1276c4c <_ZNSt6__ndk117bad_function_callD0Ev+0x519e4>
 1276c08: 320003ea     	orr	w10, wzr, #0x1
 1276c0c: c8dffe6b     	ldar	x11, [x19]
 1276c10: f100057f     	cmp	x11, #0x1
 1276c14: 540001c8     	b.hi	0x1276c4c <_ZNSt6__ndk117bad_function_callD0Ev+0x519e4>
 1276c18: c8dffe6b     	ldar	x11, [x19]
 1276c1c: b400008b     	cbz	x11, 0x1276c2c <_ZNSt6__ndk117bad_function_callD0Ev+0x519c4>
 1276c20: f1000529     	subs	x9, x9, #0x1
 1276c24: 54ffff41     	b.ne	0x1276c0c <_ZNSt6__ndk117bad_function_callD0Ev+0x519a4>
 1276c28: 14000009     	b	0x1276c4c <_ZNSt6__ndk117bad_function_callD0Ev+0x519e4>
 1276c2c: c85ffe6b     	ldaxr	x11, [x19]
 1276c30: b500008b     	cbnz	x11, 0x1276c40 <_ZNSt6__ndk117bad_function_callD0Ev+0x519d8>
 1276c34: c80bfe6a     	stlxr	w11, x10, [x19]
 1276c38: 35ffffab     	cbnz	w11, 0x1276c2c <_ZNSt6__ndk117bad_function_callD0Ev+0x519c4>
 1276c3c: 14000012     	b	0x1276c84 <_ZNSt6__ndk117bad_function_callD0Ev+0x51a1c>
 1276c40: d5033f5f     	clrex
 1276c44: f1000529     	subs	x9, x9, #0x1
 1276c48: 54fffe21     	b.ne	0x1276c0c <_ZNSt6__ndk117bad_function_callD0Ev+0x519a4>
 1276c4c: c85ffe69     	ldaxr	x9, [x19]
 1276c50: 91000529     	add	x9, x9, #0x1
 1276c54: c80afe69     	stlxr	w10, x9, [x19]
 1276c58: 35ffffaa     	cbnz	w10, 0x1276c4c <_ZNSt6__ndk117bad_function_callD0Ev+0x519e4>
 1276c5c: f100093f     	cmp	x9, #0x2
 1276c60: 54000123     	b.lo	0x1276c84 <_ZNSt6__ndk117bad_function_callD0Ev+0x51a1c>
 1276c64: f9400108     	ldr	x8, [x8]
 1276c68: eb16011f     	cmp	x8, x22
 1276c6c: 54000081     	b.ne	0x1276c7c <_ZNSt6__ndk117bad_function_callD0Ev+0x51a14>
 1276c70: 79439288     	ldrh	w8, [x20, #0x1c8]
 1276c74: 11000508     	add	w8, w8, #0x1
 1276c78: 14000006     	b	0x1276c90 <_ZNSt6__ndk117bad_function_callD0Ev+0x51a28>
 1276c7c: aa1303e0     	mov	x0, x19
 1276c80: 944546b5     	bl	0x23c8754 <Java_com_ea_EAIO_EAIO_Shutdown+0x238f8>
 1276c84: d5033bbf     	dmb	ish
 1276c88: 320003e8     	orr	w8, wzr, #0x1
 1276c8c: f900ea96     	str	x22, [x20, #0x1d0]
 1276c90: 79039288     	strh	w8, [x20, #0x1c8]
 1276c94: 9002af61     	adrp	x1, 0x6862000
 1276c98: 911e1821     	add	x1, x1, #0x786
 1276c9c: 910023e0     	add	x0, sp, #0x8
 1276ca0: 97fc2c3d     	bl	0x1181d94 <_ZdaPvSt11align_val_tRKSt9nothrow_t+0x178>
 1276ca4: 910043e9     	add	x9, sp, #0x10
 1276ca8: 528002e8     	mov	w8, #0x17               // =23
 1276cac: 91006136     	add	x22, x9, #0x18
 1276cb0: a901ffff     	stp	xzr, xzr, [sp, #0x18]
 1276cb4: f9000bff     	str	xzr, [sp, #0x10]
 1276cb8: 39009fe8     	strb	w8, [sp, #0x27]
 1276cbc: 910023e1     	add	x1, sp, #0x8
 1276cc0: aa1603e0     	mov	x0, x22
 1276cc4: 97fc2c3a     	bl	0x1181dac <_ZdaPvSt11align_val_tRKSt9nothrow_t+0x190>
 1276cc8: d10006a8     	sub	x8, x21, #0x1
 1276ccc: 38401d09     	ldrb	w9, [x8, #0x1]!
 1276cd0: 35ffffe9     	cbnz	w9, 0x1276ccc <_ZNSt6__ndk117bad_function_callD0Ev+0x51a64>
 1276cd4: cb150117     	sub	x23, x8, x21
 1276cd8: f10062ff     	cmp	x23, #0x18
 1276cdc: 54000123     	b.lo	0x1276d00 <_ZNSt6__ndk117bad_function_callD0Ev+0x51a98>
 1276ce0: 910006e1     	add	x1, x23, #0x1
 1276ce4: aa1603e0     	mov	x0, x22
 1276ce8: 2a1f03e2     	mov	w2, wzr
 1276cec: 97fc2c3a     	bl	0x1181dd4 <_ZdaPvSt11align_val_tRKSt9nothrow_t+0x1b8>
 1276cf0: b24102e8     	orr	x8, x23, #0x8000000000000000
 1276cf4: a9017fe0     	stp	x0, xzr, [sp, #0x10]
 1276cf8: f90013e8     	str	x8, [sp, #0x20]
 1276cfc: 14000006     	b	0x1276d14 <_ZNSt6__ndk117bad_function_callD0Ev+0x51aac>
 1276d00: 910043e0     	add	x0, sp, #0x10
 1276d04: 528002e8     	mov	w8, #0x17               // =23
 1276d08: a901ffff     	stp	xzr, xzr, [sp, #0x18]
 1276d0c: f9000bff     	str	xzr, [sp, #0x10]
 1276d10: 39009fe8     	strb	w8, [sp, #0x27]
 1276d14: aa1503e1     	mov	x1, x21
 1276d18: aa1703e2     	mov	x2, x23
 1276d1c: 97e9f637     	bl	0xcf45f8 <memmove@plt>
 1276d20: 39c09fe8     	ldrsb	w8, [sp, #0x27]
 1276d24: 37f80168     	tbnz	w8, #0x1f, 0x1276d50 <_ZNSt6__ndk117bad_function_callD0Ev+0x51ae8>
 1276d28: 528002e8     	mov	w8, #0x17               // =23
 1276d2c: 4b170109     	sub	w9, w8, w23
 1276d30: 13001d28     	sxtb	w8, w9
 1276d34: 39009fe9     	strb	w9, [sp, #0x27]
 1276d38: 37f80108     	tbnz	w8, #0x1f, 0x1276d58 <_ZNSt6__ndk117bad_function_callD0Ev+0x51af0>
 1276d3c: 528002e9     	mov	w9, #0x17               // =23
 1276d40: cb28c128     	sub	x8, x9, w8, sxtw
 1276d44: 910043e9     	add	x9, sp, #0x10
 1276d48: 8b080128     	add	x8, x9, x8
 1276d4c: 14000006     	b	0x1276d64 <_ZNSt6__ndk117bad_function_callD0Ev+0x51afc>
 1276d50: f9000ff7     	str	x23, [sp, #0x18]
 1276d54: 14000002     	b	0x1276d5c <_ZNSt6__ndk117bad_function_callD0Ev+0x51af4>
 1276d58: f9400ff7     	ldr	x23, [sp, #0x18]
 1276d5c: f9400be8     	ldr	x8, [sp, #0x10]
 1276d60: 8b170108     	add	x8, x8, x23
 1276d64: 910b6298     	add	x24, x20, #0x2d8
 1276d68: 3900011f     	strb	wzr, [x8]
 1276d6c: 910043e1     	add	x1, sp, #0x10
 1276d70: aa1803e0     	mov	x0, x24
 1276d74: 94005d32     	bl	0x128e23c <_ZNSt6__ndk117bad_function_callD0Ev+0x68fd4>
 1276d78: aa0003f7     	mov	x23, x0
 1276d7c: b5000380     	cbnz	x0, 0x1276dec <_ZNSt6__ndk117bad_function_callD0Ev+0x51b84>
 1276d80: 910a8299     	add	x25, x20, #0x2a0
 1276d84: 910043e1     	add	x1, sp, #0x10
 1276d88: aa1903e0     	mov	x0, x25
 1276d8c: 94000078     	bl	0x1276f6c <_ZNSt6__ndk117bad_function_callD0Ev+0x51d04>
 1276d90: 910aa288     	add	x8, x20, #0x2a8
 1276d94: eb08001f     	cmp	x0, x8
 1276d98: aa1f03f7     	mov	x23, xzr
 1276d9c: 54000281     	b.ne	0x1276dec <_ZNSt6__ndk117bad_function_callD0Ev+0x51b84>
 1276da0: f9413e88     	ldr	x8, [x20, #0x278]
 1276da4: 9109e297     	add	x23, x20, #0x278
 1276da8: eb17011f     	cmp	x8, x23
 1276dac: 54000180     	b.eq	0x1276ddc <_ZNSt6__ndk117bad_function_callD0Ev+0x51b74>
 1276db0: aa1703fa     	mov	x26, x23
 1276db4: f9400748     	ldr	x8, [x26, #0x8]
 1276db8: f9400900     	ldr	x0, [x8, #0x10]
 1276dbc: aa1503e1     	mov	x1, x21
 1276dc0: 94005acc     	bl	0x128d8f0 <_ZNSt6__ndk117bad_function_callD0Ev+0x68688>
 1276dc4: aa0003e1     	mov	x1, x0
 1276dc8: b50004c1     	cbnz	x1, 0x1276e60 <_ZNSt6__ndk117bad_function_callD0Ev+0x51bf8>
 1276dcc: f940075a     	ldr	x26, [x26, #0x8]
 1276dd0: f94002e8     	ldr	x8, [x23]
 1276dd4: eb1a011f     	cmp	x8, x26
 1276dd8: 54fffee1     	b.ne	0x1276db4 <_ZNSt6__ndk117bad_function_callD0Ev+0x51b4c>
 1276ddc: 910043e2     	add	x2, sp, #0x10
 1276de0: aa1903e0     	mov	x0, x25
 1276de4: 94000af2     	bl	0x12799ac <_ZNSt6__ndk117bad_function_callD0Ev+0x54744>
 1276de8: aa1f03f7     	mov	x23, xzr
 1276dec: 39c09fe8     	ldrsb	w8, [sp, #0x27]
 1276df0: 36f80108     	tbz	w8, #0x1f, 0x1276e10 <_ZNSt6__ndk117bad_function_callD0Ev+0x51ba8>
 1276df4: f9400be1     	ldr	x1, [sp, #0x10]
 1276df8: b40000c1     	cbz	x1, 0x1276e10 <_ZNSt6__ndk117bad_function_callD0Ev+0x51ba8>
 1276dfc: f94013e8     	ldr	x8, [sp, #0x20]
 1276e00: 9240f908     	and	x8, x8, #0x7fffffffffffffff
 1276e04: 91000502     	add	x2, x8, #0x1
 1276e08: aa1603e0     	mov	x0, x22
 1276e0c: 97fc2c06     	bl	0x1181e24 <_ZdaPvSt11align_val_tRKSt9nothrow_t+0x208>
 1276e10: 79439288     	ldrh	w8, [x20, #0x1c8]
 1276e14: 51000508     	sub	w8, w8, #0x1
 1276e18: 72003d1f     	tst	w8, #0xffff
 1276e1c: 79039288     	strh	w8, [x20, #0x1c8]
 1276e20: 540002c1     	b.ne	0x1276e78 <_ZNSt6__ndk117bad_function_callD0Ev+0x51c10>
 1276e24: f900ea9f     	str	xzr, [x20, #0x1d0]
 1276e28: d5033bbf     	dmb	ish
 1276e2c: c85ffe68     	ldaxr	x8, [x19]
 1276e30: f1000508     	subs	x8, x8, #0x1
 1276e34: c809fe68     	stlxr	w9, x8, [x19]
 1276e38: 35ffffa9     	cbnz	w9, 0x1276e2c <_ZNSt6__ndk117bad_function_callD0Ev+0x51bc4>
 1276e3c: 54000281     	b.ne	0x1276e8c <_ZNSt6__ndk117bad_function_callD0Ev+0x51c24>
 1276e40: aa1703e0     	mov	x0, x23
 1276e44: a9477bfd     	ldp	x29, x30, [sp, #0x70]
 1276e48: a9464ff4     	ldp	x20, x19, [sp, #0x60]
 1276e4c: a94557f6     	ldp	x22, x21, [sp, #0x50]
 1276e50: a9445ff8     	ldp	x24, x23, [sp, #0x40]
 1276e54: a94367fa     	ldp	x26, x25, [sp, #0x30]
 1276e58: 910203ff     	add	sp, sp, #0x80
 1276e5c: d65f03c0     	ret
 1276e60: aa1803e0     	mov	x0, x24
 1276e64: 94005d77     	bl	0x128e440 <_ZNSt6__ndk117bad_function_callD0Ev+0x691d8>
 1276e68: aa0003f7     	mov	x23, x0
 1276e6c: 39c09fe8     	ldrsb	w8, [sp, #0x27]
 1276e70: 36fffd08     	tbz	w8, #0x1f, 0x1276e10 <_ZNSt6__ndk117bad_function_callD0Ev+0x51ba8>
 1276e74: 17ffffe0     	b	0x1276df4 <_ZNSt6__ndk117bad_function_callD0Ev+0x51b8c>
 1276e78: c85ffe68     	ldaxr	x8, [x19]
 1276e7c: d1000508     	sub	x8, x8, #0x1
 1276e80: c809fe68     	stlxr	w9, x8, [x19]
 1276e84: 35ffffa9     	cbnz	w9, 0x1276e78 <_ZNSt6__ndk117bad_function_callD0Ev+0x51c10>
 1276e88: 17ffffee     	b	0x1276e40 <_ZNSt6__ndk117bad_function_callD0Ev+0x51bd8>
 1276e8c: aa1303e0     	mov	x0, x19
 1276e90: 9445462f     	bl	0x23c874c <Java_com_ea_EAIO_EAIO_Shutdown+0x238f0>
 1276e94: 17ffffeb     	b	0x1276e40 <_ZNSt6__ndk117bad_function_callD0Ev+0x51bd8>
 1276e98: 97fc2a6f     	bl	0x1181854 <_ZnwmRKSt9nothrow_t+0x5c>
 1276e9c: 39c09fe8     	ldrsb	w8, [sp, #0x27]
 1276ea0: aa0003f5     	mov	x21, x0
 1276ea4: 36f80368     	tbz	w8, #0x1f, 0x1276f10 <_ZNSt6__ndk117bad_function_callD0Ev+0x51ca8>
 1276ea8: 14000013     	b	0x1276ef4 <_ZNSt6__ndk117bad_function_callD0Ev+0x51c8c>
 1276eac: 39c09fe8     	ldrsb	w8, [sp, #0x27]
 1276eb0: aa0003f5     	mov	x21, x0
 1276eb4: 36f802e8     	tbz	w8, #0x1f, 0x1276f10 <_ZNSt6__ndk117bad_function_callD0Ev+0x51ca8>
 1276eb8: 1400000f     	b	0x1276ef4 <_ZNSt6__ndk117bad_function_callD0Ev+0x51c8c>
 1276ebc: 97fc2a66     	bl	0x1181854 <_ZnwmRKSt9nothrow_t+0x5c>
 1276ec0: 39c09fe8     	ldrsb	w8, [sp, #0x27]
 1276ec4: aa0003f5     	mov	x21, x0
 1276ec8: 36f80248     	tbz	w8, #0x1f, 0x1276f10 <_ZNSt6__ndk117bad_function_callD0Ev+0x51ca8>
 1276ecc: 1400000a     	b	0x1276ef4 <_ZNSt6__ndk117bad_function_callD0Ev+0x51c8c>
 1276ed0: 39c09fe8     	ldrsb	w8, [sp, #0x27]
 1276ed4: aa0003f5     	mov	x21, x0
 1276ed8: 36f801c8     	tbz	w8, #0x1f, 0x1276f10 <_ZNSt6__ndk117bad_function_callD0Ev+0x51ca8>
 1276edc: 14000006     	b	0x1276ef4 <_ZNSt6__ndk117bad_function_callD0Ev+0x51c8c>
 1276ee0: aa0003f5     	mov	x21, x0
 1276ee4: 1400000b     	b	0x1276f10 <_ZNSt6__ndk117bad_function_callD0Ev+0x51ca8>
 1276ee8: 39c09fe8     	ldrsb	w8, [sp, #0x27]
 1276eec: aa0003f5     	mov	x21, x0
 1276ef0: 36f80108     	tbz	w8, #0x1f, 0x1276f10 <_ZNSt6__ndk117bad_function_callD0Ev+0x51ca8>
 1276ef4: f9400be1     	ldr	x1, [sp, #0x10]
 1276ef8: b40000c1     	cbz	x1, 0x1276f10 <_ZNSt6__ndk117bad_function_callD0Ev+0x51ca8>
 1276efc: f94013e8     	ldr	x8, [sp, #0x20]
