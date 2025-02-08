#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "restapi.h"

void handle_greet() {
	restapi_respond(200, "hey wassup");
}

void handle_greet_name(char *name) {
	char reply[0x200];
	snprintf(reply, 0x200, "woah, it's %s!", name);
	restapi_respond(200, reply);

	// string arguments are heap-allocated, and it is the handler's responsibilty to free them
	free(name);
}

void handle_add(uint64_t a, uint64_t b) {
	char reply[0x200];
	snprintf(reply, 0x200, "%ld + %ld = %ld", a, b, a+b);
	restapi_respond(200, reply);
}


int main(int argc, char **argv) {
	if (argc != 2) exit(1);

	restapi_setup(atoi(argv[1]));

	restapi_add_route("/greet",                    handle_greet);
	restapi_add_route("/greet/$string",            handle_greet_name);
	restapi_add_route("/calculate/$num/plus/$num", handle_add);

	restapi_run();
}
