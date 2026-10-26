#ifndef TL_PTZ_MOTION_H
#define TL_PTZ_MOTION_H
#include "ptz_ioctl.h"
#ifdef __KERNEL__
#include <linux/errno.h>
#else
#include <errno.h>
#endif
/* Internal movement plan, not a user-space movement ioctl. */
struct ptz_move {
    __u32 axis;
    __s32 direction; /* +1 or -1; physical direction depends on phase wiring */
    __u32 speed;
    __u32 steps;
};
/* Four winding inputs, half-step sequence. Test actual phase order at low speed. */
static const unsigned char ptz_phases[8] = {1, 3, 2, 6, 4, 12, 8, 9};
static inline int ptz_valid_move(const struct ptz_move *m)
{
    return m->axis < PTZ_AXES && (m->direction == 1 || m->direction == -1) &&
           m->speed >= 1 && m->speed <= PTZ_MAX_SPEED && m->steps >= 1 &&
           m->steps <= m->speed * PTZ_MAX_SECONDS;
}
static inline unsigned int ptz_next_phase(unsigned int phase, int direction)
{
    return (phase + (direction > 0 ? 1 : 7)) & 7;
}
static inline int ptz_valid_position(const struct ptz_set_position *p)
{
    return p->axis < PTZ_AXES &&
           (p->positive_direction == 1 || p->positive_direction == -1);
}
#define PTZ_POSITION_MAX ((__s64)((~(__u64)0) >> 1))
#define PTZ_POSITION_MIN (-PTZ_POSITION_MAX - 1)
static inline int ptz_count_step(struct ptz_axis_position *p, int direction)
{
    int delta = direction == p->positive_direction ? 1 : -1;
    if ((delta > 0 && p->position == PTZ_POSITION_MAX) ||
        (delta < 0 && p->position == PTZ_POSITION_MIN))
        return 0;
    p->position += delta;
    return 1;
}
/* Plan from a snapshot protected by the driver's axis lock. No side effects. */
static inline int ptz_plan_absolute(const struct ptz_axis_position *p,
                                   __u32 max_steps, const struct ptz_move_to *to,
                                   struct ptz_move *m)
{
    __s64 distance;
    if (to->axis >= PTZ_AXES || !to->speed || to->speed > PTZ_MAX_SPEED)
        return -EINVAL;
    if (!max_steps)
        return -ENODATA;
    if (p->positive_direction != 1 && p->positive_direction != -1)
        return -EINVAL;
    if (p->position < 0 || p->position > max_steps ||
        to->target < 0 || to->target > max_steps)
        return -ERANGE;
    /* Both operands are in [0, UINT32_MAX], so signed 64-bit subtraction is safe. */
    distance = to->target - p->position;
    m->axis = to->axis;
    m->speed = to->speed;
    m->direction = distance < 0 ? -p->positive_direction : p->positive_direction;
    if (distance < 0) distance = -distance;
    if (distance > to->speed * PTZ_MAX_SECONDS)
        return -ERANGE;
    m->steps = distance;
    return 0;
}
#endif
