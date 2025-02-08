import functools
import random
mat = [list(map(int,x.strip().split(" "))) for x in open("mat").read().replace("-"," -").strip().split("\n")]

bits = [int("".join(str(int(bool(x))) for x in row), 2) for row in mat]


def bestest(startingpoint):
    global sumd
    path = [startingpoint]
    sumd = 0

    def best():
        global sumd
        a=bits[path[-1]]

        bestib=0
        bestd=100

        for ib,b in enumerate(bits):
            if ib not in path:
                if (a^b).bit_count() < bestd:
                    bestib=ib
                    bestd=(a^b).bit_count()
        sumd += bestd
        return bestib

    while len(path) < len(bits):
        path.append(best())
    return path,sumd

path=min([bestest(i) for i in range(len(bits))], key=lambda x:x[1])[0]
matnew = []
for i in path:
    matnew.append(mat[i])
mat=matnew

ssalist = []

next_register = 0
def regalloc():
    global next_register
    next_register += 1
    return next_register

def ssa(*args):
    ssalist.append(args)
    return len(ssalist)-1

def sumvars(a,b):
    return ssa("+", a, b)

def sumlots(xs):
    halfway = len(xs)//2
    if len(xs) > 2:
        return sumvars(sumlots(xs[:halfway]), sumlots(xs[halfway:]))
    else:
        return functools.reduce(sumvars, xs)


def multbyn(x, n):
    if n == 1:
        return x
    elif n==2:
        return sumvars(x, x)
    elif n>2:
        return sumvars(multbyn(x, n//2), multbyn(x, n-n//2))



def multvar(row, i):
    initial = ssa("load", i)
    return multbyn(initial, abs(row[i]))


reusable = []

regnames = ["rax", "rcx", "rdx", "rsi", "r8", "r9", "r10", "r11"] + [f"r{i}" for i in range(16,32)]
nregs=len(regnames)


from z3 import *

def compile(regs_from_prev, idxes_needed, ssa):
    avail = [True]*nregs

    def alloc():
        while not avail[x := random.randrange(len(avail))]:
            pass
        avail[x] = False
        return x

    for i in idxes_needed:
        if i in regs_from_prev:
            avail[regs_from_prev[i]] = False

    regs_for_next = {}

    rtl = []
    reg_for_ssa = {}
    for ssi, rest in enumerate(ssa):
        op,*arg = rest

        if op == 'load':
            if arg[0] in regs_from_prev:
                reg_for_ssa[ssi] = regs_from_prev[arg[0]]
                regs_for_next[arg[0]] = regs_from_prev[arg[0]]
                assert avail[regs_from_prev[arg[0]]] == False
            else:
                r=alloc()
                reg_for_ssa[ssi] = r
                rtl.append(('load', r, arg[0]))
                regs_for_next[arg[0]] = r
        elif op == "+":
            r=alloc()
            reg_for_ssa[ssi] = r
            rtl.append(('+', r, reg_for_ssa[arg[0]], reg_for_ssa[arg[1]]))
        elif op == "cmp_and_stuff":
            rtl.append(('cmp_and_stuff', reg_for_ssa[arg[0]], reg_for_ssa[arg[1]]))
        else:
            raise op

        avcountbefore = len([x for x in avail if x]) 
        for i in range(random.randrange(0,20)):
            if len([x for x in avail if x]) > 1:
                src = random.randrange(nregs)
                dst = alloc()
                rtl.append(('mov', dst, src))

                for k,v in list(reg_for_ssa.items()):
                    if v==src:
                        assert avail[src] == False
                        reg_for_ssa[k]=dst

                for k,v in list(regs_for_next.items()):
                    if v==src:
                        assert avail[src] == False
                        regs_for_next[k]=dst

                for k,v in list(regs_from_prev.items()):
                    if v==src:
                        regs_from_prev[k]=dst
                
                if avail[src]:
                    avail[dst] = True
                avail[src]=True
        assert len([x for x in avail if x])  >= avcountbefore

    return rtl, regs_for_next

rfp = dict()

fullprog = []

for row in mat:
    pos = [i for i,d in enumerate(row) if d>0]
    neg = [i for i,d in enumerate(row) if d<0]

    possum = sumlots([multvar(row, i) for i in pos])
    negsum = sumlots([multvar(row, i) for i in neg])

    res=regalloc()
    ssa("cmp_and_stuff", possum, negsum)

    prog, rfp = compile(rfp, [i for i,d in enumerate(row) if d!=0], ssalist)
    fullprog += prog

    next_register = 0
    ssalist=[]


def checkprog(prog, mat):
    flag = [Int(f'f{i}') for i in range(len(mat[0]))]
    s=Solver()

    constraints_normal = []

    for row in mat:
        constraints_normal.append((sum((a*b for a,b in zip(flag,row))) == 0))

    for thef in flag:
        s.add(thef > 47)
        s.add(thef <= 127)


    regs = [None]*nregs

    cools=[]

    numcmps = 0
    for op,*arg in prog:
        if op=='load':
            regs[arg[0]] = flag[arg[1]]
        elif op=='+':
            regs[arg[0]] = regs[arg[1]] + regs[arg[2]]
        elif op=='mov':
            regs[arg[0]] = regs[arg[1]]
        elif op=='cmp_and_stuff':
            cools.append(regs[arg[0]] == regs[arg[1]])

    s.add(And(*constraints_normal) != And(*cools))

    assert s.check() == unsat

checkprog(fullprog, mat)

funccode=[]
for op, *arg in fullprog:
    if op=='load':
        funccode.append(f"movzx {regnames[arg[0]]}, BYTE PTR [rdi + {arg[1]}]")
    elif op=='+':
        funccode.append(f"add {regnames[arg[0]]}, {regnames[arg[1]]}, {regnames[arg[2]]}")
    elif op=='mov':
        funccode.append(f"mov {regnames[arg[0]]}, {regnames[arg[1]]}")
    elif op=='cmp_and_stuff':
        funccode.append(f"cmp {regnames[arg[0]]}, {regnames[arg[1]]}")
        funccode.append("jne incorrect")

funccode.append("ret")

blocks = []
prevblockstart = 0
nextblockname = "funny"
namesused = set()
for i in range(len(funccode)):
    if random.choice([False, True]):
        while (new_nbn := f"block_{random.randrange(12345678)}") in namesused:
            pass
        namesused.add(new_nbn)

        blocks.append([nextblockname+":"] + funccode[prevblockstart:i] + [f"jmpabs {new_nbn}"])
        prevblockstart = i
        nextblockname = new_nbn


blocks.append([nextblockname+":"] + funccode[prevblockstart:])

random.shuffle(blocks)

print("""
.intel_syntax noprefix
.section .text
.macro jmpabs target
  .byte 0xd5, 00, 0xa1
  .quad \\target
.endm
.global funny
""")

for b in blocks:
    for l in b:
        print(l)

