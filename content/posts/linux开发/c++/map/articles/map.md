---
title: map
type: categories
categories: linux开发
description: c++
abbrlink: 93adaabb
cover: "../images/封面.png"
typora-root-url: ./..\..\..
date: 2022-09-29 00:00:00
swiper_index:
---
# map
std::map<key_type, value_type> myMap;

## 注意事项
1. map的key是唯一的，不能重复。
2、注意访问如果不存在会自动创建一个元素。所以尽量是用迭代器访问。(避免map[key]方式)
