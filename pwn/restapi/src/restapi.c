#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include "restapi.h"

#define bufsz 102400

struct route {
	char *path;
	void *func;
	struct route *next;
};

struct route *routes_head;

void restapi_add_route(char *path, void *func) {
	struct route *seg;
       	seg = malloc(sizeof(*seg));

	seg->path = path;
	seg->func = func;
	seg->next = routes_head;
	routes_head = seg;
}

// To avoid strcopies, these strings are not null terminated, so recording lengths is useful here
struct path_segment {
	char *segment;
	uint16_t length;
};


// Turns a string like `/foo/bar/bazzz` into a heap-allocated array like:
// { "foo", 3 }, { "bar", 3 }, { "bazzz", 5 }
struct path_segment *split_path_segments(char *seg) {
       	struct path_segment *segs = malloc(sizeof(struct path_segment) * 256);
	memset(segs, 0, sizeof(struct path_segment) * 256);

	int8_t i = 0;

	segs[i++].segment = seg+1;

	while (1) {
		seg = strchr(seg+1, '/');
		if (!seg) break;

		// record the length of the previous one (now we know where this one starts)
		segs[i-1].length = seg - (segs[i-1].segment);

		// record the pointer of this segment
		segs[i++].segment = seg+1;
	}

	// record the length of the final segment, since it did not have a slash
	segs[i-1].length = strlen(segs[i-1].segment);

	return segs;
}


int sockfd, connfd;
char *buf;

void restapi_setup(int port) {
    int s;
    struct sockaddr_in addr;

    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = htonl(INADDR_ANY);

    s = socket(AF_INET, SOCK_STREAM, 0);
    if (s < 0) {
        perror("Unable to create socket");
        exit(EXIT_FAILURE);
    }
    int reuse = 1;
    setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));
    setsockopt(s, SOL_SOCKET, SO_REUSEPORT, &reuse, sizeof(reuse));

    if (bind(s, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("Unable to bind");
        exit(EXIT_FAILURE);
    }

    if (listen(s, 1) < 0) {
        perror("Unable to listen");
        exit(EXIT_FAILURE);
    }

    buf = malloc(bufsz);

    sockfd=s;
}

void call_func_with_args(void *func, intptr_t *args, int argc) {
	// who the fuck is screaming "READ X86_64-ABI-0.99.PDF" at my house.
	// show yourself, coward. i will never read x86_64-abi-0.99.pdf

	switch (argc) {
		case 0: ((void (*)(                                                )) func)();                                            break;
		case 1: ((void (*)(intptr_t                                        )) func)(args[0]);                                     break;
		case 2: ((void (*)(intptr_t, intptr_t                              )) func)(args[0], args[1]);                            break;
		case 3: ((void (*)(intptr_t, intptr_t, intptr_t                    )) func)(args[0], args[1], args[2]);                   break;
		case 4: ((void (*)(intptr_t, intptr_t, intptr_t, intptr_t          )) func)(args[0], args[1], args[2], args[3]);          break;
		case 5: ((void (*)(intptr_t, intptr_t, intptr_t, intptr_t, intptr_t)) func)(args[0], args[1], args[2], args[3], args[4]); break;
	}
}


void route_request(char *req_path) {
	struct path_segment *req_segs = split_path_segments(req_path);
	struct route *candidate_route = routes_head;

	while (candidate_route != NULL) {
		struct path_segment *candidate_segs = split_path_segments(candidate_route->path);
		
		intptr_t args[5] = { 0 };
		int argc = 0;

		for (int i = 0; i<256; i++) {
			if (candidate_segs[i].segment == NULL && req_segs[i].segment == NULL) {
				// reached the end with both segments being the same length - it's a match.
				
				free(req_segs);
				free(candidate_segs);
				call_func_with_args(candidate_route->func, args, argc);
				return;
			}

			if (candidate_segs[i].segment == NULL || req_segs[i].segment == NULL) {
				// The paths have different segment counts, move on to the next route.
				break;
			}

			if (candidate_segs[i].segment[0] == '$') {
				// This path segment contains arguments
				if (candidate_segs[i].length == strlen("$string") && memcmp(candidate_segs[i].segment, "$string", candidate_segs[i].length) == 0) {
					// Need to heap-allocate this arg so we can null-terminate it
					char *str = malloc(req_segs[i].length+1);
					memcpy(str, req_segs[i].segment, req_segs[i].length);
					str[req_segs[i].length] = '\0';

					args[argc++] = (intptr_t) str;
				} else if (candidate_segs[i].length == strlen("$num") && memcmp(candidate_segs[i].segment, "$num", candidate_segs[i].length) == 0) {
					args[argc++] = atol(req_segs[i].segment);
				}
			} else {
				if (candidate_segs[i].length != req_segs[i].length) break;
				if (memcmp(candidate_segs[i].segment, req_segs[i].segment, req_segs[i].length) != 0) break;
			}
		}

		candidate_route = candidate_route->next;

		free(candidate_segs);
	}

	free(req_segs);
	// No matching route found
	restapi_respond(404, "nah cant find that one, sorry");
}

void restapi_respond(int statuscode, char *content) {
	dprintf(connfd, "HTTP/1.1 %d\r\nContent-Length: %ld\r\n\r\n%s", statuscode, strlen(content), content);
	close(connfd);
}


void restapi_run() {
	while (1) {
		memset(buf, 0, bufsz);

		connfd = accept(sockfd, NULL, NULL);

		int amount_read = 0;
		while (strchr(buf, '\n') == NULL && amount_read<bufsz) {
			int r = read(connfd, buf+amount_read, bufsz-amount_read);
			if (r < 1 && strchr(buf, '\n') == NULL) {
				close(connfd); continue;
				restapi_respond(400, "bad request"); continue;
			}

			amount_read += r;
		}

		// first http line is e.g. `GET /path/to/endpoint HTTP/1.1`
		char *before_path = strchr(buf, ' ');
		if (before_path == NULL || before_path >= buf+bufsz) {
		       	restapi_respond(400, "bad request"); continue; 
		}

		char *after_path = strchr(before_path+1, ' ');
		if (after_path == NULL || after_path >= buf+bufsz) {
		       	restapi_respond(400, "bad request"); continue; 
		}

		*after_path = '\0';

		route_request(before_path+1);
	}
}
