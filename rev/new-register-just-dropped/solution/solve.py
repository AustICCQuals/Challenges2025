from z3 import *
import re


# objdump --insn-width=13  --disassemble  -j .text -M x86_64,intel new-register-just-dropped > disas
idxbyaddr = dict()
insns = []
for l in open("disas"):
    if m := re.search("^  (.{6}):\t........................................(.*)$", l):
        idxbyaddr[int(m[1], 16)] = len(insns)
        insns.append(m[2])

def linearize(insns, a):
    insns_linear = []

    while True:
        i = idxbyaddr[a]

        while True:
            if insns[i].startswith("jmpabs"):
                a = int(insns[i].split(" 0x")[1], 16)
                break
            elif insns[i].startswith("ret"):
                return insns_linear
            else:
                insns_linear.append(insns[i])
                i += 1

    return insns_linear


lin = linearize(insns, 0x409216) # from disassembly of main in binja - this address is the undecompilable function which gets called.


s=Solver()
flag = [Int(f"f{x}") for x in range(33)]

for f in flag:
    s.add(f > 47)
    s.add(f <= 127)

regs = dict()

for i in lin:
    if (m := re.match("mov\s*(r.*),(r.*)", i)):
        if m[2] not in regs:
            regs[m[2]] = None

        regs[m[1]] = regs[m[2]]

    elif (m := re.match("movzx\s*(r.*),BYTE PTR \[rdi\+0x(.*)\]", i)):
        regs[m[1]] = flag[int(m[2], 16)]
    # special case for 0
    elif (m := re.match("movzx\s*(r.*),BYTE PTR \[rdi\]", i)):
        regs[m[1]] = flag[0]

    elif (m := re.match("add\s*(r.*),(r.*),(r.*)", i)):
        regs[m[1]] = regs[m[2]]+regs[m[3]]

    elif (m := re.match("cmp\s*(r.*),(r.*)", i)):
        s.add(regs[m[1]] == regs[m[2]])

    elif i.startswith("jne"):
        pass

    else:
        print("cant decomp", i)
        exit(1)


print(s.check())
m=s.model()
print("".join(chr(m[x].as_long()) for x in flag))
