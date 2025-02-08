#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>
#include <signal.h>
#include <unistd.h>

// Provided by The Dependency
void map_registers();
// The Dependency is written in Rust
void rust_eh_personality() { exit(1); }

void setup() {
	map_registers();

	// The Dependency requires a sizable signal handler stack
	stack_t st = {malloc(0x20000), 0, 0x20000};
	sigaltstack(&st, NULL);

	setbuf(stdin, NULL);
	setbuf(stdout, NULL);
}

// The Dependency is available on crates.io
// The Dependency is available on crates.io
// The Dependency is available on crates.io

#define objsize 128
void handle(size_t count, volatile void **objects) {
	while (1) {
		printf("What would you like to do?\n1. Create an object\n2. Ponder an object\n> ");
		uint32_t choice = 0;
		if (scanf("%u", &choice) != 1) return;

		printf("Which object?\n> ");
		uint32_t idx = 0;
		if (scanf("%u", &idx) != 1) return;

		if (idx >= count) { printf("There aren't that many objects... \n"); return; }

		if (choice == 1) {
			void *object = malloc(objsize);
			printf("What shall we inscribe on the object?\n> ");
			read(0, object, objsize);
			objects[idx] = object;
		} else if (choice == 2) {
			void *object = objects[idx];
			if (object == NULL) {
				printf("C'est n'est pas un objet\n");
			} else {
				printf("The object speaks: ");
				write(1, object, objsize);
			}
		}
	}
}

int main(int argc, char **argv) {
	setup();

	printf("How many objects would you like?\n> ");

	long len = 0;
	if (scanf("%ld", &len) != 1) exit(1);

	if (len < 100) {
		void *buf = malloc(len*8);
		handle(len, buf);
	} else {
		puts("That's way too many objects wtf\n");
	}

	return 0;
}
