---
abbrlink: b21e2d25
categories:
  - - WinPE
cover: >-
  https://blog.aidengrong.top/img/2022/11/07/98792aa8029d653f5e2d3fdee31a07fd3f0fe8da.jpg
date: '2022-11-07 15:08:26'
tags:
  - WinPE
title: FirPE-V1.8.1维护系统
updated: '2022-11-07 15:08:26'
---
FirPE 是一款系统预安装环境（Windows PE），它具有简约、易操作等特点，使用起来十分人性化。以U盘作为使用载体，空间更为充分，携带更为方便。同时整合各种装机必备工具，有效提高系统安装效率。FirPE 将为大家带来全新的用户体验！

采用经过优化的U盘三分区方案，同时支持BIOS（Legacy）与UEFI两种启动模式。结合一贯的“双PE分治”理念，两个PE分别接管不同的硬件范围，可在支持主流硬件的基础上，同时兼容以往多数旧硬件。U盘WinPE所在分区于系统下自动隐藏，WinPE区与数据区分别独立，便于使用者对数据的各项操作。![FirPE](https://blog.aidengrong.top/img/2022/11/07/98792aa8029d653f5e2d3fdee31a07fd3f0fe8da.jpg)

### V1.8.1（2021.12.12）

**Win11PE**

* 变更 Win11PE内核为22000.348
* 变更 X盘卷标为WinPE
* 变更 Notepad3为Notepad2
* 更新 EasyRC-V2.0.8
* 更新 WinNTSetup
* 更新 IT天空万能驱动屏蔽插件
* 新增 桌面硬件信息显示
* 新增 从本地系统加载驱动选项
* 修复 DriverIndexer加载部分驱动失败BUG
* 修复 部分环境黑屏BUG
* 修复 插件分类后无法加载插件BUG
* 修复 部分显示屏超出范围BUG
* 修复 外置程序找不到不提示BUG
* 修复 运行外置绿色程序重复运行BUG
* 修复 部分程序图标无法显示BUG
* 修复 宽带拨号无法正常使用BUG
* 修复 右键任务栏崩溃BUG
* 修复 MTP无法使用BUG
* 修复 Rndis无法使用BUG
* 修复 网络共享无法使用BUG
* 修复 微信无法运行BUG
* 修复 轻松备份无法运行BUG
* 修复 IDM运行报错BUG
* 优化 系统图标
* 优化 驱动加载速度
* 优化 连接WIFI界面

**ISO合盘**

* 更新 Grldr
* 修复 部分环境无法启动本地系统BUG
* 优化 UEFI启动菜单顺序

**FirPE写入器**

* 更新 Ventoy-V1.0.62
* 更新 Rufus-V3.17
* 更新 UltralISO-V9.7.6.3829
* 修复 部分环境下初始化错误BUG
* 修复 无法识别Windows11 BUG
* 修复 部分环境下生成ISO卡住BUG
* 修复 网启失败BUG
* 修复 本地安装启动失败BUG
* 修复 自定义 UD区大小、EFI区大小 无效BUG
* 修复 EFI区大小无法大于2GB
* 修复 任务栏进度不显示BUG
* 优化 写入模式兼容性
* 优化 还原空间
* 优化 本地安装
* 优化 本地卸载
* 优化 Ventoy写入模式
* 优化 进度条显示
* 优化 网启脚本
* 优化 系统盘容量检测

大小: 779644952 字节
文件版本: 1.8.1.0
修改时间: 2021年12月17日, 21:52:40
MD5: 2CC72E535A8B8575BB240A3E4869F759
SHA1: 1792478AE6D17BEC3C07DAF5DC4FFBE0C612765F
CRC32: 55D12804

# 下载地址

123盘提取码zlk6

<div class="btn-center">
{% btn 'https://www.123pan.com/s/ZgR9-bPtlA',123盘,iconfont icon-tianmao123shixiao,blue larger %}
</div>
