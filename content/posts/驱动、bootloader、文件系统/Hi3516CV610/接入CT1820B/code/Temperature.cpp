#include "Temperature.h"

#include <cerrno>
#include <cctype>
#include <cstdlib>
#include <fcntl.h>
#include <glob.h>
#include <unistd.h>

int TemperatureRead(int *temperatureMilliC)
{
    if (!temperatureMilliC)
        return -EINVAL;

    glob_t devices{};
    const int found = glob("/sys/bus/w1/devices/28-*/temperature", 0, nullptr, &devices);
    if (found != 0 || devices.gl_pathc != 1) {
        const int error = found == GLOB_NOMATCH ? ENODEV : found == GLOB_NOSPACE ? ENOMEM
                : found                                                          ? EIO
                                                                                 : EEXIST;
        globfree(&devices);
        return -error;
    }
    const int fd = open(devices.gl_pathv[0], O_RDONLY | O_CLOEXEC);
    const int openError = errno;
    globfree(&devices);
    if (fd < 0)
        return -openError;

    char text[64];
    // One sysfs read triggers one conversion. Do not retry EINTR implicitly.
    const ssize_t size = read(fd, text, sizeof(text) - 1);
    const int readError = errno;
    close(fd);
    if (size < 0)
        return -readError;
    if (size == 0 || size == sizeof(text) - 1)
        return -EIO;
    text[size] = '\0';
    errno = 0;
    char *end = nullptr;
    const long value = strtol(text, &end, 10);
    if (end == text || errno == ERANGE || value < -50000 || value > 150000)
        return -ERANGE;
    while (end < text + size && std::isspace(static_cast<unsigned char>(*end)))
        ++end;
    if (end != text + size)
        return -EIO;
    *temperatureMilliC = static_cast<int>(value);
    return 0;
}
