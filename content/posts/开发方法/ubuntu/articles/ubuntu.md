---
title: ubuntu
type: categories
categories: 开发方法
cover: "../images/封面.png"
description: ubuntu使用技巧
swiper_index: 1
abbrlink: 7c4b9639
typora-root-url: ./..\..\..
date: 2023-09-13 00:00:00
---
# 文件目录
linux目录从/开始
/bin 大部分系统的命令
/boot 引导文件，启动相关的目录
/dev 设备文件目录,Linux下一切设备皆文件
/etc：系统配置文件
/home 用户目录，一个用户对应一个文件夹
/lib 库文件
/lib64 64位库文件
/libx32 32位库文件
/lost+found 文件系统错误恢复文件
/media 媒体文件目录
/mnt 挂载目录
/opt 第三方软件安装目录
/proc 虚拟文件系统，存放进程和内核信息
/root 超级用户目录
/run 运行目录
/sbin 超级用户可执行文件
/srv 服务器数据目录
/sys 虚拟文件系统，存放硬件信息
/tmp 临时文件目录
/usr 用户程序目录
/var 变量文件目录
    


# 1 、ubuntu 24.04 
## 1-1、输入完密码或者安装完系统后黑屏
两步：vmware关闭3D加速、配置grub文件
```shell
vim /etc/default/grub

 ---找到 GRUB_CMDLINE_LINUX_DEFAULT="quiet splash" 一行
 ---改为 GRUB_CMDLINE_LINUX_DEFAULT="quiet splash nomodeset"

reboot
```
解析：
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash nomodeset" 这一行配置是在设置 GRUB（GNU GRand Unified Bootloader）引导程序的默认启动参数，
用于控制 Linux 内核的启动行为。   
具体来说：
* quiet: 使系统在启动过程中减少输出信息，使启动过程更加安静，不显示详细的启动信息。
* splash: 启用启动时的图形启动界面（splash screen），通常会显示一个漂亮的背景图片和启动进度条。
* nomodeset: 防止内核在启动时尝试自动设置显卡模式，这对于一些可能引起显示问题的显卡来说很有用，特别是在一些集成显卡或较新硬件上。
这条配置通常出现在 /etc/default/grub 文件中，并且在修改后需要运行 update-grub 命令来更新 GRUB 的配置文件，以使更改生效。这不属于编程语言层面的内容，而是操作系统级别的配置。

## 1-2、samba
```shell
[shared]
    comment = Shared Folder
    path = /srv/samba/shared
    browseable = yes
    read only = no
    guest ok = yes
    create mask = 0644
    directory mask = 0755
    passwd level = 0 
```

重点在于以下两个选项：

guest ok = yes：允许以“访客”身份访问共享文件夹。这意味着不需要用户名和密码就可以访问共享资源。
read only = no：允许用户写入共享文件夹。如果只需要读取访问，则可以设置为 yes。
passwd level = 0：表示 Samba 不需要用户的密码与系统密码一致。
passwd level = 0：表示 Samba 不需要用户的密码与系统密码一致。
还有不要有任何特定samba用户，若有就`sudo userdel -r <username>`删除掉。

## 1-3、ubuntu报chown: 无法访问 '/var/lib/nfs': 没有那个文件或目录

```shell
dpkg: 处理软件包 nfs-common (--configure)时出错：
 已安装 nfs-common 软件包 post-installation 脚本 子进程返回错误状态 1
在处理时有错误发生：
 nfs-common
E: Sub-process /usr/bin/dpkg returned an error code 
```
报类似这个错误解决办法
```shell
#1.重命名dpkg目录下的info目录
 sudo mv /var/lib/dpkg/info /var/lib/dpkg/info_qingsword

#2.创建一个新的info文件夹
 sudo mkdir /var/lib/dpkg/info

#3.执行更新操作
 sudo apt-get update && sudo apt-get -f install

#4.将更新操作产生的文件，全部复制到重命名的info_qingsword文件夹下
 sudo mv /var/lib/dpkg/info/* /var/lib/dpkg/info_qingsword

#5.删除创建的info文件夹
 sudo rm -rf /var/lib/dpkg/info

#6.将重命名的info_qingsword文件夹重新重命名为info
 sudo mv /var/lib/dpkg/info_qingsword /var/lib/dpkg/info

#7.再次执行更新操作，问题解决
  sudo apt-get update && sudo apt-get upgrade

```