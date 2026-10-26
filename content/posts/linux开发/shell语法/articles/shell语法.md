---
title: shell语法
type: categories
categories: linux开发
cover: "../images/封面.png"
description: shell语法
swiper_index: 1
sticky: 1
abbrlink: 4652f0c6
date: 2023-09-13 00:00:00
---

* shell函数例子     start()和stop()就是函数      

```shell
#!/bin/sh
#
# Start logging
#

SYSLOGD_ARGS=-n
KLOGD_ARGS=-n
[ -r /etc/default/logging ] && . /etc/default/logging

start() {
        printf "Starting logging: "
        start-stop-daemon -b -S -q -m -p /var/run/syslogd.pid --exec /sbin/syslogd -- $SYSLOGD_ARGS
        start-stop-daemon -b -S -q -m -p /var/run/klogd.pid --exec /sbin/klogd -- $KLOGD_ARGS
        echo "OK"
}

stop() {
        printf "Stopping logging: "
        start-stop-daemon -K -q -p /var/run/syslogd.pid
        start-stop-daemon -K -q -p /var/run/klogd.pid
        echo "OK"
}

case "$1" in    #这里就是执行脚本的时候，后后面带的参数， 如果带了start参数就执行start函数  
                               #$1就是取传入的第一个参数。$0是取脚本的名字（包括了路径）
  start)
        cat /etc/os-release
        start
        ;;
  stop)
        stop
        ;;
  restart|reload)
        stop
        start
        ;;
  *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
esac

```

* 扩展
  $PS1可以用来修改命令行的提示符。
  $?可以用来获取一个函数的返回值，上一个命令的返回状态。   

 # 易错问题
 判断，变量，各种语句之间尽量加上空格。 