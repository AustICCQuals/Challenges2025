# The Dependency

The binary allows you to:
* Allocate a block of pointers, of chosen size (without checking whether malloc returns NULL...)
* Read 128 bytes from any of these pointers (including unitialized ones)
* Allocate a 128-byte buffer with chosen contents, and set any of the pointers to this buffer

Normally, this should be unexploitable: we can maybe get a leak by reading an
unitialized pointer, and we can request an oversized allocation, but this would
only let us write within the first 32 bits of memory space, which will never
contain anything of value with ASLR on.

# The Dependency is regmap

> some well-known and known-to-be-good computer architectures, such as the
> Microchip PIC product line, or many of the AVR processor family, were
> fortunate enough to have architects that understood the power of a strategic
> alignment between the processor's register file and main memory. on these
> architectures, the foresight to synergize register and memory accesses
> reduces instruction complexity: to load or store registers a developer only
> has to know the instructions to operate on memory.
> 
> unfortunately, the architects at Intel who designed the 8086 did not
> appreciate the learnings of these architectures and did not synergize the
> register file with main memory. regmap handles this design oversight by
> allowing users to memory-map the processor's general-purpose registers (GPR).

Thanks to `regmap`, memory accesses in the zero page of memory will hit a
SIGSEGV handler, which emulates the faulting instruction, making it behave as
if CPU registers are memory-mapped in this area!

The register layout can be seen in `src/regmap.rs:225`:

```rust
    match reg.num() {
        0 => { self.uc_mcontext.rax = value; },
        1 => { self.uc_mcontext.rcx = value; },
        2 => { self.uc_mcontext.rdx = value; },
        3 => { self.uc_mcontext.rbx = value; },
        4 => { self.uc_mcontext.rsp = value; },
        5 => { self.uc_mcontext.rbp = value; },
        6 => { self.uc_mcontext.rsi = value; },
        7 => { self.uc_mcontext.rdi = value; },
        8 => { self.uc_mcontext.r8 = value; },
        9 => { self.uc_mcontext.r9 = value; },
        10 => { self.uc_mcontext.r10 = value; },
        11 => { self.uc_mcontext.r11 = value; },
        12 => { self.uc_mcontext.r12 = value; },
        13 => { self.uc_mcontext.r13 = value; },
        14 => { self.uc_mcontext.r14 = value; },
        15 => { self.uc_mcontext.r15 = value; },
        _ => { unreachable!("sins"); }
    }
```

For example, we can read 128 bytes from rsp, like so:
```
How many objects would you like?
> -1
What would you like to do?
1. Create an object
2. Ponder an object
> 2
Which object?
> 4
The object speaks: 
┌─────────────────────────┬─────────────────────────┬────────┬────────┐
│ 10 4c 51 35 fd 7f 00 00 ┊ 00 00 00 00 00 00 00 00 │•LQ5×•⋄⋄┊⋄⋄⋄⋄⋄⋄⋄⋄│
│ 02 00 00 00 04 00 00 00 ┊ 00 35 e1 8e d7 9f 5d c6 │•⋄⋄⋄•⋄⋄⋄┊⋄5××××]×│
│ a8 4d 51 35 fd 7f 00 00 ┊ ff ff ff ff ff ff ff ff │×MQ5×•⋄⋄┊××××××××│
│ 01 00 00 00 00 00 00 00 ┊ 00 00 00 00 00 00 00 00 │•⋄⋄⋄⋄⋄⋄⋄┊⋄⋄⋄⋄⋄⋄⋄⋄│
│ a8 4d 51 35 fd 7f 00 00 ┊ 00 60 62 27 72 7f 00 00 │×MQ5×•⋄⋄┊⋄`b'r•⋄⋄│
│ 78 9e 36 a3 51 56 00 00 ┊ 31 62 28 a3 51 56 00 00 │x×6×QV⋄⋄┊1b(×QV⋄⋄│
│ ff ff ff ff ff ff ff ff ┊ 00 35 e1 8e d7 9f 5d c6 │××××××××┊⋄5××××]×│
│ 98 4d 51 35 fd 7f 00 00 ┊ fc a1 22 27 72 7f 00 00 │×MQ5×•⋄⋄┊××"'r•⋄⋄│
└─────────────────────────┴─────────────────────────┴────────┴────────┘
```

The leakable buffer at rsp contains a libc leak, a main binary leak, a heap
leak, and a stack cookie leak - anything a budding Remote Code Executor could wish for.

We can similarly set $rsp to a buffer we control. There are presumably several
solutions from this point, but mine is to replace offsets
0x58-0x70 in the leaked stack with a 3-word ropchain:

* pop rdi; ret (from libc)
* address of "/bin/sh\0" in libc
* address of execv in libc
