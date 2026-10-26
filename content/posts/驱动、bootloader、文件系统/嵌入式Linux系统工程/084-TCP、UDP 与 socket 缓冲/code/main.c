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

/* A deliberately fragmented stream: length prefix (big endian) plus body. */
int main(void) {
    const unsigned char wire[]={0,0,0,5,'h','e','l','l','o'};
    unsigned char received[sizeof(wire)]={0};
    const size_t fragments[]={2,3,1,3}; size_t offset=0;
    for (size_t i=0;i<sizeof(fragments)/sizeof(fragments[0]);++i) {
        CHECK(offset+fragments[i] <= sizeof(received));
        memcpy(received+offset,wire+offset,fragments[i]); offset+=fragments[i];
        if (offset < 4) continue;
        uint32_t length=((uint32_t)received[0]<<24)|((uint32_t)received[1]<<16)|
                        ((uint32_t)received[2]<<8)|received[3];
        CHECK(length <= sizeof(received)-4);
        if (offset < 4+length) continue;
        CHECK(length == 5 && memcmp(received+4,"hello",5) == 0);
    }
    CHECK(offset == sizeof(wire));
    puts("2/3/1/3-byte fragments reconstructed one bounded hello frame");
    return 0;
}
