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

#include <limits.h>
static int parse_count(const char *text, int *out) {
    if (text[0] < '0' || text[0] > '9') return -1;
    errno=0; char *end=NULL; long value=strtol(text,&end,10);
    if (errno == ERANGE || *end != '\0' || value < 1 || value > 1024) return -1;
    *out=(int)value; return 0;
}
int main(void) {
    int count=0;
    CHECK(parse_count("16",&count) == 0 && count == 16);
    const char *bad[]={"", "0", "-1", "16junk", "1025", "999999999999999999999999999"};
    for (size_t i=0;i<sizeof(bad)/sizeof(bad[0]);++i) CHECK(parse_count(bad[i],&count) == -1);
    puts("valid=16; empty, zero, negative, suffix, bound and overflow rejected");
    return 0;
}
