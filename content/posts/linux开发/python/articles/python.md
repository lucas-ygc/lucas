---
title: python
date: 2026-08-11 11:31:24
categories: linux开发
abbrlink: '0'
cover: "../images/封面.png"
---
# import 
相当于include

# import cv2 as cv
相当于 include<cv2>
namespace cv = cv2



# from .xx文件 import aa函数
相当于从这个文件中拿到了这个函数


# 类
class p:
        def __init__(self, weights_path: str, providers: list[str] | None = None) -> None:

def = 定义函数
__init__ = 构造函数
self = 指向自身的实例
weights_path: str =  参数 + 类型标注
providers: list[str] | None  = 可选参数，默认 None
-> None = 返回值类型标注：无返回值，构造函数本来就没返回值

如果要想指定传某个参数可以变成weights_path=path

# _
通用下划线表示某些值不用，丢弃
_,_,se = input()
