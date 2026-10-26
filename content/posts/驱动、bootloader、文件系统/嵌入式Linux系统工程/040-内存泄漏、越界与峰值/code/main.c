#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define CHECK(x) do { if (!(x)) { fprintf(stderr, "check failed: %s at line %d (errno=%d)\n", #x, __LINE__, errno); exit(EXIT_FAILURE); } } while (0)

int main(void) {
    size_t live=0,peak=0;
    for (int cycle=0;cycle<20;++cycle) {
        void *frames[4]={0};
        for (int i=0;i<4;++i) {
            frames[i]=malloc(4096); CHECK(frames[i] != NULL);
            memset(frames[i],cycle,4096); ++live;
            if (live>peak) peak=live;
        }
        for (int i=0;i<4;++i) { free(frames[i]); frames[i]=NULL; --live; }
        CHECK(live == 0);
    }
    CHECK(peak == 4);
    puts("20 bounded cycles: live objects return to 0; peak=4, independent of RSS retention");
    return 0;
}
