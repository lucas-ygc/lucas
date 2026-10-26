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
    int *value = mmap(NULL, sizeof(*value), PROT_READ | PROT_WRITE,
                      MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    CHECK(value != MAP_FAILED); *value=0;
    pid_t child=fork(); CHECK(child >= 0);
    if (child == 0) { *value=42; _exit(0); }
    int status=0; CHECK(waitpid(child,&status,0) == child);
    CHECK(WIFEXITED(status) && WEXITSTATUS(status) == 0 && *value == 42);
    CHECK(munmap(value,sizeof(*value)) == 0);
    puts("parent sees shared value=42 after child exit; no concurrent access");
    return 0;
}
