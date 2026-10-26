#ifndef TL_PTZ_IOCTL_H
#define TL_PTZ_IOCTL_H
#include <linux/types.h>
#include <linux/ioctl.h>
#define PTZ_AXES 2
#define PTZ_MAX_SPEED 625 /* 单位：半步/秒；机械速度上限仍需实测 */
#define PTZ_MAX_SECONDS 120
struct ptz_axis_status {
    __u32 running;
    __u32 done;
    __u32 remaining;
    __u32 speed;
    __s32 direction;
    __u32 superseded; /* 此句柄保护的轴已被其他句柄发出的命令替换 */
    __s64 position __attribute__((aligned(8)));
    __s64 target __attribute__((aligned(8)));
    __u64 generation __attribute__((aligned(8))); /* 已接受命令的序列号 */
};
struct ptz_status {
    struct ptz_axis_status axis[PTZ_AXES];
};
/* 位置记录的是已输出的半步数，不是传感器测得的实际轴位置。 */
struct ptz_set_position {
    __u32 axis;
    __s32 positive_direction; /* 位置增加对应的原始相序方向（+1/-1） */
    __s64 position __attribute__((aligned(8)));
};
struct ptz_axis_position {
    __s64 position __attribute__((aligned(8)));
    __u32 reserved;
    __s32 positive_direction;
};
struct ptz_positions {
    struct ptz_axis_position axis[PTZ_AXES];
};
struct ptz_travel {
    __u32 axis;
    __u32 max_steps; /* 范围为闭区间 [0, max_steps]，上限必须非零 */
};
struct ptz_travels {
    __u32 max_steps[PTZ_AXES];
}; /* 零表示尚未配置 */
struct ptz_move_to {
    __u32 axis;
    __u32 speed; /* 单位：半步/秒；档位通过 ptz_speed_for_level() 换算 */
    __s64 target __attribute__((aligned(8)));
};
/* 旧命令 1（MOVE）和 9（JOG）已移除，运动统一使用 MOVE_TO。 */
#define PTZ_STOP _IOW('P', 2, __u32) /* 轴掩码：水平=1，垂直=2，两轴=3 */
#define PTZ_STATUS _IOR('P', 3, struct ptz_status)
#define PTZ_SET_POSITION _IOW('P', 4, struct ptz_set_position)
#define PTZ_GET_POSITION _IOR('P', 5, struct ptz_positions)
#define PTZ_SET_TRAVEL _IOW('P', 6, struct ptz_travel)
#define PTZ_GET_TRAVEL _IOR('P', 7, struct ptz_travels)
#define PTZ_MOVE_TO _IOW('P', 8, struct ptz_move_to)
/* 内核归零状态命令 10/11 已移除。
 * 可选的句柄序列保护：记录掩码指定轴的当前命令序列号。
 * 其他句柄的修改仅使对应轴的保护失效。
 * 修改命令涉及失效轴时，整体返回 ESTALE，不修改任何轴。
 * 查询不受影响；STATUS.superseded 分别报告各轴的保护状态。
 * 失效后需新建句柄重新保护，其他轴仍可使用。
 * 此机制不阻止其他句柄替换运动命令或停止电机。
 */
#define PTZ_GUARD _IOW('P', 12, __u32) /* 轴掩码与 STOP 相同 */
#endif
