---
title: rrkeePE系统安装维护工具 22.02.07
date: 2022-06-7 14:31:00
tags: WinPE
categories: WinPE
cover: https://vkceyugu.cdn.bspapp.com/VKCEYUGU-6f00c918-7a62-47b5-8e8a-9578acfb171c/23832a35-e772-44c5-ac27-0386390e7811.png
---

# rrkeePE x64温馨提示

1、rrkeePE中包含的软件版权归微软公司和软件开发者所有。
2、rrkeePE是 自制Windows PE用于工作中的环境，现在分享给大家。制作过程非常简单，请务必仔细阅读PE制作过程及步骤的全部内容;制作过程是经过无数次实践总结，让所有人都会制作使用。
3、rrkeePE只为系统安装维护为主的简单实用功能，不支持网络功能;不收费，不要流氓，无矿告,也不强迫使用。但是请尊重本人劳动成果，转贴请说明。
4、rrkeePE支 持Legacy+ MBR和UEFI+GPT引导,新旧电脑通用。并且bootx64.efi采用微软签名文件，支持主板UEFI签名安全引导。
5、台式机笔记本主板很少支持32位UEFI;为了减小PE体积及不必要的空间浪费，因此不包含32位PE。

# rrkeePE制作过程及步骤

#### 第一种制作方法

最简单，只需选择FAT32或NTFS格式化U盘为一个分区。
打开ISO包或者解压ISO包所得的全部文件复制到U盘根目录下即可使用。
FAT32、NTFS、 exFAT的区别:

1. 可以直接把rrkeePE.ISO刻盘使用。
2. 格式化为FAT32,优点:兼容性好支持Legacy/UEFI双引导;缺点: U盘不能存储大于4G单文件。
3. 格式化为NTFS,优点:支持Legacy引导PE，支持大于4G单文件;缺点:部分新主板支持NTFS引导UEFI,使用过程中NTFS对U盘有损伤。
4. 格式化为exFAT,优点:支持大于4G单文件，适合存储数据;缺点:只有部分新主板

#### 第二种制作方法

兼容性最好，格式化U盘为两个分区(第一 分区存用户数据第二分区存PE系统)。完美支持Legacy/UEFI双引导PE,又能存储大于4G单个文件。

1. 请严格按照下面步骤制作WinPE:打开ISO包或者解压ISO包得到的文件夹中找到BOOTICE .EXE 并双击打开得到下图界面。![rrkeePE](https://vkceyugu.cdn.bspapp.com/VKCEYUGU-6f00c918-7a62-47b5-8e8a-9578acfb171c/0326ac0f-abf1-4d93-ae35-7bb68f251b54.png)![rrkeePE](https://vkceyugu.cdn.bspapp.com/VKCEYUGU-6f00c918-7a62-47b5-8e8a-9578acfb171c/3747d69f-cf30-41ab-a9e4-b04eb4659c15.png)
2. 返回图1击主引得记录得到下图继续操作。![rrkeePE](https://vkceyugu.cdn.bspapp.com/VKCEYUGU-6f00c918-7a62-47b5-8e8a-9578acfb171c/2faff08c-541a-4e2d-8b96-5dffd19258ac.png)
3. 最后一步打开ISO包或者解压ISO包所得的全部文件复制到U盘FAT(FAT32)UEFI分区的根目录下即可。
   注意事项:
   (1)如果Win10/11系统不能显示两个分区;请在磁盘管理中为U盘分配盘符即可显示分区。步骤: (右键此电脑->管理- >找到并点击磁盘管理->找到没有盘符的U盘分区，右击->更改驱动器号和路径)
   (2)如果Win7、Win8系统不能显示FAT16分区，所以使用BOOTICE.EXE的“分区管理”下图界面中进行切换。![rrkeePE](https://vkceyugu.cdn.bspapp.com/VKCEYUGU-6f00c918-7a62-47b5-8e8a-9578acfb171c/0f5e4e38-dd09-4d62-a982-82597732329e.png)到这里就制作完成了。可以重启电脑进入WinPE使用了。

# rrkeePE 升级方法

不需要格式化U盘!只需要准备您已经制作好，并且能正常引导PE使用的U盘。再把新升级的rrkeePE.ISO文件包打开或解压出来的全部文件复制到U盘弓|导分区的根目录覆盖旧文件就完成了升级。
注意事项:
(1)如果Win10/11系统不能显示两个分区;请在磁盘管理中为U盘分配盘符即可显示分区。
(2)如果Win7、Win8系统不能显示FAT1 6分区，所以使用BOOTICE.EXE的“分区管理”下图界面中进行切换。![rrkeePE](https://vkceyugu.cdn.bspapp.com/VKCEYUGU-6f00c918-7a62-47b5-8e8a-9578acfb171c/a66c690f-ac0b-4e91-82c6-de73eff51e2a.png)

# rrkeePE x64文件包及升级日志

1. Win10 21H1内核更新和增加驱动程序
2. 更新7-Zip 21.07
3. 更新CPU-Z 1.99.0
4. 更新WinNTSetup 5.2.0
5. 更新CrystalDiskInfo 8.15
6. 更新Victoria 4.7.3.0
7. 更新AOMEI无损分区9.6
8. 更新Rufus 3.17.1846 U盘制作I具
9. 更新Snapshot 1.49.19073备份还原
10. 更新AIDA64 6.60.5900
11. 更新R-Studio 8.17.180.955
12. 更新Winhex 20.4
13. 众多更新...
14. 修正小bug

#### 22.02.07.iso

SHA1: 2dcc4360b8a83e2ce1ff79e345777dcc45510a67

# 下载地址

123盘提取码90kA

<div class="btn-center">
{% btn 'https://www.123pan.com/s/ZgR9-BptlA',123盘,iconfont icon-tianmao123shixiao,blue larger %}
</div>

