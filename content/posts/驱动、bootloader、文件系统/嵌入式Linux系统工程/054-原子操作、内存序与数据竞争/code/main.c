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

#include <stdatomic.h>
static atomic_int count=0;
static void *worker(void *unused) {
    (void)unused;
    for (int i=0;i<10000;++i) atomic_fetch_add_explicit(&count,1,memory_order_relaxed);
    return NULL;
}
int main(void) {
    pthread_t a,b;
    CHECK(pthread_create(&a,NULL,worker,NULL) == 0);
    CHECK(pthread_create(&b,NULL,worker,NULL) == 0);
    CHECK(pthread_join(a,NULL) == 0); CHECK(pthread_join(b,NULL) == 0);
    CHECK(atomic_load(&count) == 20000);
    puts("atomic counter=20000 after joins; not a multi-field publication protocol");
    return 0;
}
