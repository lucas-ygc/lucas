---
title: 仿函数operator--泛型编程
type: categories
categories: linux开发
description: c++
abbrlink: 1b6149d4
cover: "../images/封面.png"
typora-root-url: ./..\..\..
date: 2022-09-29 00:00:00
swiper_index:
---

# 仿函数
## 用法
```c++
class A {

public:
    virtual ~A() {}
    virtual void operator()() {
        std::cout << "A" << std::endl;
    }
}


struct B {
    void operator()() {
        std::cout << "B" << std::endl;
    }
}
struct C {
    bool operator==(int a, int b) const  {
        return a == b;
    }
}
struct D {
    int operator()(int a, int b) const {
        return a + b;
    }
struct E {
    int operator=(int a, int b) const {
        return a + b;
    }


int main() {
    A a;
    B b;
    a();
    b();
}

```

仿函数（Function Object）是一种对象，它重载了()运算符，使得对象可以像函数一样被调用。仿函数通常用于实现算法和数据结构，以及作为回调函数传递给其他函数。