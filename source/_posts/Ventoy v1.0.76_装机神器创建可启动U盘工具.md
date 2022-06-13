---
title:  [Ventoy v1.0.76_装机神器创建可启动U盘工具]
date: 2022-06-13 14:20:00
tags: 系统工具
categories: 系统工具
cover: https://vkceyugu.cdn.bspapp.com/VKCEYUGU-6f00c918-7a62-47b5-8e8a-9578acfb171c/5c364084-6776-4885-89ec-0cbf48fb4387.png
---

Ventoy是一个制作可启动U盘的开源工具。

- 有了Ventoy你就无需反复地格式化U盘，你只需要把ISO/WIM/IMG/VHD(x)/EFI 等类型的文件直接拷贝到U盘里面就可以启动了，无需其他操作。
- 你可以一次性拷贝很多个不同类型的镜像文件，Ventoy 会在启动时显示一个菜单来供你进行选择。
- 你还可以在 Ventoy 的界面中直接浏览并启动本地硬盘中的 ISO/WIM/IMG/VHD(x)/EFI 等类型的文件。
- Ventoy 安装之后，同一个U盘可以同时支持 x86 Legacy BIOS、IA32 UEFI、x86_64 UEFI、ARM64 UEFI 和 MIPS64EL UEFI 模式，同时还不影响U盘的日常使用。
- Ventoy 支持大部分常见类型的操作系统（Windows/WinPE/Linux/ChromeOS/Unix/VMware/Xen ...）

# 软件截图

![Ventoy](https://vkceyugu.cdn.bspapp.com/VKCEYUGU-6f00c918-7a62-47b5-8e8a-9578acfb171c/ea5353e7-d987-432b-9e02-7350597e9a10.png)

# 特点描述

News . Ventoy
[http://ventoy.net/cn/doc_news.html](http://ventoy.net/cn/doc_news.html)
完全开源免费，使用简单
快速 (拷贝文件有多快就有多快)
直接从ISO文件启动，无需解开
无差异支持Legacy + UEFI 模式
UEFI 模式支持安全启动 (Secure Boot) (1.0.07+)
支持持久化 (1.0.11版本开始) 说明
支持直接启动WIM文件(Legacy + UEFI) (1.0.12+)
支持MBR和GPT分区格式(1.0.15+)
支持自动安装部署(1.0.09+)
支持超过4GB的ISO文件
保留ISO原始的启动菜单风格(Legacy & UEFI)
支持大部分常见操作系统, 已测试300+ 个ISO文件
不仅仅是启动，而是完整的安装过程
ISO文件支持列表模式或目录树模式显示 说明
提出 "Ventoy Compatible" 概念
支持插件扩展
启动过程中支持U盘设置写保护
不影响U盘日常普通使用
版本升级时数据不会丢失
无需跟随操作系统升级而升级Ventoy

# 注意问题

1、ISO文件放U盘任意目录或子目录，~~但全路径(包括目录和ISO文件名)中不能有中文或空格~~。
2、Win下如果一直安装失败，可先用分区工具把U盘分区全删除再把启动模式改为HDD再试。
3、关于兼容性的问题，部分老机器上可能存在兼容性问题。

# 更新日志

2022/06/12 --- 1.0.76 发布

1. 安装 Ventoy 时默认开启 安全启动支持 选项。[说明](https://www.ventoy.net/cn/doc_secure.html)
2. 升级 Super UEFIinSecureBoot Disk v3-3 以解决安全启动时导入 key 失败的问题。
3. 根据ISO文件名中的特殊标识自动使用 memdisk/grub2/wimboot 模式。[说明](https://www.ventoy.net/cn/doc_name_identifier.html)
4. 修复了 Legacy BIOS 模式下 使用 F2或ventoy_grub.cfg 启动 Linux vDisk (.vtoy) 文件时的一个BUG。
5. 支持 EasyOS 首次启动时的分区自动扩展。
6. 支持 EasyOS 4.0
7. 支持 Stratodesk NoTouch OS. (#1652)
8. 更新 languages.json
9. 新增 ISO 文件支持 (累计 900+)

# 下载地址

Ventoy v1.0.76 for Win / Linux / Livecd (2022/06/12)
[https://github.com/ventoy/Ventoy/releases](https://github.com/ventoy/Ventoy/releases)
U盘启动工具 Ventoy v1.0.76 便捷版单文件
[123盘](https://www.123pan.com/s/CDiA-BDNF3)
提取码

```
ftbT
```

[蓝奏网盘](https://wwu.lanzoub.com/b0374fyhg)
提取码

```
hpnv
```
