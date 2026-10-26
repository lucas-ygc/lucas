---
title: 'std::this_thread 命名空间'
type: categories
categories: linux开发
description: c++
abbrlink: 45a88c5b
cover: "../images/封面.png"
typora-root-url: ./..\..\..
date: 2022-09-29 00:00:00
swiper_index:
---

# std::this_thread

## 问题1： std::this_thread 命名空间下都有哪些线程操作
`std::this_thread` 是 C++11 引入的，专门用于操作**当前执行的线程**，提供了一系列简洁实用的接口。

### 一、`std::this_thread` 核心操作详解
`std::this_thread` 所有接口都定义在 `<thread>` 头文件中，核心操作分为以下几类：

#### 1. 获取当前线程 ID：`get_id()`
- **功能**：返回当前线程的唯一标识符（类型为 `std::thread::id`）。
- **用途**：调试、日志记录、区分不同线程、判断线程是否为主线程等。
- **示例代码**：
```cpp
#include <iostream>
#include <thread>
#include <vector>

void thread_func(int num) {
    // 获取当前线程ID并打印
    std::cout << "线程 " << num << " 的ID: " << std::this_thread::get_id() << std::endl;
}

int main() {
    std::cout << "主线程ID: " << std::this_thread::get_id() << std::endl;
    
    std::vector<std::thread> threads;
    for (int i = 0; i < 3; ++i) {
        threads.emplace_back(thread_func, i);
    }
    
    for (auto& t : threads) {
        t.join();
    }
    return 0;
}
```
- **输出示例**（ID 为系统分配，每次运行可能不同）：
```
主线程ID: 1407092608
线程 0 的ID: 1407092320
线程 1 的ID: 1407092236
线程 2 的ID: 1407092152
```

#### 2. 线程休眠：`sleep_for()`
- **功能**：让当前线程休眠**指定的时间段**，休眠期间线程不占用 CPU 资源。
- **参数**：`std::chrono` 类型的时间间隔（如 `std::chrono::seconds`、`std::chrono::milliseconds`）。
- **示例代码**：
```cpp
#include <iostream>
#include <thread>
#include <chrono>

int main() {
    std::cout << "开始休眠..." << std::endl;
    // 休眠 2 秒 + 500 毫秒
    std::this_thread::sleep_for(std::chrono::seconds(2) + std::chrono::milliseconds(500));
    std::cout << "休眠结束！" << std::endl;
    return 0;
}
```

#### 3. 线程休眠到指定时间点：`sleep_until()`
- **功能**：让当前线程休眠**直到指定的时间点**，而非固定时长（适合需要精准到某个时间执行的场景）。
- **参数**：`std::chrono::time_point` 类型的时间点（如系统时钟的某个时刻）。
- **示例代码**：
```cpp
#include <iostream>
#include <thread>
#include <chrono>

int main() {
    // 获取当前系统时间 + 3 秒，作为休眠结束的时间点
    auto wake_up_time = std::chrono::system_clock::now() + std::chrono::seconds(3);
    std::cout << "休眠到指定时间点..." << std::endl;
    std::this_thread::sleep_until(wake_up_time);
    std::cout << "到达时间点，休眠结束！" << std::endl;
    return 0;
}
```

#### 4. 线程让步：`yield()`
- **功能**：主动让当前线程放弃 CPU 执行权，提示操作系统调度器优先调度其他就绪线程（但操作系统不一定采纳）。
- **用途**：避免单个线程长时间占用 CPU（如循环等待某个条件时），提升多线程并发效率。
- **示例代码**：
```cpp
#include <iostream>
#include <thread>

void busy_wait() {
    int count = 0;
    while (count < 1000000) {
        ++count;
        // 每循环一次就让步，给其他线程执行机会
        std::this_thread::yield();
    }
    std::cout << "循环结束，当前线程ID: " << std::this_thread::get_id() << std::endl;
}

int main() {
    std::thread t1(busy_wait);
    std::thread t2(busy_wait);
    
    t1.join();
    t2.join();
    return 0;
}
```

### 二、注意事项
1. `sleep_for()`/`sleep_until()` 可能会被系统信号中断，导致实际休眠时间短于预期（C++11 及以上可通过返回值判断，但部分编译器未实现）。
2. `yield()` 仅为“提示”，不能保证其他线程一定被调度，不要依赖它实现精准的线程同步（同步应使用 `std::mutex`/`std::condition_variable`）。
3. 所有 `std::this_thread` 操作仅作用于**当前线程**，无法操作其他线程（操作其他线程需通过 `std::thread` 对象）。

### 总结
`std::this_thread` 的核心操作可归纳为 4 类，重点如下：
1. `get_id()`：获取当前线程的唯一 ID，用于标识和区分线程；
2. `sleep_for()`/`sleep_until()`：让当前线程休眠（固定时长/指定时间点）；
3. `yield()`：主动让步 CPU，提升多线程并发效率；
4. 所有操作均需包含 `<thread>` 头文件，且仅作用于当前执行的线程。


## 问题2： 与c中的sleep()函数区别

C++ 的 `std::this_thread::sleep_for` 与 C 语言的 `sleep` 函数有以下主要区别：

### 参数类型

- **C++ `std::this_thread::sleep_for`**：使用 `std::chrono::duration` 类型，如 `std::chrono::seconds(5)`
- **C `sleep`**：使用整数类型，表示秒数

### 精度控制

- **C++ 版本**：支持多种时间精度（纳秒、微秒、毫秒、秒等）
- **C 版本**：通常只支持秒级精度

### 使用示例对比

```cpp
// C++ 方式
#include <thread>
#include <chrono>
std::this_thread::sleep_for(std::chrono::milliseconds(1000)); // 1000毫秒
std::this_thread::sleep_for(std::chrono::seconds(5));         // 5秒
```

```c
// C 方式
#include <unistd.h>
sleep(5);  // 5秒
```

### 类型安全

- **C++ 版本**：类型安全，编译时检查时间单位
- **C 版本**：类型不安全，容易混淆时间单位

### 标准库归属

- **C++ 版本**：属于 `<thread>` 头文件
- **C 版本**：属于 POSIX 标准，`<unistd.h>` 头文件

**总结**：C++ 版本提供了更好的类型安全和更精细的时间控制能力，而 C 版本简单直接但精度较低。