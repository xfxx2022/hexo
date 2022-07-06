---
title: Ventoy v1.0.78 开源多合一启动盘工具
tags: 系统工具
categories: 系统工具
cover: >-
  https://vkceyugu.cdn.bspapp.com/VKCEYUGU-6f00c918-7a62-47b5-8e8a-9578acfb171c/ea5353e7-d987-432b-9e02-7350597e9a10.png
abbrlink: 50615
date: 2022-07-06 13:20:00
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

* 2022/07/01 --- 1.0.78 发布

1. 改进 `启动配置替换插件`，现在最多支持替换2个文件。[说明](https://ventoy.net/cn/plugin_bootconf_replace.html#replace_more_files)
2. 更新 Super-UEFIinSecureBoot-Disk 到 v3.4 (#1695)
3. `.ventoyignore` 在 F2 浏览模式下也可以生效。
4. 修复了启动最新 KaOS 时的一个BUG。 (#1696)
5. 修复了启动 TrueNAS Core 13.0 时的一个BUG。(#1684)
6. 修复了启动 StorageCraft StorageProtect SPX 时的一个BUG。(#1683)
7. 在 VentoyPlugson 页面上设置文件夹路径时自动剔除末尾多余的斜杠。
8. languages.json 更新
9. 新增 ISO 支持 (累计 920+)
10. 文档：[如何删除 Ventoy 导入的安全启动 Key](https://ventoy.net/cn/doc_delete_key.html)

# 下载地址

Ventoy v1.0.76 for Win / Linux / Livecd (2022/06/12)
[https://github.com/ventoy/Ventoy/releases](https://github.com/ventoy/Ventoy/releases)
U盘启动工具 Ventoy v1.0.78 x86-x64 便捷版单文件
123盘提取码ftbT
蓝奏网盘提取码hpnv

<div class="btn-center">
{% btn 'https://www.123pan.com/s/CDiA-BDNF3',123盘,iconfont icon-tianmao123shixiao,blue larger %}
{% btn 'https://wwu.lanzoub.com/b0374fyhg',蓝奏网盘,iconfont icon-yunpan,pink larger %}
</div>

