---
abbrlink: ''
categories:
- - Android
date: '2024-04-27T11:42:51.565888+08:00'
tags: []
title: payload-dumper-go提取boot（payload提取boot.img）
updated: '2024-04-27T11:54:07.696+08:00'
---
1、下载手机系统包：[rom](https://blog.1314151.xyz/posts/bbbc0c01/)（一定要下载和手机系统版本一致的系统包）
2、下载[**payload-dumper-go-64**](https://blog.1314151.xyz/file/payload-dumper-go-64.zip))，下载[**payload-dumper-go-32**](https://blog.1314151.xyz/file/payload-dumper-go-32.zip))（解压出来）
3、解压系统包（只需要payload.bin文件）
4、复制 **payload.bin **文件到 **payload-dumper-go** 文件夹里面
![https://blog.1314151.xyz/img/2024/04/27/abbb6d60aec99d0ad1e24d1194a45a6d_2efa273a75fd6b7_4df43a87533df778fe9273f95d79ab24.jpg](https://blog.1314151.xyz/img/2024/04/27/abbb6d60aec99d0ad1e24d1194a45a6d_2efa273a75fd6b7_4df43a87533df778fe9273f95d79ab24.jpg)5、打开CMD命令行
![https://blog.1314151.xyz/img/2024/04/27/6e72626c6f90e0c6a4756e775555c093_35beee9e1b2e940_0dc765b680e90d42e3cb479994e43480.jpg](https://blog.1314151.xyz/img/2024/04/27/6e72626c6f90e0c6a4756e775555c093_35beee9e1b2e940_0dc765b680e90d42e3cb479994e43480.jpg)6、按照提示输入 b
![https://blog.1314151.xyz/img/2024/04/27/e8cfd5eeb0d3010fef43cf1076d20326_1bc49334127f327_cda7d633a6fbb129c26dddd0a65d088b.jpg](https://blog.1314151.xyz/img/2024/04/27/e8cfd5eeb0d3010fef43cf1076d20326_1bc49334127f327_cda7d633a6fbb129c26dddd0a65d088b.jpg)7、提取成功
![https://blog.1314151.xyz/img/2024/04/27/61a9802351cb5e6ec2dfb0150fac7068_9f415bbcdc6445c_4e5b5890eafbab979685ac4adee8e264.jpg](https://blog.1314151.xyz/img/2024/04/27/61a9802351cb5e6ec2dfb0150fac7068_9f415bbcdc6445c_4e5b5890eafbab979685ac4adee8e264.jpg)8、打开 **img** 文件夹 就可以看到提取的 **boot.img** 了

