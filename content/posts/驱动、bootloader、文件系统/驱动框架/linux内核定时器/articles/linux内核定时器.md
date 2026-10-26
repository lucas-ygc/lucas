---
title: linux内核定时器
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: linux内核
abbrlink: 7ec46997
typora-root-url: ./..\..\..
date: 2022-10-29 00:00:00
swiper_index:
---


# 定时器
## 1、内核config配置
配置内核定时器步骤
```c
->kernel Features
        ->timer frequency (<choice> [=y])
```
在里面可以选择系统的节拍数，默认是1000Hz，也就是1ms节拍，如果选择2000Hz，就是0.5ms节拍，如果选择10000Hz，就是0.1ms节拍。配置完成后，在源码中的.config文件中，会自动生成如下配置：
```c
CONFIG_HZ=1000
```
这个就是节拍率。

这个配置生效在：include/asm-generic/param.h中
```c
#ifndef __ASM_GENERIC_PARAM_H
#define __ASM_GENERIC_PARAM_H

#include <uapi/asm-generic/param.h>

# undef HZ
# define HZ		CONFIG_HZ	/* Internal kernel timer frequency */
# define USER_HZ	100		/* some user interfaces are */
# define CLOCKS_PER_SEC	(USER_HZ)       /* in "ticks" like times() */
#endif /* __ASM_GENERIC_PARAM_H */

```
这就是内核定时器的频率了

## 2、api
### 2-1、Linux内核定时器API

#### 定时器数据结构
```c
struct timer_list *timer;
```

- **`struct timer_list *timer`**: 所有定时器操作都基于此结构。

#### 初始化和设置定时器
```c
void init_timer(struct timer_list *timer);
void setup_timer(struct timer_list *timer, void (*function)(unsigned long), unsigned long data);
```

- **`init_timer`**
  - **参数**：
    - `struct timer_list *timer`: 定时器结构体指针。
  - **功能**：初始化定时器。
  - **推荐使用**：在较新的内核版本中，推荐使用`setup_timer`函数。

- **`setup_timer`**
  - **参数**：
    - `struct timer_list *timer`: 定时器结构体指针。
    - `void (*function)(unsigned long)`: 定时器回调函数指针。
    - `unsigned long data`: 传递给回调函数的私有数据。
  - **功能**：初始化定时器并同时设置回调函数和定时器私有数据。

#### 修改和启动定时器
```c
int mod_timer(struct timer_list *timer, unsigned long expires);
void add_timer(struct timer_list *timer);
```

- **`mod_timer`**
  - **参数**：
    - `struct timer_list *timer`: 定时器结构体指针。
    - `unsigned long expires`: 定时器到期时间（以jiffies为单位）。
  - **返回值**：
    - `0`: 成功修改或启动定时器。
    - 非零值: 修改或启动失败。
  - **功能**：修改定时器的超时时间。如果定时器已经在等待队列中，它将被移除并重新安排新的超时时间。如果定时器未启动，则启动定时器。

- **`add_timer`**
  - **参数**：
    - `struct timer_list *timer`: 定时器结构体指针。
  - **功能**：向系统添加定时器，指定定时器到期时间。等同于初始化定时器后调用`mod_timer`。

#### 删除定时器
```c
int del_timer(struct timer_list *timer);
int del_timer_sync(struct timer_list *timer);
```

- **`del_timer`**
  - **参数**：
    - `struct timer_list *timer`: 定时器结构体指针。
  - **返回值**：
    - `1`: 定时器被成功删除。
    - `0`: 定时器未被删除（可能未找到或正在运行）。
  - **功能**：删除定时器。如果定时器当前正在运行，则不会等待其完成，直接删除。

- **`del_timer_sync`**
  - **参数**：
    - `struct timer_list *timer`: 定时器结构体指针。
  - **返回值**：
    - `1`: 定时器被成功删除。
    - `0`: 定时器未被删除（可能未找到或正在运行）。
  - **功能**：同步删除定时器。确保定时器在多处理器系统中的所有CPU上都不再运行后再删除。

#### 检查定时器状态
```c
int timer_pending(struct timer_list *timer);
```

- **`timer_pending`**
  - **参数**：
    - `struct timer_list *timer`: 定时器结构体指针。
  - **返回值**：
    - `1`: 定时器已启动但尚未到期。
    - `0`: 定时器未启动或已到期。
  - **功能**：检查定时器是否挂起（即已启动但尚未到期）。

### 使用示例

下面是一个简单的使用定时器的例子：

```c
#include <linux/timer.h>
#include <linux/module.h>
#include <linux/kernel.h>

static struct timer_list my_timer;

// 定时器回调函数
void my_timer_callback(unsigned long data)
{
    printk(KERN_INFO "Timer expired, data=%lu\n", data);
}

static int __init my_module_init(void)
{
    // 初始化定时器，并设置回调函数和私有数据
    setup_timer(&my_timer, my_timer_callback, 12345);

    // 设置定时器在5秒后触发
    mod_timer(&my_timer, jiffies + msecs_to_jiffies(5000));

    return 0;
}

static void __exit my_module_exit(void)
{
    // 同步删除定时器
    del_timer_sync(&my_timer);
}

module_init(my_module_init);
module_exit(my_module_exit);

MODULE_LICENSE("GPL");
```

### 总结

以上是Linux内核定时器的主要API及其使用方法。通过这些API，开发者可以在内核模块中实现精确的时间管理功能。