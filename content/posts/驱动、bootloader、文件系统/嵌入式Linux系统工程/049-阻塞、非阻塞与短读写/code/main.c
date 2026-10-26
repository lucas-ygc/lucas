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
    int p[2]; CHECK(pipe2(p, O_NONBLOCK | O_CLOEXEC) == 0);
    char buf[8]; errno=0;
    CHECK(read(p[0], buf, sizeof(buf)) == -1 && errno == EAGAIN);
    CHECK(write(p[1], "abc", 3) == 3);
    CHECK(read(p[0], buf, sizeof(buf)) == 3 && memcmp(buf,"abc",3) == 0);
    CHECK(close(p[1]) == 0);
    CHECK(read(p[0], buf, sizeof(buf)) == 0); CHECK(close(p[0]) == 0);
    puts("empty=EAGAIN; read=3 bytes; all writers closed=EOF");
    return 0;
}
