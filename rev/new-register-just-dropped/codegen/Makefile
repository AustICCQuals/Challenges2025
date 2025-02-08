new-register-just-dropped: cool.s main.c
	gcc cool.s main.c -o $@
	strip $@
	patchelf --set-interpreter /lib64/ld-linux-x86-64.so.2 $@
	patchelf --remove-rpath $@

code.s: mat compile.py
	python3 compile.py > code.s

