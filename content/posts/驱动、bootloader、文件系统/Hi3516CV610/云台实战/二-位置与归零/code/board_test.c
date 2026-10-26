/* On-board regression test. Explicit --run required; moves each axis up to
 * 64 half-steps above its starting software position and returns by counting.
 * Requires both ranges configured and 64 steps of verified physical clearance.
 * No homing or reference-position writes. Failure stops both axes.
 */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <time.h>
#include <unistd.h>
#include "ptz_ioctl.h"
static int a = -1, b = -1;
static void delay_ms(long ms)
{
    struct timespec t = {ms / 1000, ms % 1000 * 1000000};
    while (nanosleep(&t, &t) && errno == EINTR) {}
}
static int move(int fd, unsigned axis, long long target, unsigned speed)
{
    struct ptz_move_to to = {axis, speed, target};
    return ioctl(fd, PTZ_MOVE_TO, &to);
}
static int idle(void)
{
    struct ptz_status s;
    unsigned n;
    for (n = 0; n < 200; n++) {
        if (ioctl(b, PTZ_STATUS, &s)) return -1;
        if (!s.axis[0].running && !s.axis[1].running) return 0;
        delay_ms(10);
    }
    return -1;
}
#define CHECK(x) do { if (!(x)) { fprintf(stderr, "FAIL line %d: %s (errno=%d)\n", __LINE__, #x, errno); goto fail; } } while (0)
int main(int argc, char **argv)
{
    struct ptz_status start, s, t;
    struct ptz_travels ranges;
    struct ptz_positions positions;
    struct ptz_travel range;
    struct ptz_set_position pos;
    /* Retired JOG ABI must return ENOTTY even when its payload is valid. */
    struct { __u32 axis; __s32 direction; __u32 speed, steps; } old_jog = {0, 1, 100, 8};
    __u32 mask = 3;
    unsigned level, cycle;
    if (argc != 2 || strcmp(argv[1], "--run")) {
        fprintf(stderr, "Usage: %s --run (physically moves both axes up to 64 half-steps)\n", argv[0]);
        return 2;
    }
    a = open("/dev/tuling_ptz", O_RDWR);
    b = open("/dev/tuling_ptz", O_RDWR);
    if (a < 0 || b < 0) { perror("open"); goto fail; }
    CHECK(!ioctl(b, PTZ_STATUS, &start));
    if (start.axis[0].running || start.axis[1].running) {
        puts("Already moving: no test commands issued"); close(a); close(b); return 2;
    }
    CHECK(!ioctl(b, PTZ_GET_TRAVEL, &ranges));
    CHECK(start.axis[0].position >= 0 && start.axis[1].position >= 0);
    CHECK(start.axis[0].position + 64 <= ranges.max_steps[0]);
    CHECK(start.axis[1].position + 64 <= ranges.max_steps[1]);
    CHECK(ioctl(b, _IOW('P', 9, old_jog), &old_jog) < 0 && errno == ENOTTY);
    CHECK(!ioctl(a, PTZ_GUARD, &mask));
    CHECK(!move(a, 0, start.axis[0].position + 64, 100));
    CHECK(!move(a, 1, start.axis[1].position + 64, 100));
    delay_ms(80);
    CHECK(!ioctl(a, PTZ_STATUS, &s));
    CHECK(s.axis[0].running && s.axis[1].running);
    CHECK(s.axis[0].done > 0 && s.axis[1].done > 0);
    range.axis = 1; range.max_steps = ranges.max_steps[1];
    pos.axis = 1; pos.position = start.axis[1].position; pos.positive_direction = 1;
    CHECK(ioctl(b, PTZ_SET_TRAVEL, &range) < 0 && errno == EBUSY);
    CHECK(ioctl(b, PTZ_SET_POSITION, &pos) < 0 && errno == EBUSY);
    CHECK(move(b, 0, (long long)ranges.max_steps[0] + 1, 100) < 0 && errno == ERANGE);
    CHECK(move(b, 1, -1, 100) < 0 && errno == ERANGE);
    CHECK(!ioctl(a, PTZ_STATUS, &t));
    CHECK(!t.axis[0].superseded && !t.axis[1].superseded);
    CHECK(t.axis[0].generation == s.axis[0].generation);
    /* Another fd retargets H while both axes are moving. Only H guard expires. */
    CHECK(!move(b, 0, start.axis[0].position, 200));
    CHECK(!ioctl(a, PTZ_STATUS, &t));
    CHECK(t.axis[0].superseded && !t.axis[1].superseded);
    CHECK(!ioctl(a, PTZ_GET_POSITION, &positions));
    CHECK(!ioctl(a, PTZ_GET_TRAVEL, &ranges));
    mask = 1;
    CHECK(ioctl(a, PTZ_STOP, &mask) < 0 && errno == ESTALE);
    CHECK(move(a, 0, start.axis[0].position + 32, 100) < 0 && errno == ESTALE);
    /* Same fd can still retarget and stop V despite stale H. */
    CHECK(!move(a, 1, start.axis[1].position + 32, 200));
    delay_ms(20);
    mask = 2;
    CHECK(!ioctl(a, PTZ_STOP, &mask));
    CHECK(!ioctl(a, PTZ_STATUS, &s) && !s.axis[1].running);
    CHECK(!move(b, 1, start.axis[1].position, 100));
    CHECK(!idle());
    puts("PASS: per-axis guarded replacement, queries after replacement, unaffected V retarget/stop, bounds, busy configuration, retired JOG");
    /* Short repeated out-and-back runs at every speed level. Physical missed
     * steps cannot be detected without an external reference or observer. */
    for (level = 1; level <= 5; level++) {
        for (cycle = 0; cycle < 3; cycle++) {
            CHECK(!move(b, 0, start.axis[0].position + 32, level * 100));
            CHECK(!move(b, 1, start.axis[1].position + 32, level * 100));
            CHECK(!idle());
            CHECK(!ioctl(b, PTZ_STATUS, &s));
            CHECK(s.axis[0].position == start.axis[0].position + 32);
            CHECK(s.axis[1].position == start.axis[1].position + 32);
            CHECK(!move(b, 0, start.axis[0].position, level * 100));
            CHECK(!move(b, 1, start.axis[1].position, level * 100));
            CHECK(!idle());
            CHECK(!ioctl(b, PTZ_STATUS, &s));
            CHECK(s.axis[0].position == start.axis[0].position);
            CHECK(s.axis[1].position == start.axis[1].position);
        }
        printf("PASS: level=%u speed=%u, both axes 3 round trips of 32 half-steps\n", level, level * 100);
        fflush(stdout);
    }
    printf("FINAL H=%lld V=%lld, both stopped\n",
           (long long)s.axis[0].position, (long long)s.axis[1].position);
    close(a); close(b);
    return 0;
fail:
    mask = 3;
    if (b >= 0) { ioctl(b, PTZ_STOP, &mask); close(b); }
    if (a >= 0) close(a);
    return 1;
}
