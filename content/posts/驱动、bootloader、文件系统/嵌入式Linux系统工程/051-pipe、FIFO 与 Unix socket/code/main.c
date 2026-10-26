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

static void receive_exact(int fd, char *buffer, size_t length) {
    size_t done=0;
    while (done < length) {
        ssize_t n=read(fd, buffer+done, length-done);
        if (n < 0 && errno == EINTR) continue;
        CHECK(n > 0); done += (size_t)n;
    }
}
int main(void) {
    int pair[2]; CHECK(socketpair(AF_UNIX, SOCK_STREAM, 0, pair) == 0);
    CHECK(write(pair[0], "ping", 4) == 4);
    char data[4]; receive_exact(pair[1], data, 4); CHECK(memcmp(data,"ping",4) == 0);
    CHECK(write(pair[1], "pong", 4) == 4);
    receive_exact(pair[0], data, 4); CHECK(memcmp(data,"pong",4) == 0);
    CHECK(close(pair[0]) == 0); CHECK(close(pair[1]) == 0);
    puts("local socketpair: ping -> pong, no network connection");
    return 0;
}
