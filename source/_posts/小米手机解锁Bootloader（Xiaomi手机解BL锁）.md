---
abbrlink: ''
categories:
- - Android
date: '2024-04-27T10:59:44.328389+08:00'
tags: []
title: 小米手机解锁Bootloader（Xiaomi手机解BL锁）
updated: '2024-04-27T10:59:45.753+08:00'
---
解锁Bootloader会**清除手机数据**，有重要数据请备份再操作！！！

---

解锁步骤：

一、开启 开发者选项：1.我的设备 – 2.全部参数 – 3.连击MIUI版本

![https://blog.1314151.xyz/img/2024/04/27/3d123eba8c2a3d7326ca3efa13942f2e_c10d778311b8b0d_f3e344b33804523c7cccaf8ce727b874.jpg](https://blog.1314151.xyz/img/2024/04/27/3d123eba8c2a3d7326ca3efa13942f2e_c10d778311b8b0d_f3e344b33804523c7cccaf8ce727b874.jpg)
二、1.更多设置 – 2.开发者选项 – 3.设备解锁状态 – 4.绑定账号和设备
![https://blog.1314151.xyz/img/2024/04/27/ff4c193f76373f0ae1e8030e7dc1eb60_b464a4330bc7e34_b5ab4b255c79a3d15d8be01fc7930e21.jpg](https://blog.1314151.xyz/img/2024/04/27/ff4c193f76373f0ae1e8030e7dc1eb60_b464a4330bc7e34_b5ab4b255c79a3d15d8be01fc7930e21.jpg)
三：下载小米解锁工具：​**[Miflash\_Unlock\_7.6.727.43.zip](https://cdn.cnbj1.fds.api.mi-img.com/flash-tool/miflash_unlock_7.6.727.43.zip)**​，解压出来，打开 **MiUsbDriver.exe** （驱动安装程序）
![https://blog.1314151.xyz/img/2024/04/27/72f17d0a1fd2129ff0d90898af9fde44_c4496a4a6fe047d_e2993dc45bc19af9070d7d54fa5e4009.png](https://blog.1314151.xyz/img/2024/04/27/72f17d0a1fd2129ff0d90898af9fde44_c4496a4a6fe047d_e2993dc45bc19af9070d7d54fa5e4009.png)四、打开 **miflash\_unlock.exe**，登录小米账号

![https://blog.1314151.xyz/img/2024/04/27/f1c2de67d82935fd61dd42a42533c8a6_5f39c513df33c74_287ef3e5a046177c4741f4d965e5c819.jpg](https://blog.1314151.xyz/img/2024/04/27/f1c2de67d82935fd61dd42a42533c8a6_5f39c513df33c74_287ef3e5a046177c4741f4d965e5c819.jpg)

![https://blog.1314151.xyz/img/2024/04/27/b1a9d3e858389eaa5da6a2184b5a056a_b30535ad66cbdd3_4fc5bbee9e43dae619c96ebdb1d28be6.jpg](https://blog.1314151.xyz/img/2024/04/27/b1a9d3e858389eaa5da6a2184b5a056a_b30535ad66cbdd3_4fc5bbee9e43dae619c96ebdb1d28be6.jpg)
五：手机进入 **Bootloader** 模式，再插入电脑。
（手机关机，电源键+音量下键，两个键长按）

![https://blog.1314151.xyz/img/2024/04/27/031384677353a743ed672e357fef691b_a4381a987eb897e_8fe5baeca2dc463ee40c26cc9e7c1c01.png](https://blog.1314151.xyz/img/2024/04/27/031384677353a743ed672e357fef691b_a4381a987eb897e_8fe5baeca2dc463ee40c26cc9e7c1c01.png)
六：手机数据线插到电脑，点击 ​**解锁**​（解锁会清除手机数据）

![https://blog.1314151.xyz/img/2024/04/27/978233e349ef91b8ea0d141e0ab4b5a3_a045e10674b1c2f_457503b5d6071a2e5992ee6c01594bad.jpg](https://blog.1314151.xyz/img/2024/04/27/978233e349ef91b8ea0d141e0ab4b5a3_a045e10674b1c2f_457503b5d6071a2e5992ee6c01594bad.jpg)
七：解锁成功（第一次开机会有点慢）
![https://blog.1314151.xyz/img/2024/04/27/c202788722b5231d9a89dc16ba18869c_eb33511de4ac052_3c30b13df78c66ea5df81f474f9d1637.png](https://blog.1314151.xyz/img/2024/04/27/c202788722b5231d9a89dc16ba18869c_eb33511de4ac052_3c30b13df78c66ea5df81f474f9d1637.png)
**解锁过程中可能遇到的问题：**

Q：解锁工具提示“账号设备不一致”是怎么回事？
A：这是在解锁过程中没有通过账号与设备验证，解决办法是先将手机升级到最新的稳定版或者从稳定版卡刷到最新的开发版，在待解锁的设备和解锁工具上要登陆同一个账号，并进入“设置 -> 开发者选项 -> 设备解锁状态”中绑定账号和设备。

Q：解锁工具提示“无法获取手机信息”是怎么回事？
A：这种情况一般是电脑上的设备驱动没有装好，可以尝试重插USB线或者换个USB接口或者换根USB线来等待电脑慢慢安装驱动，或在工具右上角驱动安装模块中主动安装驱动。

Q：解锁失败显示“账号与设备的绑定时间太短，xxx个小时后再解锁”
A：在售的新机型一般需要等待，用户账号安全评分较低的需要等待，等待时间目前是7天起，如果本年度解锁手机数超过2台，等待时间会相应增长。

Q：解锁失败显示“此账号本月解锁次数达到上限”
A：一个小米账号每月限制解锁一台设备。

Q：解锁失败显示“此账号本年累计解锁次数已达上限”
A：一个小米账号每年限制解锁4台不同设备。

Q：解锁失败显示“账号权限不足或者账号受限”
A：账号存在安全风险，无法处理解锁操作，建议更换账号。

Q：解锁失败显示“未知错误-1”
A：网络异常，请更换时间段或更换网络进行解锁。

