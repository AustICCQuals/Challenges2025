Binja/Ghidra/etc can decompile the `main` function, which grabs the flag and checks that characters are in-range and in the flag format, before calling another function.

`main` also refuses to run unless `CPUID.(EAX=0x7, ECX=1).EDX[21] == 1`, which e.g. the CPUID article on Wikipedia shows represents Intel Advanced Performance Extensions. This will not be available on any CPUs until 2026, but the binary can be run under Intel's Software Development Emulator with the `-future` flag.

No decompilers (to my knowledge) support this ISA, but the latest release of binutils does, so it can be disassembled with `objdump -d` (ideally `objdump -d -M x86_64,intel`, if you have good taste...)

The checker function has 6 types of instrution:
* Loading a byte (zero-extended to 64 bit) from `[rsi + offset]` (i.e. `flag[offset]`), potentially into one of the new registers
* Additions (in the new 3-operand format)
* Comparisons follwed by jumps to `puts("incorrect")`
* Unconditional jumps in the new 64-bit absolute encoding (i.e. randomly shuffling the layout of the function at a sub-basic-block level)

Each comparison is checking a row of a system of equations with small integer coefficients, e.g. `f[0] + 3*f[20] == 4*f[3] + 2*f[9] + 3*f[5]`

The intended solution is to use some regexe to untangle the objdump output, putting the blocks back in order, then forming a system of equations with z3.

... or, if you're cool, you can write a binja plugin :)

The final z3 step might look like this:

```python
mat = """
-1 0-2 0 0 0 1 0 0 0 0 0-1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 1
 0 0 0 0-1 0 0 1 0 0-1 0 0 0 0 0 6 0 0 0 0 0 0 0 0 0 0 1 0 0 0-3 0
 0 0 0 1 0 0 0 0 0 0 0-1 0 1 0 0 0 0-6 0 0 0 0 0 0 0 0 0 0 0 0 1 1
 0 1 0 0 0 0 0 0 0 5 0 0 0 0 0-1 0 1 0 0 0 0 0 0 0 0 0 0 0-1 0-4 0
 0 1 0 0 0 0 0 0 0 0 0 0 0-1 0-1 0 0 0 1 0-1 0-1 0 0 0 0 0 0 0 1 0
 0 0 0 1-1 4 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0-1 0 0 0 0-4 0
 0 0-3 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 2 0 0-1 1 0 0 0-1 0 0 1 0
 0 0 0 1-1 0 0 0 0 0 0 0 0 0-1 0 0 0-6 0 0 0 0 0 0 0-1 0 0 0 0 4 0
 0 0 0 0 1 0 0 0 0 0 0-1 0 1 0 0 0 0 0 0 0-4 0 0 0 0 1 0 0 0-1 1 0
 0 1 0 0 0 0 0-6 0 0-1 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0
 0 0 0 0 0 0 0 0 0 0 0 0-1-1 0 0-5 0 0 0 0 0 0 0 0 0 0 0 1 1 0 2 0
 6 0 0 0 0 0 0 0 0 0 1 0 0 0-1 0-1 0 0-1 0 0 1 0 0 0 0 0 0 0 0-5 0
 0 0 0 0 0-1 5 0 0 0 0 0-6 0-1 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1
 1 0 0 0 0 0 0 0 0 0 0 0 0-1 0 0-5 0 1 0 0 1 0 0 0 0 0 0 0 0 0 1 0
 0 0 4 1-1 0 0 0 0 0-1 0 0-1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0-3 0
 0-3 0 0 0 0 0 0 0 0 0-1 0-1 0 0 0 0 0 0 0 0 1 0 1 0 0 0 0 0-1 3 0
 0 0 1 0-1 0 0 0 0-1 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0-1 0
 0 0 0 0 1-2-1 0-1 0 0 0 0 0 0 0 0 0 0 0 0 0-1 0 1 0 0 0 0 0 0 3 0
 0 0 0 0 0-4 1 0 0 0 0 0 0-1 0 0 0 0 0 0 0 0 0-1 0 0 0 1 0-1 0 4 0
 0-2 0 0 0 1 0 0 0 0 0 0 0-1 0-1 0 0 0 0 0 0 0 0 0 0 0 0 0-1-1 4 0
 0 0 0 0 0 0 5 0 0 0 0 0 0 0 1 0 0 0-1 0 0-1-1 0 0 0 0-1 0 0 0-2 0
 1-1 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0-1 0 0-1 0 1 0 0 0 0 0 0 0 0-3 0
 1 0 0 0 0 0-1-1 0 0 0-2 0 0 0 0-1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 0
-6 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0-1 0 0 0 0-1 0 0-1 0 0 0 0 6 0
 0 0-6 0 0 0 0 0 0 0 1-1 0 0 0 0 0 0 0 0 0-1 0 0 0 0 0-1 0 1 0 6 0
 0 0 0 0 0 6 0 0 0 1 0 0 0 0 0 0 0 0-1-1 0 0-1 0 0-1 0 0 0 0 0-3 0
""".replace("-"," -")

mat = [list(map(int,x.strip().split(" "))) for x in mat.strip().split("\n")]

f = [Int(f'{i}') for i in range(len(mat[0]))]
s=Solver()

for row in mat:
    s.add(sum((a*b for a,b in zip(f,row))) == 0)

# it is sufficient to either constrain to 0-256+flagformat, or 47-127 -- both will give you a unique solution :)
for x in f:
    s.add(x > 47)
    s.add(x <= 127)
s.add(roweq(f, map(ord, "oiccflag{")))
s.add(f[-1] == ord("}"))

def roweq(a,b):
    return And(*(x==y for x,y in zip(a,b)))

print(s.check())
m=s.model()

print("".join(chr(m[x].as_long()) for x in f))
```

Note that the theory of integers is used, rather than that of bitvectors. 64-sized BVs would be a truer reflection of the binary, but since the coefficients are so small, overflow is impossible, and z3 performs much better on this task with Ints than with 64-size BVs. (and the use of e.g. size-8 bitvectors could give false positives from overflow).

A full solution with disassembly parsing is in `solve.py`.
