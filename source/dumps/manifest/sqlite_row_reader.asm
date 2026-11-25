
libFIFAMobileNeon.so.original:	file format elf64-littleaarch64

Disassembly of section .text:

0000000001225268 <_ZNSt6__ndk117bad_function_callD0Ev>:
 128d8f0: a9ba6ffc     	stp	x28, x27, [sp, #-0x60]!
 128d8f4: a90167fa     	stp	x26, x25, [sp, #0x10]
 128d8f8: a9025ff8     	stp	x24, x23, [sp, #0x20]
 128d8fc: a90357f6     	stp	x22, x21, [sp, #0x30]
 128d900: a9044ff4     	stp	x20, x19, [sp, #0x40]
 128d904: a9057bfd     	stp	x29, x30, [sp, #0x50]
 128d908: 910143fd     	add	x29, sp, #0x50
 128d90c: 399a5c08     	ldrsb	x8, [x0, #0x697]
 128d910: aa0103f6     	mov	x22, x1
 128d914: aa0003f3     	mov	x19, x0
 128d918: 91198014     	add	x20, x0, #0x660
 128d91c: 911a0015     	add	x21, x0, #0x680
 128d920: b7f800c8     	tbnz	x8, #0x3f, 0x128d938 <_ZNSt6__ndk117bad_function_callD0Ev+0x686d0>
 128d924: 528002e9     	mov	w9, #0x17               // =23
 128d928: cb080128     	sub	x8, x9, x8
 128d92c: 8b0802a8     	add	x8, x21, x8
 128d930: aa1503e0     	mov	x0, x21
 128d934: 14000004     	b	0x128d944 <_ZNSt6__ndk117bad_function_callD0Ev+0x686dc>
 128d938: f9434260     	ldr	x0, [x19, #0x680]
 128d93c: f9434668     	ldr	x8, [x19, #0x688]
 128d940: 8b080008     	add	x8, x0, x8
 128d944: d10006d7     	sub	x23, x22, #0x1
 128d948: aa1703e9     	mov	x9, x23
 128d94c: 38401d2a     	ldrb	w10, [x9, #0x1]!
 128d950: 35ffffea     	cbnz	w10, 0x128d94c <_ZNSt6__ndk117bad_function_callD0Ev+0x686e4>
 128d954: cb160138     	sub	x24, x9, x22
 128d958: cb000119     	sub	x25, x8, x0
 128d95c: eb19031f     	cmp	x24, x25
 128d960: 9a99b302     	csel	x2, x24, x25, lt
 128d964: aa1603e1     	mov	x1, x22
 128d968: 1a9fa7fa     	cset	w26, lt
 128d96c: 97e99b27     	bl	0xcf4608 <memcmp@plt>
 128d970: eb18033f     	cmp	x25, x24
 128d974: 5a9fa348     	csinv	w8, w26, wzr, ge
 128d978: 7100001f     	cmp	w0, #0x0
 128d97c: 1a800108     	csel	w8, w8, w0, eq
 128d980: 34001868     	cbz	w8, 0x128dc8c <_ZNSt6__ndk117bad_function_callD0Ev+0x68a24>
 128d984: f9400668     	ldr	x8, [x19, #0x8]
 128d988: b40006c8     	cbz	x8, 0x128da60 <_ZNSt6__ndk117bad_function_callD0Ev+0x687f8>
 128d98c: f9400a78     	ldr	x24, [x19, #0x10]
 128d990: b4000698     	cbz	x24, 0x128da60 <_ZNSt6__ndk117bad_function_callD0Ev+0x687f8>
 128d994: aa1603e0     	mov	x0, x22
 128d998: 9444b2fc     	bl	0x23ba588 <Java_com_ea_EAIO_EAIO_Shutdown+0x1572c>
 128d99c: aa0003e3     	mov	x3, x0
 128d9a0: 320003e1     	orr	w1, wzr, #0x1
 128d9a4: aa1803e0     	mov	x0, x24
 128d9a8: aa1603e2     	mov	x2, x22
 128d9ac: aa1f03e4     	mov	x4, xzr
 128d9b0: 943c2e39     	bl	0x2199294 <Java_com_ea_rwfilesystem_rwfilesystem_Shutdown+0xd0c38>
 128d9b4: 2a0003e8     	mov	w8, w0
 128d9b8: aa1f03e0     	mov	x0, xzr
 128d9bc: 350016a8     	cbnz	w8, 0x128dc90 <_ZNSt6__ndk117bad_function_callD0Ev+0x68a28>
 128d9c0: f9400a60     	ldr	x0, [x19, #0x10]
 128d9c4: 943c21e9     	bl	0x2196168 <Java_com_ea_rwfilesystem_rwfilesystem_Shutdown+0xcdb0c>
 128d9c8: 34000500     	cbz	w0, 0x128da68 <_ZNSt6__ndk117bad_function_callD0Ev+0x68800>
 128d9cc: 7101941f     	cmp	w0, #0x65
 128d9d0: 540004c0     	b.eq	0x128da68 <_ZNSt6__ndk117bad_function_callD0Ev+0x68800>
 128d9d4: 7101901f     	cmp	w0, #0x64
 128d9d8: aa1f03e0     	mov	x0, xzr
 128d9dc: 540015a1     	b.ne	0x128dc90 <_ZNSt6__ndk117bad_function_callD0Ev+0x68a28>
 128d9e0: f9400a60     	ldr	x0, [x19, #0x10]
 128d9e4: 2a1f03e1     	mov	w1, wzr
 128d9e8: 943c2a48     	bl	0x2198308 <Java_com_ea_rwfilesystem_rwfilesystem_Shutdown+0xcfcac>
 128d9ec: f9400a68     	ldr	x8, [x19, #0x10]
 128d9f0: aa0003fa     	mov	x26, x0
 128d9f4: 320003e1     	orr	w1, wzr, #0x1
 128d9f8: aa0803e0     	mov	x0, x8
 128d9fc: 943c29a7     	bl	0x2198098 <Java_com_ea_rwfilesystem_rwfilesystem_Shutdown+0xcfa3c>
 128da00: f9400a68     	ldr	x8, [x19, #0x10]
 128da04: 2a0003f8     	mov	w24, w0
 128da08: 321f03e1     	orr	w1, wzr, #0x2
 128da0c: aa0803e0     	mov	x0, x8
 128da10: 943c29a2     	bl	0x2198098 <Java_com_ea_rwfilesystem_rwfilesystem_Shutdown+0xcfa3c>
 128da14: 2a0003f9     	mov	w25, w0
 128da18: d100075b     	sub	x27, x26, #0x1
 128da1c: 38401f68     	ldrb	w8, [x27, #0x1]!
 128da20: 35ffffe8     	cbnz	w8, 0x128da1c <_ZNSt6__ndk117bad_function_callD0Ev+0x687b4>
 128da24: 39805e88     	ldrsb	x8, [x20, #0x17]
 128da28: cb1a037c     	sub	x28, x27, x26
 128da2c: b7f80228     	tbnz	x8, #0x3f, 0x128da70 <_ZNSt6__ndk117bad_function_callD0Ev+0x68808>
 128da30: 528002e9     	mov	w9, #0x17               // =23
 128da34: cb080122     	sub	x2, x9, x8
 128da38: eb02039f     	cmp	x28, x2
 128da3c: aa1403e0     	mov	x0, x20
 128da40: 54000209     	b.ls	0x128da80 <_ZNSt6__ndk117bad_function_callD0Ev+0x68818>
 128da44: aa1a03e1     	mov	x1, x26
 128da48: 97e99aec     	bl	0xcf45f8 <memmove@plt>
 128da4c: 39805e88     	ldrsb	x8, [x20, #0x17]
 128da50: b7f80328     	tbnz	x8, #0x3f, 0x128dab4 <_ZNSt6__ndk117bad_function_callD0Ev+0x6884c>
 128da54: 528002e9     	mov	w9, #0x17               // =23
 128da58: cb080128     	sub	x8, x9, x8
 128da5c: 14000017     	b	0x128dab8 <_ZNSt6__ndk117bad_function_callD0Ev+0x68850>
 128da60: aa1f03e0     	mov	x0, xzr
 128da64: 1400008b     	b	0x128dc90 <_ZNSt6__ndk117bad_function_callD0Ev+0x68a28>
 128da68: aa1f03f4     	mov	x20, xzr
 128da6c: 14000084     	b	0x128dc7c <_ZNSt6__ndk117bad_function_callD0Ev+0x68a14>
 128da70: f9433662     	ldr	x2, [x19, #0x668]
 128da74: f9433260     	ldr	x0, [x19, #0x660]
 128da78: eb02039f     	cmp	x28, x2
 128da7c: 54fffe48     	b.hi	0x128da44 <_ZNSt6__ndk117bad_function_callD0Ev+0x687dc>
 128da80: aa1a03e1     	mov	x1, x26
 128da84: aa1c03e2     	mov	x2, x28
 128da88: 97e99adc     	bl	0xcf45f8 <memmove@plt>
 128da8c: 39805e88     	ldrsb	x8, [x20, #0x17]
 128da90: b7f801e8     	tbnz	x8, #0x3f, 0x128dacc <_ZNSt6__ndk117bad_function_callD0Ev+0x68864>
 128da94: 528002e9     	mov	w9, #0x17               // =23
 128da98: cb080129     	sub	x9, x9, x8
 128da9c: 8b09029a     	add	x26, x20, x9
 128daa0: aa1403e9     	mov	x9, x20
 128daa4: 8b1c013b     	add	x27, x9, x28
 128daa8: eb1a037c     	subs	x28, x27, x26
 128daac: 540001c1     	b.ne	0x128dae4 <_ZNSt6__ndk117bad_function_callD0Ev+0x6887c>
 128dab0: 14000027     	b	0x128db4c <_ZNSt6__ndk117bad_function_callD0Ev+0x688e4>
 128dab4: f9433668     	ldr	x8, [x19, #0x668]
 128dab8: 8b080341     	add	x1, x26, x8
 128dabc: aa1403e0     	mov	x0, x20
 128dac0: aa1b03e2     	mov	x2, x27
 128dac4: 97fc23b5     	bl	0x1196998 <_ZdaPvSt11align_val_tRKSt9nothrow_t+0x14d7c>
 128dac8: 14000021     	b	0x128db4c <_ZNSt6__ndk117bad_function_callD0Ev+0x688e4>
 128dacc: f9433269     	ldr	x9, [x19, #0x660]
 128dad0: f943366a     	ldr	x10, [x19, #0x668]
 128dad4: 8b0a013a     	add	x26, x9, x10
 128dad8: 8b1c013b     	add	x27, x9, x28
 128dadc: eb1a037c     	subs	x28, x27, x26
