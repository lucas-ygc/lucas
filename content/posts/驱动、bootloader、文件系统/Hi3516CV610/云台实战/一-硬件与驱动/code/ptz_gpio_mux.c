#define _FILE_OFFSET_BITS 64
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

/* Used only after ptz.sh has claimed the selected GPIOs and driven them low. */
int main(int argc, char **argv)
{
    const uintptr_t regs[2][4] = {
        {0x17940070, 0x17940078, 0x17940060, 0x17940074},
        {0x10260000, 0x17940058, 0x17940064, 0x1794005c}
    };
    int axis, fd;
    long page = sysconf(_SC_PAGESIZE);
    if (argc != 2 || (strcmp(argv[1], "h") && strcmp(argv[1], "v"))) return 2;
    if (page <= 0) return 1;
    axis = !strcmp(argv[1], "v");
    fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (fd < 0) { perror("/dev/mem"); return 1; }
    for (unsigned i = 0; i < 4; i++) {
        uintptr_t addr = regs[axis][i], base = addr / page * page;
        size_t size = addr - base + 4;
        void *map = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, (off_t)base);
        if (map == MAP_FAILED) { perror("mmap"); close(fd); return 1; }
        volatile uint32_t *reg = (volatile uint32_t *)((char *)map + addr - base);
        uint32_t wanted = *reg & ~UINT32_C(15);
        *reg = wanted;
        uint32_t actual = *reg;
        munmap(map, size);
        if (actual != wanted) { fprintf(stderr, "mux readback failed\n"); close(fd); return 1; }
    }
    close(fd);
    return 0;
}
