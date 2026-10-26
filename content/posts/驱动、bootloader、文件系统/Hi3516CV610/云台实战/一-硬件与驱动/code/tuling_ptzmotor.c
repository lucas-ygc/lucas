// SPDX-License-Identifier: GPL-2.0
/* Hi3516CV610 two-axis, four-input ULN2803 motor control. */
#include <linux/module.h>
#include <linux/miscdevice.h>
#include <linux/fs.h>
#include <linux/gpio.h>
#include <linux/of_gpio.h>
#include <linux/hrtimer.h>
#include <linux/mutex.h>
#include <linux/spinlock.h>
#include <linux/uaccess.h>
#include <linux/reboot.h>
#include <linux/slab.h>
#include "ptz_motion.h"

struct ptz_axis {
    struct hrtimer timer;
    spinlock_t lock;
    int gpio[4];
    unsigned int acquired;
    unsigned int phase;
    u64 interval;
    struct ptz_axis_status state;
    struct ptz_axis_position position;
    u32 max_steps;
};
static struct ptz_axis axes[PTZ_AXES];
static DEFINE_MUTEX(control_lock);
struct ptz_client {
    u32 guarded;
    u64 generation[PTZ_AXES];
};
static bool shutting_down;

static void drive(struct ptz_axis *a, unsigned int pattern)
{
    unsigned int i;
    /* Turn off old winding inputs before turning on the next phase. */
    for (i = 0; i < a->acquired; i++)
        if (!(pattern & BIT(i))) gpio_set_value(a->gpio[i], 0);
    for (i = 0; i < a->acquired; i++)
        if (pattern & BIT(i)) gpio_set_value(a->gpio[i], 1);
}

static enum hrtimer_restart tick(struct hrtimer *timer)
{
    struct ptz_axis *a = container_of(timer, struct ptz_axis, timer);
    unsigned long flags;
    spin_lock_irqsave(&a->lock, flags);
    /* Keep the last phase energized for a whole step interval before release. */
    if (!a->state.remaining) {
        drive(a, 0);
        a->state.running = 0;
        spin_unlock_irqrestore(&a->lock, flags);
        return HRTIMER_NORESTART;
    }
    if (!ptz_count_step(&a->position, a->state.direction)) {
        drive(a, 0);
        a->state.running = 0;
        a->state.remaining = 0;
        spin_unlock_irqrestore(&a->lock, flags);
        return HRTIMER_NORESTART;
    }
    a->phase = ptz_next_phase(a->phase, a->state.direction);
    drive(a, ptz_phases[a->phase]);
    a->state.done++;
    a->state.remaining--;
    /* Do not catch up delayed callbacks with a burst of zero-duration steps. */
    hrtimer_forward_now(timer, ns_to_ktime(a->interval));
    spin_unlock_irqrestore(&a->lock, flags);
    return HRTIMER_RESTART;
}

static void stop_axis(struct ptz_axis *a)
{
    unsigned long flags;
    hrtimer_cancel(&a->timer);
    spin_lock_irqsave(&a->lock, flags);
    drive(a, 0);
    a->state.running = 0;
    a->state.remaining = 0;
    a->state.target = a->position.position;
    spin_unlock_irqrestore(&a->lock, flags);
}

static long ptz_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
    void __user *p = (void __user *)arg;
    struct ptz_move m;
    struct ptz_status status = {0};
    struct ptz_set_position position;
    struct ptz_positions positions = {0};
    struct ptz_travel travel;
    struct ptz_travels travels = {0};
    struct ptz_move_to to;
    struct ptz_client *client = file->private_data;
    struct ptz_axis *a;
    unsigned long flags;
    unsigned int i;
    u32 mask = 0, changed = 0;
    int ret = 0;
    bool start_timer;
    if (cmd == PTZ_STOP || cmd == PTZ_GUARD) {
        if (copy_from_user(&mask, p, sizeof(mask))) return -EFAULT;
        if (!mask || (mask & ~3U)) return -EINVAL;
    } else if (cmd == PTZ_SET_POSITION) {
        if (copy_from_user(&position, p, sizeof(position))) return -EFAULT;
        if (!ptz_valid_position(&position)) return -EINVAL;
    } else if (cmd == PTZ_SET_TRAVEL) {
        if (copy_from_user(&travel, p, sizeof(travel))) return -EFAULT;
        if (travel.axis >= PTZ_AXES || !travel.max_steps) return -EINVAL;
    } else if (cmd == PTZ_MOVE_TO) {
        if (copy_from_user(&to, p, sizeof(to))) return -EFAULT;
        if (to.axis >= PTZ_AXES || !to.speed || to.speed > PTZ_MAX_SPEED)
            return -EINVAL;
    } else if (cmd != PTZ_STATUS && cmd != PTZ_GET_POSITION &&
               cmd != PTZ_GET_TRAVEL) return -ENOTTY;

    mutex_lock(&control_lock);
    if (shutting_down) { ret = -ESHUTDOWN; goto out; }
    if (cmd == PTZ_MOVE_TO) changed = BIT(to.axis);
    else if (cmd == PTZ_SET_POSITION) changed = BIT(position.axis);
    else if (cmd == PTZ_SET_TRAVEL) changed = BIT(travel.axis);
    else if (cmd == PTZ_STOP) changed = mask;
    /* Check-and-mutate under one mutex: an old sequence cannot stop or
     * overwrite the command that superseded it, including between home stages. */
    for (i = 0; i < PTZ_AXES; i++) {
        if (((changed | (cmd == PTZ_GUARD ? mask : 0)) & client->guarded & BIT(i)) &&
            client->generation[i] != axes[i].state.generation) {
            ret = -ESTALE;
            goto out;
        }
    }
    switch (cmd) {
    case PTZ_GUARD:
        client->guarded |= mask;
        for (i = 0; i < PTZ_AXES; i++)
            if (mask & BIT(i)) client->generation[i] = axes[i].state.generation;
        break;
    case PTZ_STOP:
        for (i = 0; i < PTZ_AXES; i++) if (mask & BIT(i)) stop_axis(&axes[i]);
        break;
    case PTZ_MOVE_TO:
        a = &axes[to.axis];
        spin_lock_irqsave(&a->lock, flags);
        ret = ptz_plan_absolute(&a->position, a->max_steps, &to, &m);
        if (ret) {
            spin_unlock_irqrestore(&a->lock, flags);
            break; /* An invalid target must not interrupt the active move. */
        }
        start_timer = !a->state.running;
        a->state.done = 0;
        a->state.remaining = m.steps;
        a->state.direction = m.direction;
        a->state.speed = m.speed;
        a->state.running = m.steps != 0;
        a->state.target = to.target;
        a->interval = div_u64(NSEC_PER_SEC, m.speed);
        if (!m.steps) drive(a, 0);
        spin_unlock_irqrestore(&a->lock, flags);
        if (!m.steps)
            hrtimer_cancel(&a->timer);
        else if (start_timer)
            hrtimer_start(&a->timer, ns_to_ktime(a->interval), HRTIMER_MODE_REL);
        /* A running timer picks up the updated plan at its next step. */
        break;
    case PTZ_STATUS:
        for (i = 0; i < PTZ_AXES; i++) {
            spin_lock_irqsave(&axes[i].lock, flags);
            status.axis[i] = axes[i].state;
            status.axis[i].position = axes[i].position.position;
            status.axis[i].superseded = (client->guarded & BIT(i)) &&
                client->generation[i] != axes[i].state.generation;
            spin_unlock_irqrestore(&axes[i].lock, flags);
        }
        if (copy_to_user(p, &status, sizeof(status))) ret = -EFAULT;
        break;
    case PTZ_SET_POSITION:
        a = &axes[position.axis];
        spin_lock_irqsave(&a->lock, flags);
        if (a->state.running) {
            ret = -EBUSY;
        } else if (a->max_steps && (position.position < 0 ||
                                   position.position > a->max_steps)) {
            ret = -ERANGE;
        } else {
            a->position.position = position.position;
            a->position.positive_direction = position.positive_direction;
            a->state.target = position.position;
        }
        spin_unlock_irqrestore(&a->lock, flags);
        break;
    case PTZ_GET_POSITION:
        for (i = 0; i < PTZ_AXES; i++) {
            spin_lock_irqsave(&axes[i].lock, flags);
            positions.axis[i] = axes[i].position;
            spin_unlock_irqrestore(&axes[i].lock, flags);
        }
        if (copy_to_user(p, &positions, sizeof(positions))) ret = -EFAULT;
        break;
    case PTZ_SET_TRAVEL:
        a = &axes[travel.axis];
        spin_lock_irqsave(&a->lock, flags);
        if (a->state.running) {
            ret = -EBUSY;
        } else if ((a->position.position < 0 ||
                   a->position.position > travel.max_steps)) {
            ret = -ERANGE;
        } else {
            a->max_steps = travel.max_steps;
        }
        spin_unlock_irqrestore(&a->lock, flags);
        break;
    case PTZ_GET_TRAVEL:
        for (i = 0; i < PTZ_AXES; i++) travels.max_steps[i] = axes[i].max_steps;
        if (copy_to_user(p, &travels, sizeof(travels))) ret = -EFAULT;
        break;
    }
    if (!ret && changed) {
        for (i = 0; i < PTZ_AXES; i++) {
            if (!(changed & BIT(i))) continue;
            axes[i].state.generation++;
            client->generation[i] = axes[i].state.generation;
        }
    }
out:
    mutex_unlock(&control_lock);
    return ret;
}

static int ptz_open(struct inode *inode, struct file *file)
{
    struct ptz_client *client = kzalloc(sizeof(*client), GFP_KERNEL);
    if (!client) return -ENOMEM;
    file->private_data = client;
    return 0;
}
static int ptz_release(struct inode *inode, struct file *file)
{
    /* Motion is asynchronous and independent of the command fd lifetime. */
    kfree(file->private_data);
    return 0;
}
static const struct file_operations ptz_fops = {
    .owner = THIS_MODULE, .unlocked_ioctl = ptz_ioctl,
    .open = ptz_open, .release = ptz_release, .llseek = no_llseek,
};
static struct miscdevice ptz_device = {
    .minor = MISC_DYNAMIC_MINOR, .name = "tuling_ptz", .fops = &ptz_fops, .mode = 0600,
};

static int ptz_shutdown(struct notifier_block *nb, unsigned long event, void *data)
{
    unsigned int i;
    mutex_lock(&control_lock);
    shutting_down = true;
    for (i = 0; i < PTZ_AXES; i++) stop_axis(&axes[i]);
    mutex_unlock(&control_lock);
    return NOTIFY_DONE;
}
static struct notifier_block reboot_hook = { .notifier_call = ptz_shutdown };

static void cleanup_gpio(void)
{
    unsigned int i, j;
    for (i = 0; i < PTZ_AXES; i++) {
        stop_axis(&axes[i]);
        for (j = 0; j < axes[i].acquired; j++) gpio_free(axes[i].gpio[j]);
        axes[i].acquired = 0;
    }
}

static int __init ptz_init(void)
{
    const char *props[] = {"horizontal-gpios", "vertical-gpios"};
    struct device_node *np;
    enum of_gpio_flags flags;
    unsigned int i, j;
    int ret;
    for (i = 0; i < PTZ_AXES; i++) {
        spin_lock_init(&axes[i].lock);
        axes[i].position.positive_direction = 1;
        hrtimer_init(&axes[i].timer, CLOCK_MONOTONIC, HRTIMER_MODE_REL);
        axes[i].timer.function = tick;
    }
    np = of_find_compatible_node(NULL, NULL, "tuling,ba4k-ptzmotor");
    if (!np) return -ENODEV;
    if (!of_device_is_available(np)) { ret = -ENODEV; goto fail; }
    for (i = 0; i < PTZ_AXES; i++) {
        if (of_gpio_named_count(np, props[i]) != 4) { ret = -EINVAL; goto fail; }
        for (j = 0; j < 4; j++) {
            ret = of_get_named_gpio_flags(np, props[i], j, &flags);
            if (ret < 0) goto fail;
            axes[i].gpio[j] = ret;
            if (flags || gpio_cansleep(ret)) { ret = -EINVAL; goto fail; }
            ret = gpio_request(axes[i].gpio[j], "tuling-ptz");
            if (ret) goto fail;
            axes[i].acquired++;
            ret = gpio_direction_output(axes[i].gpio[j], 0);
            if (ret) goto fail;
        }
    }
    ret = register_reboot_notifier(&reboot_hook);
    if (ret) goto fail;
    ret = misc_register(&ptz_device);
    if (ret) { unregister_reboot_notifier(&reboot_hook); goto fail; }
    of_node_put(np);
    pr_info("tuling_ptz: two axes ready, coils released\n");
    return 0;
fail:
    of_node_put(np);
    cleanup_gpio();
    return ret;
}
static void __exit ptz_exit(void)
{
    misc_deregister(&ptz_device);
    unregister_reboot_notifier(&reboot_hook);
    cleanup_gpio();
}
module_init(ptz_init);
module_exit(ptz_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("ygc");
MODULE_DESCRIPTION("BA4K Hi3516CV610 dual-axis half-step motor driver");
