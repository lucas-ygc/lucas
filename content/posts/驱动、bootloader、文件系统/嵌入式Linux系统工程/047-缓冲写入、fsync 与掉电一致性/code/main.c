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
    int fd = open("config.tmp", O_WRONLY | O_CREAT | O_EXCL, 0600); CHECK(fd >= 0);
    const char data[] = "version=2\n";
    CHECK(write(fd, data, sizeof(data)-1) == (ssize_t)(sizeof(data)-1));
    CHECK(fsync(fd) == 0); CHECK(close(fd) == 0);
    CHECK(rename("config.tmp", "config.txt") == 0);
    int dir = open(".", O_RDONLY | O_DIRECTORY); CHECK(dir >= 0);
    CHECK(fsync(dir) == 0); CHECK(close(dir) == 0);
    fd = open("config.txt", O_RDONLY); CHECK(fd >= 0);
    char result[sizeof(data)] = {0};
    CHECK(read(fd, result, sizeof(result)-1) == (ssize_t)(sizeof(data)-1));
    CHECK(strcmp(result, data) == 0); CHECK(close(fd) == 0);
    puts("file fsync -> rename -> directory fsync passed; no power-cut test");
    return 0;
}
