---
title: c++虚函数
type: categories
categories: linux开发
description: c++
abbrlink: cef3c4d
cover: "../images/封面.png"
typora-root-url: ./..\..\..
date: 2022-09-29 00:00:00
swiper_index:
---

# c++虚函数
用法：
## 在析构函数中，最好都加上
```c++
class A {
public:
    virtual ~A() {}
}
```
这样可以避免内存泄漏，在子类释放的时候，父类也会被释放，即使父类有定义实现，父类也可以再次执行。

## 父类声明使用
```c++
class A {
    
    virtual void func() = 0;
    virtual void func1() = 0;
}
```
这样在子类中必须实现，否则会报错。=0 是纯虚函数，不能有实现。

## 扩展 override
在基类声明过虚函数后，子类实现添加`override`关键字，这样可以避免子类实现错误。