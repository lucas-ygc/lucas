---
title: nfs挂载文件出错
type: categories
categories: 问题总结
cover: "../images/封面.png"
abbrlink: be6530dc
description: 工作学习过程中的错误解决方案
swiper_index: 1
typora-root-url: ./..\..\..
date: 2022-10-29 00:00:00
---

在uboot中设置
```
bootargs,setenv bootargs 'console=ttymxc0,115200 root=/dev/nfs nfsroot=192.168.8.213:/home/ygc/Desktop/driver/nfs/rootfs,proto=tcp rw ip=192.168.8.50:192.168.8.213:192.168.8.1:255.255.255.0::eth0:off'

```
但是引导后出现nfs挂载网络根文件系统是出现错误。

```
Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(2,0)
---[ end Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(2,0)
random: nonblocking pool is initialized

```
经过各种试验发现是nfs服务的问题。

原因是：ubuntu18.04只支持nfs 3和nfs 4，而uboot默认使用nfs 2。

解决方法：

在ubuntu16.04以上的 “/etc/default/nfs-kernel-server” 文件末尾加一行，如图所示。

```  
# Number of servers to start up
RPCNFSDCOUNT="-V 2 8"

# Runtime priority of server (see nice(1))
RPCNFSDPRIORITY=0

# Options for rpc.mountd.
# If you have a port-based firewall, you might want to set up
# a fixed port here using the --port option. For more information, 
# see rpc.mountd(8) or http://wiki.debian.org/SecuringNFS
# To disable NFSv4 on the server, specify '--no-nfs-version 4' here
RPCMOUNTDOPTS="-V 2 --manage-gids"

# Do you want to start the svcgssd daemon? It is only required for Kerberos
# exports. Valid alternatives are "yes" and "no"; the default is "no".
NEED_SVCGSSD=""

# Options for rpc.svcgssd.
RPCSVCGSSDOPTS=""
RPCSNFSDOPTS="--nfs-version 2,3,4 --debug --syslog"


```
上面的之对ubuntu20.04以前的版本生效


20.04以后的版本需要将sudo vim /etc/nfs.conf,没有就自己创建一份
中的将文件中的udp和ver2打开
``` 
[nfsd]
# debug=0
# threads=8
# host=
# port=0
# grace-time=90
# lease-time=90
udp=y
# tcp=y
vers2=y
# vers3=y
# vers4=y
# vers4.0=y
# vers4.1=y
# vers4.2=y
# rdma=n
# rdma-port=20049
```
ubuntu22.04无法开启v2，已经验证  

查看版本
cat /proc/fs/nfsd/versions