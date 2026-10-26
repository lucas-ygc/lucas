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

static int copy_payload(char *dst,size_t capacity,const char *src,size_t length) {
    if (length >= capacity) return -1;
    memcpy(dst,src,length); dst[length]='\0'; return 0;
}
int main(void) {
    char target[8];
    CHECK(copy_payload(target,sizeof(target),"",0) == 0 && target[0] == '\0');
    CHECK(copy_payload(target,sizeof(target),"1234567",7) == 0);
    CHECK(strcmp(target,"1234567") == 0);
    CHECK(copy_payload(target,sizeof(target),"12345678",8) == -1);
    puts("empty, boundary and oversized input checked; no intentional invalid memory access");
    return 0;
}
