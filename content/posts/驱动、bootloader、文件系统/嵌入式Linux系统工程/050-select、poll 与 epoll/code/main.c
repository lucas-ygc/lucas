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

#include <poll.h>
int main(void) {
    int p[2]; CHECK(pipe(p) == 0);
    struct pollfd watch = {.fd=p[0], .events=POLLIN};
    CHECK(poll(&watch, 1, 0) == 0);
    CHECK(write(p[1], "x", 1) == 1);
    CHECK(poll(&watch, 1, 1000) == 1 && (watch.revents & POLLIN));
    char c=0; CHECK(read(p[0], &c, 1) == 1 && c == 'x');
    CHECK(close(p[0]) == 0); CHECK(close(p[1]) == 0);
    puts("empty poll=timeout; after write=POLLIN; consumed x");
    return 0;
}
