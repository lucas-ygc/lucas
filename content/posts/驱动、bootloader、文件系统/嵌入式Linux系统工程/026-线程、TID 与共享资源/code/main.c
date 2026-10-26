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

static void *worker(void *arg) {
    int *count = arg;
    for (int i=0; i<10000; ++i) ++*count;
    return NULL;
}
int main(void) {
    pthread_t threads[2]; int counts[2] = {0,0};
    for (int i=0; i<2; ++i) CHECK(pthread_create(&threads[i], NULL, worker, &counts[i]) == 0);
    for (int i=0; i<2; ++i) CHECK(pthread_join(threads[i], NULL) == 0);
    CHECK(counts[0] == 10000 && counts[1] == 10000);
    puts("joined two workers; each owns a separate counter: 10000,10000");
    return 0;
}
