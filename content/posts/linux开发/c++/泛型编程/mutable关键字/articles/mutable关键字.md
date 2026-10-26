---
title: mutable--泛型编程
type: categories
categories: linux开发
description: c++
abbrlink: 5f30f095
cover: "../images/封面.png"
typora-root-url: ./..\..\..
date: 2022-09-29 00:00:00
swiper_index:
---


# mutable--泛型编程
## 1. 定义
`mutable`是C++中的一个关键字，用于修饰类的成员变量。它的作用是允许在`const`成员函数中修改被`mutable`修饰的成员变量。
## 2. 用法
`mutable`关键字通常用于修饰类的成员变量，以便在`const`成员函数中修改这些变量的值。
```c++
class MyClass {

public:
    mutable int mutableVar;
    void constMemberFunc() const {
        mutableVar = 10; // 在const成员函数中修改mutableVar的值
    }
}
```