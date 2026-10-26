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
    FILE *file = tmpfile(); CHECK(file != NULL);
    int fd = fileno(file); CHECK(fd >= 0);
    CHECK(write(fd, "abc", 3) == 3); CHECK(lseek(fd, 0, SEEK_SET) == 0);
    int copy = dup(fd); CHECK(copy >= 0);
    char first=0,second=0;
    CHECK(read(fd, &first, 1) == 1); CHECK(read(copy, &second, 1) == 1);
    CHECK(first == 'a' && second == 'b');
    CHECK(close(copy) == 0); CHECK(fclose(file) == 0);
    puts("original=a, dup=b: shared open-file offset");
    return 0;
}
