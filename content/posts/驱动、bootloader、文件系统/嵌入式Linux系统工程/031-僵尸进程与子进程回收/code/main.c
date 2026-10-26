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
    pid_t child = fork(); CHECK(child >= 0);
    if (child == 0) _exit(3);
    siginfo_t info = {0};
    CHECK(waitid(P_PID, (id_t)child, &info, WEXITED | WNOWAIT) == 0);
    CHECK(info.si_pid == child && info.si_code == CLD_EXITED && info.si_status == 3);
    puts("child exited; WNOWAIT deliberately leaves status available");
    int status = 0; CHECK(waitpid(child, &status, 0) == child);
    CHECK(WIFEXITED(status) && WEXITSTATUS(status) == 3);
    errno = 0; CHECK(waitpid(child, &status, WNOHANG) == -1 && errno == ECHILD);
    puts("reaped child; a second wait reports ECHILD");
    return 0;
}
