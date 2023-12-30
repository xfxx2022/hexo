---
abbrlink: fae88444
categories:
- - 系统工具
cover: https://blog.aidengrong.top/img/2022/11/19/VMWare-01.png
date: '2022-11-19 15:59:22'
tags:
- 系统工具
title: VMware Workstation PRO_v17.0.0_正式版
updated: '2022-11-19 15:59:22'
---
VMware Workstation 产品允许用户将 Linux、Windows 等多个操作系统作为虚拟机在单台 PC 上运行。用户可以在虚拟机上重现服务器、桌面和平板电脑环境，无需重新启动即可跨不同操作系统同时运行应用。Workstation 还提供隔离的安全环境，用于评估新的操作系统（如 Windows 10）、测试软件应用和补丁程序以及参考体系结构。 借助 Workstation 产品，可以仅从一台本地 PC 轻松测试几乎任何操作系统和应用。构建面向 Windows 10 的应用、使用任何浏览器测试兼容性，或者在无需使用移动设备的情况下部署 Android-x86 以查看移动设备行为。![VMware Workstation PRO](https://blog.aidengrong.top/img/2022/11/19/VMWare-02.png)

# 功能特点

* **vSphere 集成：** Workstation 是 vSphere 的首要配套组件。共享的 hypervisor 可为用户提供与众不同的逼真虚拟环境，从而确保应用轻松地在桌面设备、数据中心和云环境之间移动。Workstation 将洞察信息带到远程集群、数据中心和虚拟机中，还支持用户在一台 PC 上的本地实验室中将 ESXi 和 vCenter Server Appliance 作为虚拟机快速部署。
* **全新的虚拟机自动化 REST API：** 全新 REST API 利用的 API 框架与 VMware Fusion 中引入的框架相同，可在本地作为工作流的增强功能使用，或用于向远程专有服务器发出命令。提供超过 20 种运行控件，例如主机和客户机虚拟网络连接、虚拟机启动，以及从主机对源代码目录进行编程挂载时的共享文件夹管理。
* **高性能 3D 图形：** VMware Workstation Pro 支持 DirectX 10.1 和 OpenGL 3.3，可在运行 3D 应用时提供顺畅且响应迅速的体验。可在 Windows 虚拟机中以接近本机的性能运行 AutoCAD 或 SOLIDWORKS 等要求最为严苛的 3D 应用。
* **强大的虚拟网络连接：** 可使用真实的路由软件和工具，为虚拟机创建复杂的 IPv4 或 IPv6 虚拟网络，或通过与第三方软件集成来设计完整的数据中心拓扑。通过引入数据包丢失、延迟和带宽限制来测试虚拟网络模拟的应用恢复能力。
* **使用克隆进行快速复制：** 重复创建相同虚拟机设置时，可节省时间和精力，确保副本完全相同。使用“链接克隆”快速复制虚拟机，同时可显著减少所需的物理磁盘空间。使用“完整克隆”可创建能够与其他人共享的完全独立的副本。
* **有用的快照：** 创建回滚点以便实时还原，这非常适合于测试未知软件或创建客户演示。可以利用多个快照轻松测试各种不同的场景，无需安装多个操作系统。

# 新版变化

2022年11月17日 VMware Workstation 17.0 Pro 发行说明
[https://docs.vmware.com/cn/VMware-Workstation-Pro/17.0/rn/vmware-workstation-170-pro-release-notes/index.html](https://www.423down.com/go.php?url=aHR0cHM6Ly9kb2NzLnZtd2FyZS5jb20vY24vVk13YXJlLVdvcmtzdGF0aW9uLVByby8xNy4wL3JuL3Ztd2FyZS13b3Jrc3RhdGlvbi0xNzAtcHJvLXJlbGVhc2Utbm90ZXMvaW5kZXguaHRtbA==)

## 常见问题

### 碰到启动VMware客户机系统黑屏如何解决？

经总结可能原因是14版之后注册了两个LSP协议（vSockets DGRAM、vSockets STREAM）导致异常！
解决方法：使用LSP修复工具（例如：火绒安全里或ARK工具里的LSP工具）修复LSP网络协议，或者重置下网络链接Winsock，即打开命令提示符cmd.exe，输入命令netsh winsock reset，重启系统即可解决！

### 碰到启动VMware软件后假死卡住如何解决？

解决方法：可以尝试关闭系统防火墙！

# 系统要求

VM16：硬件要求高，Windows 10 或更高版64位
VM15：硬件要求中，Windows 7 或更高版64位
VM12：硬件要求低，Windows 7 或更高版64位
VM10：Windows XP 或更高版32位和64位旧版
注意：VM14版本开始不支持某些旧的电脑硬件，
会提示不支持或安装失败, 如遇到请退回12版本。

# 激活密钥

VMware激活密钥（通用批量永久激活许可）
17：JU090-6039P-08409-8J0QH-2YR7F
16：ZF3R0-FHED2-M80TY-8QYGC-NPKYF
15：FC7D0-D1YDL-M8DXZ-CYPZE-P2AY6
12：ZC3TK-63GE6-481JY-WWW5T-Z7ATA
10：1Z0G9-67285-FZG78-ZL3Q2-234JG

# 下载地址

123盘提取码5NmU

<div class="btn-center">
{% btn 'https://www.123pan.com/s/CDiA-ITOF3',123盘,iconfont icon-tianmao123shixiao,blue larger %}
</div>
