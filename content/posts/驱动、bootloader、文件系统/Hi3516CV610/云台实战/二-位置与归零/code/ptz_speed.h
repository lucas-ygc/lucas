#ifndef TL_PTZ_SPEED_H
#define TL_PTZ_SPEED_H

/* Constant half-step rates. Mechanical limits must be checked under load. */
#define PTZ_SPEED_LEVEL_MIN 1
#define PTZ_SPEED_LEVEL_MAX 5
static inline unsigned int ptz_speed_for_level(unsigned int level)
{
    static const unsigned int rates[PTZ_SPEED_LEVEL_MAX] = {100, 200, 300, 400, 500};
    if (level < PTZ_SPEED_LEVEL_MIN || level > PTZ_SPEED_LEVEL_MAX)
        return 0;
    return rates[level - 1];
}
#endif
