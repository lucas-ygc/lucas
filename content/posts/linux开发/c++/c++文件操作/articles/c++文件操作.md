---
title: 文件操作
type: categories
categories: linux开发
description: c++
abbrlink: 95495db
cover: "../images/封面.png"
typora-root-url: ./..\..\..
date: 2022-09-29 00:00:00
swiper_index:
---


# C++ 文件与目录操作完整笔记

## 一、文件操作基础

### 1.1 文件流类型
- **`ifstream`** - 输入文件流，用于从文件读取数据
- **`ofstream`** - 输出文件流，用于向文件写入数据
- **`fstream`** - 文件流，支持读写操作

### 1.2 文件打开方式
- **构造函数方式**：
  ```cpp
  ifstream file("filename.txt");
  ```
- **`open()` 方法**：
  ```cpp
  ofstream file;
  file.open("filename.txt");
  ```

### 1.3 文件读取操作
- **`getline()`** - 读取一行
- **`read()`** - 二进制读取
- **`>>` 操作符** - 格式化读取
- **`get()`** - 读取单个字符

### 1.4 文件写入操作
- **`<<` 操作符** - 格式化写入
- **`write()`** - 二进制写入
- **`put()`** - 写入单个字符

### 1.5 文件状态检查
- **`is_open()`** - 检查文件是否打开
- **`eof()`** - 检查是否到达文件末尾
- **`good()`** - 检查流状态是否正常

### 1.6 文件打开模式
- `ios::in` - 输入模式
- `ios::out` - 输出模式
- `ios::app` - 追加模式
- `ios::binary` - 二进制模式
- `ios::trunc` - 截断模式

## 二、目录操作

### 2.1 C++17 filesystem 库（现代 C++ 推荐）

#### 基本头文件
```cpp
#include <filesystem>
namespace fs = std::filesystem;
```

#### 基本目录操作
- **`fs::create_directory(path)`** - 创建目录
- **`fs::remove(path)`** - 删除目录（空目录）
- **`fs::remove_all(path)`** - 删除目录及其内容
- **`fs::exists(path)`** - 检查目录是否存在
- **`fs::current_path()`** - 获取当前工作目录

#### 目录遍历
- **`fs::directory_iterator`** - 目录迭代器，遍历目录内容
- **`fs::recursive_directory_iterator`** - 递归遍历目录及其子目录

#### 目录信息查询
- **`fs::is_directory(path)`** - 检查路径是否为目录
- **`fs::is_empty(path)`** - 检查目录是否为空
- **`fs::file_size(path)`** - 获取目录大小

### 2.2 传统 C 风格方式（C++17 之前）

#### Windows 平台
- **`_mkdir()`** / **`_rmdir()`** - 创建/删除目录
- **`FindFirstFile()`** / **`FindNextFile()`** - 遍历目录

#### Linux/Unix 平台
- **`<dirent.h>`** 头文件中的函数：
  - **`opendir()`** - 打开目录
  - **`readdir()`** - 读取目录项
  - **`closedir()`** - 关闭目录
  - **`mkdir()`** / **`rmdir()`** - 创建/删除目录

## 三、典型操作流程

### 3.1 文件操作流程
1. 创建文件流对象
2. 打开文件并检查是否成功
3. 执行读写操作
4. 关闭文件

### 3.2 目录操作流程（C++17）
1. 包含头文件 `<filesystem>`
2. 使用 `std::filesystem` 命名空间
3. 调用相应的目录操作函数

## 四、常用示例代码

### 4.1 文件读写示例
```cpp
#include <fstream>
#include <iostream>

// 写文件
std::ofstream outFile("test.txt");
outFile << "Hello, World!" << std::endl;
outFile.close();

// 读文件
std::ifstream inFile("test.txt");
std::string line;
std::getline(inFile, line);
std::cout << line << std::endl;
inFile.close();
```

### 4.2 目录操作示例（C++17）
```cpp
#include <filesystem>
namespace fs = std::filesystem;

// 创建目录
fs::create_directory("new_dir");

// 遍历目录
for(const auto& entry : fs::directory_iterator(".")) {
    if(fs::is_directory(entry)) {
        std::cout << "Directory: " << entry.path().filename() << std::endl;
    } else {
        std::cout << "File: " << entry.path().filename() << std::endl;
    }
}
```

## 五、重要提醒

- **现代 C++**：推荐使用 C++17 的 `std::filesystem` 库进行目录操作
- **跨平台兼容**：`std::filesystem` 提供统一的跨平台接口
- **错误处理**：操作文件和目录时要检查操作是否成功
- **资源管理**：及时关闭文件流，避免资源泄露