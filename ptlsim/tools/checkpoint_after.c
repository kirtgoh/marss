/*
 * checkpoint_after.c
 *
 * Create a checkpoint after Specifiec amount of user-level-instructions.
 *
 * Usage: ./checkpoint_after N CHK_NAME
 *        N            Number of user-level-instructions to fast-forward
 *        CHK_NAME     Name of checkpoint
 *
 * To change instruction counting from user level to all, in line 36 change
 * -fast-fwd-user-insns to -fast-fwd-insns
 */

#include "ptlcalls.h"
#include <stdio.h>

int main(int argc, char **argv) {
    char* commands[2];
    char fast_fwd[128];
    char fast_fwd_chk[128];

    bzero(fast_fwd, 128);
    bzero(fast_fwd_chk, 128);


    if (argc != 3) {
        printf("Please provide following 2 arguments:\n");
        printf("Usage: ./checkpoint_after N CHK_NAME\n");
        printf("\tN : Number of user-instructions to fast-forward\n");
        printf("\tCHK_NAME : Name of checkpoint after fast-forwarding\n");
        return -1; 
    }   

    printf("Creating checkpoint %s after %s instructions.\n", argv[2], argv[1]);

    snprintf(fast_fwd, sizeof(fast_fwd), "-fast-fwd-user-insns %s", argv[1]);
    snprintf(fast_fwd_chk, sizeof(fast_fwd_chk), "-fast-fwd-checkpoint %s",
            argv[2]);

    commands[0] = fast_fwd;
    commands[1] = fast_fwd_chk;

    int i;
    for (i=0; i < 2; i++) {
        printf("Command[%d]: %s\n", i, commands[i]);
    }   

    ptlcall_multi_flush(commands, 2); 
}