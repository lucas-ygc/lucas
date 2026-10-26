#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <time.h>
#include <unistd.h>
#include "ptz_motion.h"
#include "ptz_speed.h"
/* Calibration belongs only to this user-space helper. */
struct ptz_home {
    unsigned axis;
    int positive_direction;
    unsigned seek_steps, max_steps;
};
static volatile sig_atomic_t interrupted;
static void signal_stop(int sig) { (void)sig; interrupted = 1; }
static int number(const char *s, long *value)
{
    char *end;
    errno = 0; *value = strtol(s, &end, 10);
    return !errno && *s && !*end;
}
static void print_status(const struct ptz_status *s)
{
    unsigned i;
    for (i = 0; i < PTZ_AXES; i++)
        printf("%c: running=%u direction=%d speed=%u done=%u remaining=%u position=%lld target=%lld generation=%llu superseded=%u\n",
               i ? 'V' : 'H', s->axis[i].running, s->axis[i].direction,
               s->axis[i].speed, s->axis[i].done, s->axis[i].remaining,
               (long long)s->axis[i].position, (long long)s->axis[i].target,
               (unsigned long long)s->axis[i].generation, s->axis[i].superseded);
}
static int print_positions(int fd)
{
    struct ptz_positions p;
    unsigned i;
    if (ioctl(fd, PTZ_GET_POSITION, &p)) { perror("position"); return 1; }
    for (i = 0; i < PTZ_AXES; i++)
        printf("%c: position=%lld positive_direction=%d\n",
               i ? 'V' : 'H', (long long)p.axis[i].position,
               p.axis[i].positive_direction);
    return 0;
}
static int parse_target(struct ptz_move_to *to, unsigned axis,
                        const char *target, const char *level)
{
    char *end;
    long rate;
    long long value;
    errno = 0;
    value = strtoll(target, &end, 10);
    if (errno || !*target || *end || value < 0 ||
        !number(level, &rate) || rate < PTZ_SPEED_LEVEL_MIN ||
        rate > PTZ_SPEED_LEVEL_MAX) return 0;
    to->axis = axis;
    to->target = value;
    to->speed = ptz_speed_for_level((unsigned int)rate);
    return 1;
}
static int print_travels(int fd)
{
    struct ptz_travels travel;
    unsigned i;
    if (ioctl(fd, PTZ_GET_TRAVEL, &travel)) { perror("travel"); return 1; }
    for (i = 0; i < PTZ_AXES; i++)
        printf("%c: max_steps=%u configured=%u\n", i ? 'V' : 'H',
               travel.max_steps[i], travel.max_steps[i] != 0);
    return 0;
}
static int parse_home(struct ptz_home *h, unsigned axis, const char *toward_zero,
                      const char *travel, const char *seek, const char *level,
                      unsigned *speed)
{
    long max_steps, seek_steps, rate;
    if (axis >= PTZ_AXES ||
        !number(travel, &max_steps) || max_steps < 1 || max_steps > 75000 ||
        !number(seek, &seek_steps) || seek_steps < max_steps || seek_steps > 75000 ||
        !number(level, &rate) || rate < PTZ_SPEED_LEVEL_MIN ||
        rate > PTZ_SPEED_LEVEL_MAX ||
        (strcmp(toward_zero, "forward") && strcmp(toward_zero, "reverse")))
        return 0;
    *speed = ptz_speed_for_level(rate);
    if ((unsigned long)seek_steps > *speed * PTZ_MAX_SECONDS) return 0;
    h->axis = axis;
    h->positive_direction = !strcmp(toward_zero, "forward") ? -1 : 1;
    h->seek_steps = seek_steps;
    h->max_steps = max_steps;
    return 1;
}
static int wait_target(int fd, unsigned axis, long long target)
{
    struct timespec start, now;
    const struct timespec delay = {0, 20000000};
    struct ptz_status state;
    if (clock_gettime(CLOCK_MONOTONIC, &start)) return -errno;
    for (;;) {
        if (interrupted) return -EINTR;
        if (ioctl(fd, PTZ_STATUS, &state)) return -errno;
        if (state.axis[axis].superseded) return -ESTALE;
        if (!state.axis[axis].running) {
            return state.axis[axis].position == target ? 0 : -ECANCELED;
        }
        if (clock_gettime(CLOCK_MONOTONIC, &now)) return -errno;
        if (now.tv_sec - start.tv_sec > PTZ_MAX_SECONDS + 10) return -ETIMEDOUT;
        nanosleep(&delay, NULL);
    }
}
static int run_home(int fd, const struct ptz_home *h, unsigned speed)
{
    struct ptz_move_to to = {h->axis, speed, 0};
    __u32 axis = h->axis, mask = 1U << axis;
    int rc;
    if (interrupted) return -EINTR;
    struct ptz_set_position position = {axis, h->positive_direction, 0};
    struct ptz_travel travel = {axis, h->seek_steps};
    /* A newer command from any other fd cancels this entire sequence.
     * Guarded cleanup then cannot accidentally stop that newer motion. */
    if (ioctl(fd, PTZ_GUARD, &mask)) return -errno;
    if (ioctl(fd, PTZ_STOP, &mask)) return -errno;
    if (ioctl(fd, PTZ_SET_POSITION, &position) ||
        ioctl(fd, PTZ_SET_TRAVEL, &travel)) { rc = -errno; goto fail; }
    position.position = h->seek_steps;
    if (ioctl(fd, PTZ_SET_POSITION, &position)) { rc = -errno; goto fail; }
    printf("%c: homing from assumed position %u to 0\n", axis ? 'V' : 'H', h->seek_steps);
    fflush(stdout);
    if (interrupted) { rc = -EINTR; goto fail; }
    if (ioctl(fd, PTZ_MOVE_TO, &to)) { rc = -errno; goto fail; }
    rc = wait_target(fd, axis, 0);
    if (rc) goto fail;
    if (interrupted) { rc = -EINTR; goto fail; }
    position.position = 0;
    travel.max_steps = h->max_steps;
    if (ioctl(fd, PTZ_SET_POSITION, &position) ||
        ioctl(fd, PTZ_SET_TRAVEL, &travel)) { rc = -errno; goto fail; }
    to.target = (h->max_steps + 1U) / 2U;
    printf("%c: zero reference set, moving to center %lld\n", axis ? 'V' : 'H',
           (long long)to.target);
    fflush(stdout);
    if (interrupted) { rc = -EINTR; goto fail; }
    if (ioctl(fd, PTZ_MOVE_TO, &to)) { rc = -errno; goto fail; }
    rc = wait_target(fd, axis, to.target);
    if (!rc) return 0;
fail:
    ioctl(fd, PTZ_STOP, &mask);
    return rc;
}
int main(int argc, char **argv)
{
    struct ptz_status state;
    unsigned count = 0, i;
    __u32 mask = 3;
    int stop = 0, fd, ret = 0;
    int position_command = 0;
    struct ptz_set_position position = {0};
    int travel_command = 0, absolute = 0;
    struct ptz_travel travel = {0};
    struct ptz_move_to to = {0};
    int home_command = 0;
    struct ptz_home home = {0};
    unsigned home_speed = 0;
    if (argc == 2 && strcmp(argv[1], "levels") == 0) {
        for (i = PTZ_SPEED_LEVEL_MIN; i <= PTZ_SPEED_LEVEL_MAX; i++)
            printf("level=%u speed=%u half-steps/s\n", i, ptz_speed_for_level(i));
        return 0;
    }
    if (argc == 2 && strcmp(argv[1], "status") == 0) {}
    else if (argc == 7 && !strcmp(argv[1], "home") &&
             (!strcmp(argv[2], "h") || !strcmp(argv[2], "v"))) {
        if (!parse_home(&home, !strcmp(argv[2], "v"), argv[3], argv[4], argv[5], argv[6],
                        &home_speed)) goto usage;
        home_command = 1;
    }
    else if (argc == 2 && !strcmp(argv[1], "travel")) travel_command = 1;
    else if (argc == 4 && !strcmp(argv[1], "set-travel") &&
             (!strcmp(argv[2], "h") || !strcmp(argv[2], "v"))) {
        char *end;
        long long value;
        errno = 0;
        value = strtoll(argv[3], &end, 10);
        if (errno || !*argv[3] || *end || value < 1 || value > 4294967295LL)
            goto usage;
        travel.axis = !strcmp(argv[2], "v");
        travel.max_steps = value;
        travel_command = 2;
    }
    else if (argc == 5 && !strcmp(argv[1], "move-to") &&
             (!strcmp(argv[2], "h") || !strcmp(argv[2], "v"))) {
        if (!parse_target(&to, !strcmp(argv[2], "v"), argv[3], argv[4])) goto usage;
        absolute = 1;
        count = 1;
    }
    else if (argc == 2 && strcmp(argv[1], "position") == 0) position_command = 1;
    else if (argc == 5 && !strcmp(argv[1], "set-position") &&
             (!strcmp(argv[2], "h") || !strcmp(argv[2], "v"))) {
        char *end;
        long direction;
        long long value;
        errno = 0;
        value = strtoll(argv[3], &end, 10);
        if (errno || !*argv[3] || *end || !number(argv[4], &direction) ||
            (direction != 1 && direction != -1)) goto usage;
        position.axis = !strcmp(argv[2], "v");
        position.position = value;
        position.positive_direction = direction;
        position_command = 2;
    }
    else if ((argc == 2 || argc == 3) && !strcmp(argv[1], "stop")) {
        if (argc == 3) {
            if (!strcmp(argv[2], "h")) mask = 1;
            else if (!strcmp(argv[2], "v")) mask = 2;
            else if (strcmp(argv[2], "all")) goto usage;
        }
        stop = 1;
    }
    else goto usage;
    signal(SIGINT, signal_stop); signal(SIGTERM, signal_stop);
    fd = open("/dev/tuling_ptz", O_RDWR | O_CLOEXEC);
    if (fd < 0) { perror("/dev/tuling_ptz"); return 1; }
    if (home_command) {
        int rc = run_home(fd, &home, home_speed);
        if (rc) {
            if (rc == -ESTALE)
                fprintf(stderr, "home canceled: replaced by a newer command\n");
            else
                fprintf(stderr, "home failed: %s (%d)\n", strerror(-rc), rc);
            ret = 1;
        } else ret = print_positions(fd);
        goto out;
    }
    if (travel_command) {
        if (travel_command == 2 && ioctl(fd, PTZ_SET_TRAVEL, &travel)) {
            perror("set-travel"); ret = 1; goto out;
        }
        ret = print_travels(fd);
        goto out;
    }
    if (position_command) {
        if (position_command == 2 && ioctl(fd, PTZ_SET_POSITION, &position)) {
            perror("set-position"); ret = 1; goto out;
        }
        ret = print_positions(fd);
        goto out;
    }
    if (stop && ioctl(fd, PTZ_STOP, &mask)) { perror("stop"); ret = 1; goto out; }
    if (count) {
        if (interrupted) goto out;
        if (ioctl(fd, PTZ_MOVE_TO, &to)) {
            perror("move-to"); ret = 1; goto out;
        }
    }
    if (ioctl(fd, PTZ_STATUS, &state)) { perror("status"); ret = 1; goto out; }
    print_status(&state);
    if (absolute) ret = print_positions(fd);
out:
    close(fd); /* Submitted movement continues; use stop to cancel it. */
    return interrupted ? 130 : ret;
usage:
    fprintf(stderr, "Usage: %s status | stop [h|v|all]\n"
            "       %s levels\n"
            "       %s position\n"
            "       %s set-position h|v POSITION POSITIVE_DIRECTION(+1|-1)\n"
            "       %s travel | set-travel h|v MAX_STEPS\n"
            "       %s move-to h|v TARGET_POSITION LEVEL\n"
            "       %s home h|v forward|reverse TRAVEL SEEK_STEPS LEVEL\n"
            "move-to returns immediately; use status/stop to query/cancel.\n"
            "home: direction is TOWARD the mechanical zero; seeks zero then centers.\n"
            "Levels 1..5: 100,200,300,400,500 half-steps/s (constant speed).\n"
            "Targets must be nonnegative; all movement is range checked.\n",
            argv[0], argv[0], argv[0], argv[0], argv[0], argv[0], argv[0]);
    return 2;
}
