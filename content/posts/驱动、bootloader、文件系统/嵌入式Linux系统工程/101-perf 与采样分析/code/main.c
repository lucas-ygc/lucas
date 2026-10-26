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

static uint64_t workload(uint64_t iterations) {
    uint64_t value=1;
    for (uint64_t i=0;i<iterations;++i) value=value*UINT64_C(6364136223846793005)+1;
    return value;
}
int main(void) {
    uint64_t a=workload(1000000),b=workload(1000000);
    CHECK(a == b);
    printf("bounded CPU target checksum=%llu; perf not invoked by this runner\n",(unsigned long long)a);
    return 0;
}
