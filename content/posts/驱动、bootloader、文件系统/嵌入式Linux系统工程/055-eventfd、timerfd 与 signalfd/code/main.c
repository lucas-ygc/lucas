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

#include <sys/eventfd.h>
#include <sys/timerfd.h>
#include <poll.h>
int main(void) {
    int fd=eventfd(0,EFD_CLOEXEC); CHECK(fd >= 0);
    uint64_t a=2,b=3,sum=0;
    CHECK(write(fd,&a,sizeof(a)) == (ssize_t)sizeof(a));
    CHECK(write(fd,&b,sizeof(b)) == (ssize_t)sizeof(b));
    CHECK(read(fd,&sum,sizeof(sum)) == (ssize_t)sizeof(sum) && sum == 5);
    CHECK(close(fd) == 0);
    int timer=timerfd_create(CLOCK_MONOTONIC,TFD_CLOEXEC); CHECK(timer >= 0);
    struct itimerspec spec={0}; spec.it_value.tv_nsec=1000000;
    CHECK(timerfd_settime(timer,0,&spec,NULL) == 0);
    struct pollfd watch={.fd=timer,.events=POLLIN};
    CHECK(poll(&watch,1,2000) == 1 && (watch.revents & POLLIN));
    CHECK(read(timer,&sum,sizeof(sum)) == (ssize_t)sizeof(sum) && sum == 1);
    CHECK(close(timer) == 0);
    puts("eventfd sum=5; one-shot timerfd expirations=1");
    return 0;
}
