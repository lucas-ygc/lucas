#pragma once

#ifdef CONFIG_SENSOR_CT1820B
// Blocking read, millidegrees Celsius. Returns 0 or negative errno.
// Output is unchanged on failure. Exactly one CT1820B must be connected.
int TemperatureRead(int *temperatureMilliC);
#endif
