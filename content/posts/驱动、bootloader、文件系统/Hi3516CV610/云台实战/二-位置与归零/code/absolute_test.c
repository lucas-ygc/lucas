#include <assert.h>
#include <stdio.h>
#include "ptz_motion.h"

static void finish(struct ptz_axis_position *p, const struct ptz_move *m)
{
    unsigned i;
    for (i = 0; i < m->steps; i++) assert(ptz_count_step(p, m->direction));
}
int main(void)
{
    struct ptz_axis_position p = {1000, 0, 1};
    struct ptz_move_to to = {0, 200, 2020};
    struct ptz_move m;
    assert(sizeof(to) == 16 && sizeof(struct ptz_travel) == 8 &&
           sizeof(struct ptz_travels) == 8);
    assert(ptz_plan_absolute(&p, 4039, &to, &m) == 0);
    assert(m.direction == 1 && m.steps == 1020);
    finish(&p, &m); assert(p.position == 2020);
    assert(ptz_plan_absolute(&p, 4039, &to, &m) == 0 && m.steps == 0);
    p.position = 3000;
    assert(ptz_plan_absolute(&p, 4039, &to, &m) == 0);
    assert(m.direction == -1 && m.steps == 980);
    finish(&p, &m); assert(p.position == 2020);
    p.positive_direction = -1; to.target = 0;
    assert(ptz_plan_absolute(&p, 4039, &to, &m) == 0 && m.direction == 1);
    finish(&p, &m); assert(p.position == 0);
    to.target = 4039;
    assert(ptz_plan_absolute(&p, 4039, &to, &m) == 0 && m.direction == -1);
    finish(&p, &m); assert(p.position == 4039);
    /* Replace a moving target using the position reached so far. */
    p.position = 2000; to.target = 3000;
    assert(!ptz_plan_absolute(&p, 4039, &to, &m));
    assert(ptz_count_step(&p, m.direction));
    to.target = 1000;
    assert(!ptz_plan_absolute(&p, 4039, &to, &m));
    assert(m.steps == 1001 && m.direction == 1);
    finish(&p, &m); assert(p.position == 1000);
    assert(!ptz_plan_absolute(&p, 4039, &to, &m)); /* no calibration gate */
    assert(ptz_plan_absolute(&p, 0, &to, &m) == -ENODATA);
    to.target = -1; assert(ptz_plan_absolute(&p, 4039, &to, &m) == -ERANGE);
    to.target = 4040; assert(ptz_plan_absolute(&p, 4039, &to, &m) == -ERANGE);
    to.target = PTZ_POSITION_MAX;
    assert(ptz_plan_absolute(&p, 4039, &to, &m) == -ERANGE);
    to.target = 0; p.position = PTZ_POSITION_MIN;
    assert(ptz_plan_absolute(&p, 4039, &to, &m) == -ERANGE);
    p.position = 1000; to.speed = 1;
    assert(ptz_plan_absolute(&p, 4039, &to, &m) == -ERANGE);
    to.speed = 0; assert(ptz_plan_absolute(&p, 4039, &to, &m) == -EINVAL);
    to.speed = 626; assert(ptz_plan_absolute(&p, 4039, &to, &m) == -EINVAL);
    to.speed = 200; to.axis = 2;
    assert(ptz_plan_absolute(&p, 4039, &to, &m) == -EINVAL);
    puts("PASS: absolute targets, polarity, retargeting, zero distance, no calibration gate/travel/bounds");
    return 0;
}
