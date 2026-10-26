---
title: decltype 关键字--泛型编程
type: categories
categories: linux开发
description: c++
abbrlink: '20366e75'
cover: "../images/封面.png"
typora-root-url: ./..\..\..
date: 2022-09-29 00:00:00
swiper_index:
---


# decltype 关键字
## 1. 定义
`decltype`是C++11引入的一个关键字，用于在编译时确定表达式的类型。它可以用于推导变量的类型，或者用于定义函数的返回类型。
## 2. 用法
`decltype`关键字通常用于推导变量的类型，或者用于定义函数的返回类型。
```c++
int x = 10;
decltype(x) y = 20; // y的类型为int
auto func(int a, int b) -> decltype(a + b) {
    return a + b;
}
decltype(func(1, 2)) z = func(1, 2); // z的类型为int
decltype(auto) w = x; // w的类型为int&
decltype(auto) func2(int a, int b) {
    return a + b;
}
```