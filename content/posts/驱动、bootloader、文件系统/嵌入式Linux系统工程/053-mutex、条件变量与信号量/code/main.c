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

static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t changed = PTHREAD_COND_INITIALIZER;
static int ready=0, value=0;
static void *producer(void *unused) {
    (void)unused;
    CHECK(pthread_mutex_lock(&lock) == 0);
    value=42; ready=1;
    CHECK(pthread_cond_signal(&changed) == 0);
    CHECK(pthread_mutex_unlock(&lock) == 0);
    return NULL;
}
int main(void) {
    pthread_t worker; CHECK(pthread_create(&worker,NULL,producer,NULL) == 0);
    CHECK(pthread_mutex_lock(&lock) == 0);
    while (!ready) CHECK(pthread_cond_wait(&changed,&lock) == 0);
    CHECK(value == 42);
    CHECK(pthread_mutex_unlock(&lock) == 0);
    CHECK(pthread_join(worker,NULL) == 0);
    CHECK(pthread_cond_destroy(&changed) == 0);
    CHECK(pthread_mutex_destroy(&lock) == 0);
    puts("predicate checked under mutex; received value=42");
    return 0;
}
