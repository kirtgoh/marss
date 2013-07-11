#include "ptlcalls.h"
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>

#include "sem_helper.h"

int main (int argc, char** argv)
{
	int sem_id;
	int sem_val;
	int rc;

    if (argc != 3) {
        printf("Please provide following 2 arguments:\n");
        printf("Usage: ./set_semaphore N CHK_NAME\n");
        printf("\tN : Number of threads to sync\n");
        printf("\tCHK_NAME : Name of checkpoint after sync\n");
        return -1; 
    }   
	
	/* Get semaphore */
	sem_id = get_semaphore();

	/* Retrive semaphore value from command line arg */
	sem_val = atoi(argv[1]);

	/* Set semaphore value */
	rc = set_semaphore(sem_id, sem_val);
	if (rc == -1) {
		perror("set_semaphore: semctl");
		return -1;
	}

	/* Now wait for semaphore to reach to 0 */
	wait_semaphore (sem_id);

	/* All threads will be in ROI so either create a checkpoint or 
	 * switch to simulation mode. */
	ptlcall_checkpoint_and_shutdown(argv[2]);

	return 0;
}
