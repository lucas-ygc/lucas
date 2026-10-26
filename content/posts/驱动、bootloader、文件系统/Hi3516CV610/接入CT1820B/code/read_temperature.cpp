#include "Temperature.h"
#include <cstdio>
#include <cstring>

int main()
{
    int temperatureMilliC = 0;
    const int rc = TemperatureRead(&temperatureMilliC);
    if (rc != 0) {
        std::fprintf(stderr, "TemperatureRead: %s (rc=%d)\n",
                     std::strerror(-rc), rc);
        return 1;
    }
    std::printf("%d mC, %.3f C\n", temperatureMilliC,
                temperatureMilliC / 1000.0);
    return 0;
}
