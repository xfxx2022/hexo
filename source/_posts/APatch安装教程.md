---
abbrlink: ''
categories:
- - Android
date: '2024-04-27T12:14:18.702012+08:00'
tags: []
title: APatch安装教程
updated: '2024-04-27T12:40:05.888+08:00'
---
**APatch** 理论上支持 内核版本 **3.18 – 6.1**，修补 **boot.img** 刷入即可。
大致思路：解锁Bootloader > 修补boot.img > fastboot刷入修补文件

---

演示步骤：

1、小米解锁 **Bootloader**：[Xiaomi-unlock](https://blog.1314151.xyz/posts/cddc0cd1/)

2、下载系统包：[rom](https://blog.1314151.xyz/posts/bbbc0c01/)（一定要下载和手机系统版本一致的系统包）

3、提取**boot.img**：[payload-dumper-go-boot](https://blog.1314151.xyz/posts/7d0bfba5/)（如果系统包有 **boot.img**，可以跳过此步骤）

4、手机插电脑，文件传输模式，复制 **boot.img** 到手机 **Download** 目录

5、手机下载 **APatch** APP 安装：[APatch-download]([https://github.com/bmax121/APatch/releases](https://blog.1314151.xyz/file/APatch/APatch_10657_10657-release-signed.apk))
[APatch-download-github](https://github.com/bmax121/APatch/releases)

6、手机打开 **APatch**，①：安装 – ②：选择 **boot.img** – ③：输入超级密钥，开始修补 – ④：修补完成（修补生成 **apatch\_patched-xxx.img** 文件在 **Download** 目录）
![https://blog.1314151.xyz/img/2024/04/27/5202564f7c857caf5c06f131ab468fee_8a8bb7cd343aa2a_a0a02ce6e00cd9cf742f4620db012b1b.jpg](https://blog.1314151.xyz/img/2024/04/27/5202564f7c857caf5c06f131ab468fee_8a8bb7cd343aa2a_a0a02ce6e00cd9cf742f4620db012b1b.jpg)
7、电脑下载 **adb-fastboot**：[蓝奏盘]([https://mrzzoxo.lanzoui.com/b02plghuh](https://blog.1314151.xyz/file/Adb_fastboot/adb-fastboot.zip))（解压出来）
8、手机打开 文件传输模式，打开 **Download** 目录，把 **apatch.img** 复制到电脑 **adb-fastboot** 目录
![https://blog.1314151.xyz/img/2024/04/27/7358930d2ec6601316eec0fa7c020f00_693a9fdd4c2fd07_c79df42857fb7aa337ae10fd5644de7e.png](https://blog.1314151.xyz/img/2024/04/27/7358930d2ec6601316eec0fa7c020f00_693a9fdd4c2fd07_c79df42857fb7aa337ae10fd5644de7e.png)9、手机进入 **Bootloader** 模式，再插入电脑。
（手机关机，电源键+音量下键，两个键长按）
![https://blog.1314151.xyz/img/2024/04/27/3cc2697dd84af9a3a579728f08cd4b68_78805a221a988e7-5_8fe5baeca2dc463ee40c26cc9e7c1c01.png](https://blog.1314151.xyz/img/2024/04/27/3cc2697dd84af9a3a579728f08cd4b68_78805a221a988e7-5_8fe5baeca2dc463ee40c26cc9e7c1c01.png)10、打开“**打开CMD命令行.bat**”，输入下面的命令
apatch.img 每次修补的名字都不一样，使用的时候请输入生成的名字。

```
fastboot flash boot 修补文件
```

11、输出下面这三行代码，就是成功刷入了。再使用指令 `fastboot reboot` 重启手机。

```
Sending 'boot' (196608 KB) OKAY [ 4.697s]
Writing 'boot'             OKAY [ 0.512s]
Finished. Total time: 5.235s
```

![https://blog.1314151.xyz/img/2024/04/27/4fb4abf0bf7d2b5053686ca853f2a54d_9d607a663f3e9b0_902ada0a7645595b1f40988cee66fed4.png](https://blog.1314151.xyz/img/2024/04/27/4fb4abf0bf7d2b5053686ca853f2a54d_9d607a663f3e9b0_902ada0a7645595b1f40988cee66fed4.png)12、手机开机 打开 **APatch** ，①：输入 超级密钥 – ②：安装 系统补丁 – ③：生效中😀 成功刷入
![https://blog.1314151.xyz/img/2024/04/27/e387da6a3e20d8c1b502d428f13b8495_894f782a148b33a_d07bed2dff969316bffa576905e43cb2.jpg](https://blog.1314151.xyz/img/2024/04/27/e387da6a3e20d8c1b502d428f13b8495_894f782a148b33a_d07bed2dff969316bffa576905e43cb2.jpg)

---

温馨提示:
如果刷入 **apatch.img** 不能开机，可以把前面提取的 **boot.img** 通过 **fastboot** 刷回去，恢复原 **boot**，一般都能正常开机！
**boot.img** 保留一份在电脑，避免出问题了可以自救下！还原boot指令

```
fastboot flash boot boot.img
```

后期系统更新，直接下载全量完整包升级，然后重复上面的步骤就可以继续愉快的使用**APatch**了！

