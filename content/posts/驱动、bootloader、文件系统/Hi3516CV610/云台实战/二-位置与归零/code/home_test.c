/* Compile with -Wl,--wrap=ioctl. Exercise user-space sequencing and cancellation. */
#define main ptzctl_main
#include "ptzctl.c"
#undef main
#include <assert.h>
#include <stdarg.h>
static long long current;
static unsigned travel, moves, stops, calls, inject, fault;
static int stale;
int __wrap_ioctl(int fd, unsigned long cmd, ...)
{
    va_list args;
    void *p;
    (void)fd;
    va_start(args, cmd); p = va_arg(args, void *); va_end(args);
    calls++;
    if (inject && calls == inject) {
        if (fault == 1) { errno = EIO; return -1; }
        if (fault == 2) interrupted = 1;
        if (fault == 3) stale = 1;
    }
    if (stale && cmd != PTZ_STATUS && cmd != PTZ_GET_POSITION) {
        errno = ESTALE; return -1;
    }
    switch (cmd) {
    case PTZ_GUARD: break;
    case PTZ_STOP: stops++; break;
    case PTZ_SET_TRAVEL:
        travel = ((struct ptz_travel *)p)->max_steps;
        assert(current >= 0 && current <= travel);
        break;
    case PTZ_SET_POSITION:
        current = ((struct ptz_set_position *)p)->position;
        assert(current >= 0 && current <= travel);
        break;
    case PTZ_MOVE_TO: {
        const struct ptz_move_to *to = p;
        if (!moves) assert(current == 4200 && travel == 4200 && !to->target);
        else assert(moves == 1 && current == 0 && travel == 4039 && to->target == 2020);
        current = to->target; moves++;
        break;
    }
    case PTZ_STATUS:
        memset(p, 0, sizeof(struct ptz_status));
        ((struct ptz_status *)p)->axis[0].position = current;
        ((struct ptz_status *)p)->axis[0].superseded = stale;
        break;
    case PTZ_GET_POSITION:
        memset(p, 0, sizeof(struct ptz_positions));
        ((struct ptz_positions *)p)->axis[0].position = current;
        break;
    default: assert(0);
    }
    return 0;
}
static void reset(void)
{
    current = 100; travel = 4039;
    moves = stops = calls = 0;
    interrupted = stale = 0;
}
int main(void)
{
    struct ptz_home h = {0, 1, 4200, 4039};
    unsigned total, n;
    reset();
    assert(!run_home(1, &h, 100));
    assert(moves == 2 && current == 2020 && travel == 4039 && stops == 1);
    total = calls;
    /* Replacement at every ioctl boundary, including the zero-to-center gap,
     * must abort the old sequence and cannot stop a newer motion. */
    for (n = 1; n <= total; n++) {
        reset(); inject = n; fault = 3;
        assert(run_home(1, &h, 100) == -ESTALE);
        assert(stale && moves <= (n > 10 ? 2U : 1U));
        assert(stops == (n > 2 ? 1U : 0U));
    }
    reset(); inject = 6; fault = 1;
    assert(run_home(1, &h, 100) == -EIO && moves == 0 && stops == 2);
    reset(); inject = 5; fault = 2;
    assert(run_home(1, &h, 100) == -EINTR && moves == 0 && stops == 2);
    puts("PASS: user-space home, center, errors, interrupt, replacement at every ioctl boundary");
    return 0;
}
