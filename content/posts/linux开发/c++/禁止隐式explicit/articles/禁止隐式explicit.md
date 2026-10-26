---
title: c++ explicit 关键字
type: categories
categories: linux开发
description: c++
abbrlink: 700c1288
cover: "../images/封面.png"
typora-root-url: ./..\..\..
date: 2022-09-29 00:00:00
swiper_index:
---

# c++ explicit 关键字
## 用法：
```c++
class A {
    explicit A(int a) {}
}

A a(1);


错误：
A a = 1;
错误：
A a(1, 2);
错误：
A a = {1, 2};
错误：
A a{1, 2};
错误：
A a = (A)1;
错误：
A a = (A){1, 2};
```
这样在创建对象的时候，只能使用显式的方式创建，不能使用隐式的方式创建。
这样可以避免一些不必要的错误。对创建对象的方式进行限制。


