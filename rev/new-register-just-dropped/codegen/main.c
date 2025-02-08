#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <cpuid.h>


int funny(char *);
void incorrect() {
	printf("incorrect\n");
	exit(1);
}
int main(char *argv, int argc) {

	unsigned int eax = 0;
	unsigned int ebx = 0;
	unsigned int ecx = 0;
	unsigned int edx = 0;

	if (!(__get_cpuid_count(7, 1, &eax, &ebx, &ecx, &edx)) || !(edx & bit_APX_F)) {
		printf("Please upgrade your CPU to run this program. If no suitable CPUs are available for purchase, consider hacking an Intel employee.\n");
		return 2;
	}

	char buf[34];
	fgets(buf, 34, stdin);

	for (int i = 0; i < 33; i++)
		if (!(buf[i] >= 48 && buf[i] <= 127))
			incorrect();

	if (memcmp(buf, "oiccflag{", 9) == 0 && buf[32] == '}') {
		funny(buf);
		printf("correct\n");
		return 0;
	}
	incorrect();
}
