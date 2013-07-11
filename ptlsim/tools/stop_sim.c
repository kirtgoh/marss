#include "ptlcalls.h"
#include <stdio.h>

int main() {

	printf("Stopping simulation\n");
	ptlcall_switch_to_native();
	return 0;
}
