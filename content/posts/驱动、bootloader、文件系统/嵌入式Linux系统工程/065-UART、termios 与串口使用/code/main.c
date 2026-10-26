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

#include <termios.h>
#include <poll.h>
int main(void) {
    int master=posix_openpt(O_RDWR | O_NOCTTY); CHECK(master >= 0);
    CHECK(grantpt(master) == 0 && unlockpt(master) == 0);
    char *name=ptsname(master); CHECK(name != NULL);
    int slave=open(name,O_RDWR | O_NOCTTY); CHECK(slave >= 0);
    struct termios options; CHECK(tcgetattr(slave,&options) == 0);
    cfmakeraw(&options); CHECK(tcsetattr(slave,TCSANOW,&options) == 0);
    const unsigned char input[]={0,0x0a,0x7f,0xff};
    CHECK(write(master,input,sizeof(input)) == (ssize_t)sizeof(input));
    unsigned char output[sizeof(input)]; size_t offset=0;
    while (offset < sizeof(output)) {
        struct pollfd watch={.fd=slave,.events=POLLIN};
        CHECK(poll(&watch,1,1000) == 1 && (watch.revents & POLLIN));
        ssize_t n=read(slave,output+offset,sizeof(output)-offset);
        CHECK(n > 0); offset+=(size_t)n;
    }
    CHECK(memcmp(input,output,sizeof(input)) == 0);
    CHECK(close(slave) == 0 && close(master) == 0);
    puts("PTY raw bytes preserved: 00 0a 7f ff; no electrical UART test");
    return 0;
}
