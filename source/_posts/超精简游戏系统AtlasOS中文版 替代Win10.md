---
abbrlink: ''
categories:
- - 第三方作者系统
cover: https://blog.aidengrong.top/img/2022/12/11/AtlasOS.png
date: '2022-12-11 14:07:25'
tags:
- 第三方作者系统
title: 超精简游戏系统AtlasOS中文版 替代Win10
updated: '2022-12-11 16:04:20'
---
# Atlas 是什么?

Atlas 是一个魔改版本的 Windows，删除了众多拖慢 Windows 系统的组件（游戏性能下降的罪魁祸首）。Atlas 是一个透明且开源的项目，致力于为玩家争取平等的权利，无论您是在土豆，还是高性能 PC 上运行。Atlas 在主要优化性能的同时，也同时是减少系统，网络，输入延迟的一个极佳选择。![AtlasOS](https://blog.aidengrong.top/img/2022/12/11/AtlasOS.png)

# Windows 对比 Atlas

## **隐私**

Atlas 删除了 Windows 中嵌入的所有类型的跟踪，并在部署时强制执行数百个组策略以最小化数据收集。我们无法保证除 Windows 系统之外的隐私问题，例如您访问的网站。

## **安全性**

Atlas 的目标是在不损失性能的情况下保证系统尽可能的安全。我们通过禁用可能泄露信息或被利用的功能来做到这一点。但也有一些例外，比如 [Spectre](https://spectreattack.com/spectre.pdf), 和[Meltdown](https://meltdownattack.com/meltdown.pdf). 您需要禁用这些缓解措施以提高性能。 如果该安全缓解措施降低了性能，我们将会禁用该措施。 以下是一些被修改的功能/缓解措施，如果它们包含(P)，则表示其安全风险已被修复:

## **精简**

Atlas 删除了大量预先安装的应用程序和其他组件。尽管这可能会破坏一些兼容性，但它会显著减少镜像的大小 (例如删除 Windows Defender 之类的功能)。这种修改是主要针对游戏的。但大多数教育和工作程序（理论上）都可以工作。

## **性能**

Atlas 预先调整了一些东西。在保持兼容性的同时，也在努力提高其性能，我们把每一滴可能压榨性能的点点滴滴都压缩到了 Windows 映像中。下面列出了我们为改进 Windows 所做的许多改变中的一些。

* 定制的电源计划
* 最小化的服务程序
* 最小化的驱动程序
* 禁用无需的驱动程序
* 删除节电功能
* 禁用影响性能的安全缓解措施
* 自动启用 MSI（信息信号中断）模式
* 引导配置优化
* 优化的线程调度

# 下载地址

123盘提取码bqgb

<div class="btn-center">
{% btn 'https://www.123pan.com/s/ZgR9-TWtlA',123盘,iconfont icon-tianmao123shixiao,blue larger %}
</div>
