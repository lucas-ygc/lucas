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

static volatile sig_atomic_t notified = 0;
static void notify(int signo) { (void)signo; notified = 1; }
int main(void) {
    struct sigaction action = {0}; action.sa_handler = notify;
    CHECK(sigemptyset(&action.sa_mask) == 0);
    CHECK(sigaction(SIGUSR1, &action, NULL) == 0);
    CHECK(raise(SIGUSR1) == 0);
    CHECK(notified == 1);
    puts("SIGUSR1 handled; main performs output and cleanup");
    return 0;
}
