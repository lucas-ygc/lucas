---
title: wsl迁移
type: categories
categories: 开发方法
cover: "../images/封面.png"
abbrlink: 303f5b2b
description: 技巧类
typora-root-url: ./..\..\..
date: 2022-10-29 00:00:00
swiper_index:
---
# wsl 安装
wsl --install -d 发行版名

# wsl迁移
wsl安装好后，利用rsync将数据同步到wsl中。

# 查看虚拟机
wsl -l -v

# 关闭虚拟机
wsl --shutdown 

# 启动虚拟机
wsl -d ubuntu

#  配置wsl桥接网络脚本
```shell
# 1. 创建WSL桥接交换机 绑定【以太网】
New-VMSwitch -Name "WSLBridge" -NetAdapterName "以太网" -AllowManagementOS $true

# 2. 关闭WSL
wsl --shutdown

# 3. 写入.wslconfig 桥接配置
$wslConf = @"
[wsl2]
networkingMode=bridged
vmSwitch=WSLBridge
dnsTunneling=true
"@
$confPath = "$env:USERPROFILE\.wslconfig"
Set-Content -Path $confPath -Value $wslConf -Encoding UTF8

## 4. 再次关闭生效
wsl --shutdown

Write-Host "✅ Win11 桥接配置完成，请打开WSL执行下面Linux脚本"
```

# 配置ubunt网络脚本
```shell
# 安装ifconfig工具
sudo apt update -y && sudo apt install net-tools -y

# 清空旧IP、设置固定静态IP 192.168.8.215
sudo ifconfig eth0 0.0.0.0 down
sudo ifconfig eth0 192.168.8.215 netmask 255.255.255.0 up

# 设置网关
sudo route add default gw 192.168.8.1 eth0

# 固定DNS
sudo chattr -i /etc/resolv.conf
echo "nameserver 223.5.5.5" | sudo tee /etc/resolv.conf
sudo chattr +i /etc/resolv.conf


sudo rm /etc/resolv.conf
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
echo "nameserver 223.5.5.5" | sudo tee -a /etc/resolv.conf

echo "✅ WSL桥接静态IP配置完成：192.168.8.215"(base)
```


# 迁移备份配置
## WSL 完整备份 + 还原 全套操作（Win11 原生，简单稳、不丢桥接/IP/NFS配置）
## 一、先关闭 WSL（备份必须先关）
管理员 PowerShell：
```powershell
wsl --shutdown
```

## 二、查看你的 WSL 发行版名称
```powershell
wsl --list --verbose
```
一般是：`Ubuntu-22.04` / `Ubuntu-24.04`

---

## 三、一键导出备份（打包成完整镜像，所有配置全保存）
### 格式
```powershell
wsl --export 发行版名 保存路径\备份文件名.tar
```

### 给你直接写好（复制就能用）
```powershell
# 举例：备份 Ubuntu-22.04 到D盘
wsl --export Ubuntu-22.04 D:\WSL_Backup\wsl_ubuntu_full_bak.tar
```
- 会把：**桥接配置、NFS、固定IP、所有软件、代码、配置** 全部打包
- 纯离线镜像，换电脑/重装系统都能恢复

---

## 四、日常快速备份建议
1. 专门建文件夹
```powershell
mkdir D:\WSL_Backup
```
2. 每次改完环境（NFS/网络/开发环境）就跑一次导出
几分钟搞定，体积看你占用，一般 5~20G

---

## 五、以后需要还原（一键恢复）
1. 先删掉坏掉的旧 WSL（可选）
```powershell
wsl --unregister Ubuntu-22.04
```
2. 导入恢复
```powershell
wsl --import Ubuntu-22.04 D:\WSL_Env D:\WSL_Backup\wsl_ubuntu_full_bak.tar --version 2
```
- 第一个路径：WSL 存放目录
- 第二个路径：你备份的 tar 文件

---

## 六、重点：备份后哪些东西不会丢
✅ 桥接网络模式
✅ 固定IP脚本、ifconfig、网关
✅ NFS 服务、/etc/exports 配置
✅ 所有安装的工具、编译器、开发依赖
✅ 用户文件、权限

---

## 七、补充：只备份文件（小体积，可选）
如果不想打包整个系统，只想备份代码/配置：
WSL 内打包：
```bash
tar -zcvf ~/wsl_file_bak.tar.gz /mnt/nfs /etc/exports /etc/wsl-start-ip.sh
```

---


# 换阿里源
```
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak

sudo tee /etc/apt/sources.list >/dev/null <<'EOF'
deb http://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ jammy-backports main restricted universe multiverse
EOF

sudo apt update(base)

```


# 创建vhdx虚拟磁盘给wsl使用
第一步、磁盘管理器中创建VHD，需要选择vhdx,创建完成后选择分离，否则会显示被其他进程占用   
第二步、powershell执行。wsl --mount --vhd "位置" --bare   
如果要卸载，使用wsl --unmount 
如果要扩容，就直接用磁盘管理器扩容，
如果要变小，就i直接创建个新的挂载，把数据拷贝过去。


# 关于所有权问题
用户和文件权限在WSL备份和恢复过程中通常会保留，但有时可能会遇到权限问题。可以使用以下命令来修复权限：

```bash
sudo chown -R $USER:$USER /home/$USER
```

这将递归地更改当前用户主目录下的所有文件和文件夹的所有权为当前用户。最好实在上一级目录执行此命令，以免后续的文件夹权限被改变。



# 配置wsl内存和cpu
```shell
[wsl2]
# --- 网络配置 (保持你的桥接设置) ---
networkingMode=bridged
vmSwitch=WSLBridge
dnsTunneling=true

# --- 性能配置 ---
memory=44GB           # 稍微保守一点点，留出 4GB 给 Windows 确保宿主机绝对流畅
processors=22         # 留 2 个核给 Windows，防止界面卡死
swap=16GB             # 保持 16GB，足够应对大多数模型加载
# autoMemoryReclaim=disabled  <-- 建议删除或注释掉，让系统自动管理更稳妥
# cpuPerformanceMode=high     <-- WSL2 默认就是高性能，此项非必须，除非你确定需要强制模式
localhostForwarding=true      # 建议开启，方便 Windows 访问 WSL 端口
```

```shell
#开机后运行 查看
free -h 
```