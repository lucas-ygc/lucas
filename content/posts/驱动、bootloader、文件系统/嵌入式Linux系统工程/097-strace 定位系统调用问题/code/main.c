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
    int p[2]; CHECK(pipe(p) == 0);
    CHECK(write(p[1],"trace",5) == 5); CHECK(close(p[1]) == 0);
    char data[8]; CHECK(read(p[0],data,sizeof(data)) == 5);
    CHECK(read(p[0],data,sizeof(data)) == 0); CHECK(close(p[0]) == 0);
    puts("trace target: write=5, read=5, read=0");
    return 0;
}
