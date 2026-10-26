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
    struct timespec start,finish,remaining={.tv_sec=0,.tv_nsec=10000000};
    CHECK(clock_gettime(CLOCK_MONOTONIC,&start) == 0);
    while (nanosleep(&remaining,&remaining) != 0) CHECK(errno == EINTR);
    CHECK(clock_gettime(CLOCK_MONOTONIC,&finish) == 0);
    double elapsed=(finish.tv_sec-start.tv_sec)*1000.0+(finish.tv_nsec-start.tv_nsec)/1000000.0;
    CHECK(elapsed >= 0);
    printf("requested sleep=10 ms; observed monotonic elapsed=%.3f ms\n",elapsed);
    return 0;
}
