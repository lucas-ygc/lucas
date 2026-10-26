/* Test the actual CLI parser without opening the motor device. */
#define main ptzctl_main
#include "ptzctl.c"
#undef main
#include <assert.h>
int main(void)
{
    struct ptz_move_to to;
    struct ptz_home home;
    unsigned speed;
    unsigned int i;
    char level[16];
    for (i = 1; i <= PTZ_SPEED_LEVEL_MAX; i++) {
        snprintf(level, sizeof(level), "%u", i);
        assert(parse_target(&to, 0, "64", level));
        assert(to.speed == i * 100 && to.target == 64);
    }
    assert(ptz_speed_for_level(0) == 0 && ptz_speed_for_level(~0U) == 0);
    assert(parse_target(&to, 0, "2020", "3") && to.target == 2020 && to.speed == 300);
    assert(parse_target(&to, 1, "0", "1") && to.target == 0);
    assert(!parse_target(&to, 0, "-1", "3"));
    assert(!parse_target(&to, 0, "2020", "6"));
    assert(!parse_target(&to, 0, "999999999999999999999999", "1"));
    assert(parse_home(&home, 0, "reverse", "4039", "4200", "1", &speed));
    assert(home.positive_direction == 1 && home.seek_steps == 4200 && speed == 100);
    assert(parse_home(&home, 1, "forward", "1024", "1100", "1", &speed));
    assert(home.positive_direction == -1);
    assert(!parse_home(&home, 0, "reverse", "4039", "4000", "1", &speed));
    assert(!parse_home(&home, 0, "reverse", "4039", "13000", "1", &speed));
    assert(!parse_home(&home, 0, "reverse", "-1", "4200", "1", &speed));
    assert(!parse_home(&home, 0, "reverse", "1", "64", "6", &speed));
    assert(!parse_home(&home, 0, "left", "1", "64", "1", &speed));
    assert(!parse_home(&home, 0, "reverse", "1", "-64", "1", &speed));
    puts("PASS: speed levels, absolute targets, user-space home parameters");
    return 0;
}
