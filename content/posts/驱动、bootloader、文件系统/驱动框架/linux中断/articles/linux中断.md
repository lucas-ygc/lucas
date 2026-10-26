---
title: linux中断
type: categories
categories: 驱动、bootloader、文件系统
cover: "../images/封面.png"
description: linux中断
abbrlink: 835d4465
typora-root-url: ./..\..\..
date: 2022-10-29 00:00:00
swiper_index:
---

# linux中断
## 1、硬件中断
### 1-1、Linux内核中断API

以下是Linux内核中断处理相关的API

#### 1-1-1、中断处理函数注册和注销
```c
int request_irq(unsigned int irq, irq_handler_t handler, unsigned long flags, const char *name, void *dev);
void free_irq(unsigned int irq, void *dev);
```

- **`request_irq`**
  - **参数**：
    - `unsigned int irq`: 中断号。
    - `irq_handler_t handler`: 中断处理函数指针。
    - `unsigned long flags`: 中断标志（如`IRQF_SHARED`表示共享中断线）。
    - `const char *name`: 中断处理程序的名称，用于调试。
    - `void *dev`: 设备标识符，通常为设备结构体。
  - **返回值**：
    - `0`: 成功注册。
    - 非零值: 注册失败。

- **`free_irq`**
  - **参数**：
    - `unsigned int irq`: 中断号。
    - `void *dev`: 设备标识符，必须与注册时一致。

#### 1-1-2、中断处理函数原型
```c
irqreturn_t (*handler)(int irq, void *dev_id);
```

- **参数**：
  - `int irq`: 中断号。
  - `void *dev_id`: 设备标识符，与`request_irq`中的`dev`参数一致。
- **返回值**：
  - `IRQ_HANDLED`: 成功处理了中断。
  - `IRQ_NONE`: 未处理中断。

#### 1-1-3、禁用和启用中断
```c
void local_irq_disable(void);
void local_irq_enable(void);
void local_irq_save(unsigned long flags);
void local_irq_restore(unsigned long flags);
```

- **`local_irq_disable`**
  - **参数**：无。
  - **功能**：禁用当前CPU上的本地中断。

- **`local_irq_enable`**
  - **参数**：无。
  - **功能**：启用当前CPU上的本地中断。

- **`local_irq_save`**
  - **参数**：
    - `unsigned long flags`: 用于保存当前中断状态。
  - **功能**：保存当前中断状态并禁用中断。

- **`local_irq_restore`**
  - **参数**：
    - `unsigned long flags`: 通过`local_irq_save`保存的状态。
  - **功能**：恢复之前保存的中断状态。

#### 1-1-3、延迟工作队列（Bottom Halves）

##### 任务队列（Tasklet）
```c
DECLARE_TASKLET(name, void (*func)(unsigned long), unsigned long data);
void tasklet_schedule(struct tasklet_struct *t);
void tasklet_init(struct tasklet_struct *t, void (*func)(unsigned long), unsigned long data);
void tasklet_kill(struct tasklet_struct *t);
```

- **`DECLARE_TASKLET`**
  - **参数**：
    - `name`: 任务队列的名称。
    - `void (*func)(unsigned long)`: 任务队列的处理函数。
    - `unsigned long data`: 私有数据，传递给处理函数。
  - **功能**：定义一个任务队列结构体。

- **`tasklet_schedule`**
  - **参数**：
    - `struct tasklet_struct *t`: 任务队列结构体指针。
  - **功能**：调度任务队列执行。

- **`tasklet_init`**
  - **参数**：
    - `struct tasklet_struct *t`: 任务队列结构体指针。
    - `void (*func)(unsigned long)`: 任务队列的处理函数。
    - `unsigned long data`: 私有数据，传递给处理函数。
  - **功能**：初始化任务队列。

- **`tasklet_kill`**
  - **参数**：
    - `struct tasklet_struct *t`: 任务队列结构体指针。
  - **功能**：等待任务队列完成并销毁它。

##### 工作队列（Workqueue）
```c
struct workqueue_struct *create_workqueue(const char *name);
void destroy_workqueue(struct workqueue_struct *wq);
void queue_work(struct workqueue_struct *wq, struct work_struct *work);
void INIT_WORK(struct work_struct *work, work_func_t func);
void flush_workqueue(struct workqueue_struct *wq);
```

- **`create_workqueue`**
  - **参数**：
    - `const char *name`: 工作队列的名称。
  - **返回值**：
    - `struct workqueue_struct *`: 工作队列结构体指针。
  - **功能**：创建一个新的工作队列。

- **`destroy_workqueue`**
  - **参数**：
    - `struct workqueue_struct *wq`: 工作队列结构体指针。
  - **功能**：销毁工作队列。

- **`queue_work`**
  - **参数**：
    - `struct workqueue_struct *wq`: 工作队列结构体指针。
    - `struct work_struct *work`: 工作项结构体指针。
  - **功能**：将工作项加入工作队列。

- **`INIT_WORK`**
  - **参数**：
    - `struct work_struct *work`: 工作项结构体指针。
    - `work_func_t func`: 工作项的处理函数。
  - **功能**：初始化工作项结构体。

- **`flush_workqueue`**
  - **参数**：
    - `struct workqueue_struct *wq`: 工作队列结构体指针。
  - **功能**：等待工作队列中的所有工作项完成。

### 示例代码

#### 使用任务队列（Tasklet）
```c
#include <linux/interrupt.h>
#include <linux/module.h>
#include <linux/kernel.h>

static struct tasklet_struct my_tasklet;

void my_tasklet_handler(unsigned long data)
{
    printk(KERN_INFO "Tasklet handler executed, data=%lu\n", data);
}

static irqreturn_t my_interrupt_handler(int irq, void *dev_id)
{
    tasklet_schedule(&my_tasklet);
    return IRQ_HANDLED;
}

static int __init my_module_init(void)
{
    int ret;
    unsigned int irq = 42; // 示例中断号

    tasklet_init(&my_tasklet, my_tasklet_handler, (unsigned long)12345);
    ret = request_irq(irq, my_interrupt_handler, IRQF_SHARED, "my_interrupt", NULL);
    if (ret) {
        printk(KERN_ERR "Failed to register interrupt handler\n");
        return ret;
    }

    printk(KERN_INFO "Interrupt handler registered for IRQ %d\n", irq);
    return 0;
}

static void __exit my_module_exit(void)
{
    unsigned int irq = 42; // 示例中断号

    free_irq(irq, NULL);
    tasklet_kill(&my_tasklet);

    printk(KERN_INFO "Interrupt handler unregistered for IRQ %d\n", irq);
}

module_init(my_module_init);
module_exit(my_module_exit);

MODULE_LICENSE("GPL");
```

#### 使用工作队列（Workqueue）
```c
#include <linux/interrupt.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/workqueue.h>

static struct workqueue_struct *my_wq;
static struct work_struct my_work;

void my_work_handler(struct work_struct *work)
{
    printk(KERN_INFO "Work handler executed\n");
}

static irqreturn_t my_interrupt_handler(int irq, void *dev_id)
{
    queue_work(my_wq, &my_work);
    return IRQ_HANDLED;
}

static int __init my_module_init(void)
{
    int ret;
    unsigned int irq = 42; // 示例中断号

    my_wq = create_workqueue("my_wq");
    if (!my_wq) {
        printk(KERN_ERR "Failed to create workqueue\n");
        return -ENOMEM;
    }

    INIT_WORK(&my_work, my_work_handler);
    ret = request_irq(irq, my_interrupt_handler, IRQF_SHARED, "my_interrupt", NULL);
    if (ret) {
        printk(KERN_ERR "Failed to register interrupt handler\n");
        destroy_workqueue(my_wq);
        return ret;
    }

    printk(KERN_INFO "Interrupt handler registered for IRQ %d\n", irq);
    return 0;
}

static void __exit my_module_exit(void)
{
    unsigned int irq = 42; // 示例中断号

    free_irq(irq, NULL);
    flush_workqueue(my_wq);
    destroy_workqueue(my_wq);

    printk(KERN_INFO "Interrupt handler unregistered for IRQ %d\n", irq);
}

module_init(my_module_init);
module_exit(my_module_exit);

MODULE_LICENSE("GPL");
```

### 总结

这些API提供了在Linux内核中管理和处理中断的必要工具。通过使用任务队列和工作队列，可以有效地将中断处理中的复杂任务推迟到下半部执行，从而提高系统的响应速度和稳定性。

## 2、Linux内核软中断（Softirq）API

### 2-1、Linux内核软中断（Softirq）API

软中断（Softirq）是Linux内核中用于处理下半部任务的一种机制。软中断在中断上下文之外执行，但仍然具有较高的优先级。以下是与软中断相关的API及其参数解释：

#### 2-1-1、软中断API

##### 软中断类型
Linux内核定义了多个软中断类型，常见的包括：
```c
enum
{
    HI_SOFTIRQ=0,
    TIMER_SOFTIRQ,
    NET_TX_SOFTIRQ,
    NET_RX_SOFTIRQ,
    BLOCK_SOFTIRQ,
    BLOCK_IOPOLL_SOFTIRQ,
    TASKLET_SOFTIRQ,
    SCHED_SOFTIRQ,
    HRTIMER_SOFTIRQ,
    RCU_SOFTIRQ,    /* Preferable RCU should always be the last softirq */
    NR_SOFTIRQS
};
```

##### 软中断处理函数注册和注销
```c
void open_softirq(int nr, void (*action)(struct softirq_action *));
void raise_softirq(int nr);
void raise_softirq_irqoff(int nr);
void do_softirq(void);
void local_bh_disable(void);
void local_bh_enable(void);
```

- **`open_softirq`**
  - **参数**：
    - `int nr`: 软中断类型（如`NET_RX_SOFTIRQ`）。
    - `void (*action)(struct softirq_action *)`: 软中断处理函数。
  - **功能**：注册一个软中断处理函数。

- **`raise_softirq`**
  - **参数**：
    - `int nr`: 软中断类型。
  - **功能**：触发一个软中断。

- **`raise_softirq_irqoff`**
  - **参数**：
    - `int nr`: 软中断类型。
  - **功能**：触发一个软中断，假设中断已经禁用。

- **`do_softirq`**
  - **参数**：无。
  - **功能**：执行所有待处理的软中断。

- **`local_bh_disable`**
  - **参数**：无。
  - **功能**：禁用软中断。

- **`local_bh_enable`**
  - **参数**：无。
  - **功能**：启用软中断。

#### 2-1-2、软中断处理函数原型
```c
void (*action)(struct softirq_action *);
```

- **参数**：
  - `struct softirq_action *action`: 软中断动作结构体，包含私有数据。

### 2-2-2、示例代码

下面是一个简单的示例，展示如何注册和触发一个软中断。

```c
#include <linux/interrupt.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/sched.h>
#include <linux/init.h>
#include <linux/smp.h>

// 定义软中断处理函数
void my_softirq_handler(struct softirq_action *action)
{
    printk(KERN_INFO "Softirq handler executed\n");
}

// 注册软中断
static int __init my_module_init(void)
{
    // 注册软中断处理函数
    open_softirq(TASKLET_SOFTIRQ, my_softirq_handler);

    // 触发软中断
    raise_softirq(TASKLET_SOFTIRQ);

    printk(KERN_INFO "Softirq registered and raised\n");
    return 0;
}

// 卸载模块时注销软中断
static void __exit my_module_exit(void)
{
    printk(KERN_INFO "Module exiting\n");
}

module_init(my_module_init);
module_exit(my_module_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("A simple module to demonstrate softirqs");
```

### 代码解释

1. **定义软中断处理函数**：
   ```c
   void my_softirq_handler(struct softirq_action *action)
   {
       printk(KERN_INFO "Softirq handler executed\n");
   }
   ```

2. **注册软中断**：
   ```c
   static int __init my_module_init(void)
   {
       open_softirq(TASKLET_SOFTIRQ, my_softirq_handler);
       raise_softirq(TASKLET_SOFTIRQ);
       printk(KERN_INFO "Softirq registered and raised\n");
       return 0;
   }
   ```
   - 使用`open_softirq`注册软中断处理函数。
   - 使用`raise_softirq`触发软中断。

3. **卸载模块时注销软中断**：
   ```c
   static void __exit my_module_exit(void)
   {
       printk(KERN_INFO "Module exiting\n");
   }
   ```

### 总结

## 3、软中断和中断的区别
软中断是Linux内核中用于处理下半部任务的一种高效机制。通过注册和触发软中断，可以将中断处理中的复杂任务推迟到软中断上下文中执行，从而提高系统的响应速度和稳定性。上述示例展示了如何注册和触发一个软中断。


软中断（Softirq）和硬件中断是Linux内核中两种不同的中断处理机制，它们在触发和执行时机上有明显的区别。

### 3-1、硬件中断
- **触发时机**：当硬件设备发生特定事件（如数据到达、状态变化等）时，硬件会向CPU发送中断信号。
- **执行时机**：CPU立即响应中断，进入中断处理程序（Interrupt Handler），执行中断处理逻辑。
- **上下文**：中断处理程序在中断上下文中执行，中断上下文是原子的，不允许睡眠或阻塞。

### 3-2、软中断
- **触发时机**：软中断不是由硬件直接触发的，而是由内核代码显式调用`raise_softirq`或`raise_softirq_irqoff`函数来触发。
- **执行时机**：软中断在中断上下文之外执行，通常在中断返回之前或在内核调度器调度下一个任务时执行。
- **上下文**：软中断在软中断上下文中执行，允许一定程度的延迟处理，但仍然具有较高的优先级。

### 3-3、软中断的执行流程
1. **硬件中断发生**：
   - CPU响应硬件中断，进入中断处理程序。
   - 中断处理程序执行必要的快速操作，然后触发软中断（通过调用`raise_softirq`）。

2. **软中断触发**：
   - 中断处理程序调用`raise_softirq`来设置软中断标志。
   - 内核在中断返回之前或在内核调度器调度下一个任务时检查软中断标志。

3. **软中断执行**：
   - 内核调用`do_softirq`函数来执行所有待处理的软中断。
   - 软中断处理函数在软中断上下文中执行，处理延迟的任务。

### 3-4、示例代码解释

以下是一个简单的示例，展示如何在硬件中断处理程序中触发软中断：

```c
#include <linux/interrupt.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/sched.h>
#include <linux/init.h>
#include <linux/smp.h>

// 定义软中断处理函数
void my_softirq_handler(struct softirq_action *action)
{
    printk(KERN_INFO "Softirq handler executed\n");
}

// 中断处理函数
static irqreturn_t my_interrupt_handler(int irq, void *dev_id)
{
    printk(KERN_INFO "Hardware interrupt handler executed\n");

    // 触发软中断
    raise_softirq(TASKLET_SOFTIRQ);

    return IRQ_HANDLED;
}

// 注册软中断
static int __init my_module_init(void)
{
    int ret;
    unsigned int irq = 42; // 示例中断号

    // 注册软中断处理函数
    open_softirq(TASKLET_SOFTIRQ, my_softirq_handler);

    // 注册硬件中断处理程序
    ret = request_irq(irq, my_interrupt_handler, IRQF_SHARED, "my_interrupt", NULL);
    if (ret) {
        printk(KERN_ERR "Failed to register interrupt handler\n");
        return ret;
    }

    printk(KERN_INFO "Interrupt handler registered for IRQ %d\n", irq);
    return 0;
}

// 卸载模块时注销软中断和硬件中断处理程序
static void __exit my_module_exit(void)
{
    unsigned int irq = 42; // 示例中断号

    free_irq(irq, NULL);
    printk(KERN_INFO "Interrupt handler unregistered for IRQ %d\n", irq);
}

module_init(my_module_init);
module_exit(my_module_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("A simple module to demonstrate softirqs");
```

### 代码解释

1. **定义软中断处理函数**：
   ```c
   void my_softirq_handler(struct softirq_action *action)
   {
       printk(KERN_INFO "Softirq handler executed\n");
   }
   ```

2. **中断处理函数**：
   ```c
   static irqreturn_t my_interrupt_handler(int irq, void *dev_id)
   {
       printk(KERN_INFO "Hardware interrupt handler executed\n");

       // 触发软中断
       raise_softirq(TASKLET_SOFTIRQ);

       return IRQ_HANDLED;
   }
   ```
   - 当硬件中断发生时，`my_interrupt_handler`被调用。
   - 在中断处理程序中，调用`raise_softirq(TASKLET_SOFTIRQ)`来触发软中断。

3. **注册软中断和硬件中断处理程序**：
   ```c
   static int __init my_module_init(void)
   {
       int ret;
       unsigned int irq = 42; // 示例中断号

       // 注册软中断处理函数
       open_softirq(TASKLET_SOFTIRQ, my_softirq_handler);

       // 注册硬件中断处理程序
       ret = request_irq(irq, my_interrupt_handler, IRQF_SHARED, "my_interrupt", NULL);
       if (ret) {
           printk(KERN_ERR "Failed to register interrupt handler\n");
           return ret;
       }

       printk(KERN_INFO "Interrupt handler registered for IRQ %d\n", irq);
       return 0;
   }
   ```
   - 使用`open_softirq`注册软中断处理函数。
   - 使用`request_irq`注册硬件中断处理程序。

4. **卸载模块时注销软中断和硬件中断处理程序**：
   ```c
   static void __exit my_module_exit(void)
   {
       unsigned int irq = 42; // 示例中断号

       free_irq(irq, NULL);
       printk(KERN_INFO "Interrupt handler unregistered for IRQ %d\n", irq);
   }
   ```

### 总结

- **硬件中断**：由硬件直接触发，立即执行中断处理程序。
- **软中断**：由内核代码显式触发，通常在中断返回之前或在内核调度器调度下一个任务时执行。

通过这种方式，软中断可以将复杂的中断处理任务推迟到软中断上下文中执行，从而提高系统的响应速度和稳定性。


## 4、设备树调整
以按键的中断为例，在设备树中添加中断信息，并修改中断处理函数。
```c
	key{
		#address-cells = <1>;
		#size-cells = <1>;
		compatible = "naro-key";
		pinctrl-names = "default";
		interrupt-parent = <&gpio1>;
		interrupts = <18 IRQ_TYPE_EDGE_BOTH>;
		pinctrl-0 = <&pinctrl_key>;
		naro-key = <&gpio1 18 GPIO_ACTIVE_LOW>;
		status = "okay";
	};
```

复用为gpio

```c   
		pinctrl_key: keygrp {
		 	fsl,pins = <
		 		MX6UL_PAD_UART1_CTS_B__GPIO1_IO18  	 0xF080 /* KEY1 */
		 	>;
		 };

```


使用
```shell
cat /proc/interrupts 
```
可以查添加到设备树的中断开启了没有。