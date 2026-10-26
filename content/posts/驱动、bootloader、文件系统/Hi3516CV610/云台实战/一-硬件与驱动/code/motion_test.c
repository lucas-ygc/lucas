#include <assert.h>
#include <stdio.h>
#include "ptz_motion.h"
int main(void)
{
    struct ptz_move m = {0, 1, 100, 20};
    unsigned p, i, rate;
    struct ptz_set_position origin = {0, 1, 0};
    struct ptz_axis_position position = {0, 0, 1};
    assert(sizeof(m) == 16 && sizeof(struct ptz_status) == 96);
    assert(sizeof(origin) == 16 && sizeof(struct ptz_positions) == 32);
    assert(ptz_valid_position(&origin));
    origin.axis = 2; assert(!ptz_valid_position(&origin)); origin.axis = 1;
    origin.positive_direction = 0; assert(!ptz_valid_position(&origin));
    origin.positive_direction = -1; assert(ptz_valid_position(&origin));
    for (i = 0; i < 64; i++) assert(ptz_count_step(&position, 1));
    assert(position.position == 64);
    for (i = 0; i < 64; i++) assert(ptz_count_step(&position, -1));
    assert(position.position == 0);
    position.positive_direction = -1;
    assert(ptz_count_step(&position, -1) && position.position == 1);
    position.position = PTZ_POSITION_MAX;
    assert(!ptz_count_step(&position, -1) && position.position == PTZ_POSITION_MAX);
    assert(ptz_count_step(&position, 1) && position.position == PTZ_POSITION_MAX - 1);
    position.position = PTZ_POSITION_MIN;
    assert(!ptz_count_step(&position, 1) && position.position == PTZ_POSITION_MIN);
    assert(ptz_count_step(&position, -1) && position.position == PTZ_POSITION_MIN + 1);
    assert(ptz_valid_move(&m));
    m.axis = 2; assert(!ptz_valid_move(&m)); m.axis = 1;
    m.direction = 0; assert(!ptz_valid_move(&m)); m.direction = -1;
    for (rate = 1; rate <= PTZ_MAX_SPEED; rate++) {
        m.speed = rate; m.steps = rate * PTZ_MAX_SECONDS;
        assert(ptz_valid_move(&m)); m.steps++; assert(!ptz_valid_move(&m));
    }
    m.steps = 1; m.speed = 0; assert(!ptz_valid_move(&m));
    m.speed = PTZ_MAX_SPEED + 1; assert(!ptz_valid_move(&m));
    m.speed = 100; m.steps = 0; assert(!ptz_valid_move(&m));
    m.steps = ~0U; assert(!ptz_valid_move(&m));
    for (p = 0; p < 8; p++) {
        unsigned f = p, r = p;
        assert(ptz_next_phase(ptz_next_phase(p, 1), -1) == p);
        for (i = 0; i < 8; i++) {
            unsigned n = ptz_next_phase(f, 1);
            unsigned change = ptz_phases[f] ^ ptz_phases[n];
            assert(change && !(change & (change - 1))); /* one winding changes */
            f = n; r = ptz_next_phase(r, -1);
        }
        assert(f == p && r == p);
    }
    puts("PASS: ABI sizes, position counting/polarity/overflow, move limits, phase continuity");
    return 0;
}
