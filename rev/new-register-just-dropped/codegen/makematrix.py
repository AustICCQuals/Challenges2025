from z3 import *
import functools

flag_truth = list(map(ord,"oiccflag{b1nja_w0n7_54v3_y0u_n0w}"))

typ = lambda s: Int(s)

system = []
import random

def roweq(a,b):
    return And(*(x==y for x,y in zip(a,b)))

def rowtrue(a,b):
    return sum(c*x for c,x in zip(a,b)) == 0

def trygenrow():
    s = Solver()
    row = [typ(f'c_{len(system)}_{x}') for x in range(len(flag_truth))]

    for i in range(5):
        s.add(random.choice(row) != 0)
    #for x in row:
        #s.add(x!=0)

    for other in system:
        s.add(Not(roweq(row, other)))

    for c in row:
        s.add(And(c > -7, c < 7))

    s.add(rowtrue(row, flag_truth))
    if s.check() == sat:
        m=s.model()

        if len([x for x in row if m[x].as_long() !=0]) > 10:
            return None

        return [m[x].as_long() for x in row]
    return None

def genrow():
    while (x := trygenrow()) is None:
        pass
    return x

testsolver = Solver()

flag_try = [typ(f'f_{i}') for i in range(len(flag_truth))]

for f in flag_try:
    testsolver.add(f>47)
    #testsolver.add(f<256)
    testsolver.add(f<=127)

testsolver.add(Not(roweq(flag_try, flag_truth)))
#testsolver.add(roweq(flag_try, map(ord, "oiccflag{")))
#testsolver.add(flag_try[-1] == ord('}'))
def test(row):
    testsolver.add(rowtrue(flag_try, row))

    res = []


    #testsolver.push()
    #for tri,truth in zip(flag_try, flag_truth):
        #testsolver.add(tri==truth)
    #assert testsolver.check() == sat
    #testsolver.pop()
    #assert testsolver.check() == sat

    #testsolver.add(Not(roweq(flag_try, flag_truth)))
    res = testsolver.check() == unsat
    if not res:
        m=testsolver.model()
        #print("testsolver suggests:", "".join(chr(m[x].as_long()) for x in flag_try))
    return res

def singlesln(system):
    s=Solver()

    for f in flag_try:
        s.add(f>47)
        s.add(f<128)

    s.add(Not(roweq(flag_try, flag_truth)))
    #s.add(roweq(flag_try, map(ord, "oiccflag{")))
    #s.add(flag_try[-1] == ord('}'))
    for row in system:
        s.add(rowtrue(flag_try, row))

    res = s.check() == unsat
    if not res:
        m=s.model()
        print("testsolver suggests:", "".join(chr(m[x].as_long()) for x in flag_try))
    return res


def column(i):
    return [row[i] for row in system]

def culler(system):
    q = [system]

    while len(q) > 0:
        system = q.pop()
        for i in range(len(system)):
            attempt = system[:i] + system[i+1:]

            if singlesln(attempt):
                print("found", len(attempt), "------")
                for row in attempt:
                    print("".join([f"{x: 1d}" for x in row]))
                print("------")

                q.append(attempt)


while True:
    r = genrow()
    print("".join([f"{x: 1d}" for x in r]))
    system.append(r)

    for i in range(len(flag_truth)):
        if all(x==0 for x in column(i)):
            break
    else:
        #if test(r):
        if singlesln(system):
            #print("double checking...")
                
            for row in system:
                assert rowtrue(row,flag_truth)

            print(len(system))

            exit(0)
