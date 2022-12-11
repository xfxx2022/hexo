---
abbrlink: ''
categories:
- - 教程
cover: https://blog.aidengrong.top/img/2022/12/11/huise.png
date: '2022-12-11 16:08:37'
tags:
- 教程
title: 一个css样式让网站哀悼变灰
updated: '2022-12-11 16:16:32'
---
在发生重大哀悼事件时候，需要紧急将网站变灰以示哀悼，在此给大家总结了几种方法，通过简单修改一下站点样式即可实现。

grayscale() : 对图片进行灰度转换，grayscale是 <filter-function> 的子属性，当100%参数时候的效果如下：

![huise](https://blog.aidengrong.top/img/2022/12/11/huise.png)最简单地把页面的<html>开始标签中间之间加：

```
style="-webkit-filter: grayscale(100%);"
```

或者修改站点CSS样式

```
html {-webkit-filter: grayscale(100%);filter:progid:DXImageTransform.Microsoft.BasicImage(graysale=1);}
```

将上述代码添加加到CSS最顶端就可以实现。

为了兼容多种浏览器标准，可以增加一下样式：

```
html {
-webkit-filter: grayscale(100%);
-moz-filter: grayscale(100%);
-ms-filter: grayscale(100%);
-o-filter: grayscale(100%);
filter:progid:DXImageTransform.Microsoft.BasicImage(grayscale=1);
_filter:none;
}
```

如果网站后台无法定义CSS样式，这需要在站点模板页的head标签中间插入style标志位：

```
<style>
html{-webkit-filter: grayscale(100%);}
</style>
```

对于一些老的网站，为了支持该函数需要修改html标头，将其修改为最新标准标头才可以：对一些使用Flash（不在建议使用）的老站点，起颜色可能也不支持CSS滤镜变灰，则需要在可以在FLASH代码的<object …>和之间插入：

```
<param value="false" name="menu"/>
<param value="opaque" name="wmode"/>
```

Nginx代理

对于一下没有办法修改源站代码的情况下，也可以在Nginx站点代理无服务器上，通过sub_filter指令来实现。

受限确保nginx支持http_sub_module模块，如果不支持需要重新编译安装Nginx，自爱安装时候添加build参数—with-http_sub_module

然后在Nginx的http模块增加如下代码：

```
sub_filter '</head>' '<style type="text/css">html{ -webkit-filter: grayscale(100%);filter:progid:DXImageTransform.Microsoft.BasicImage(grayscale=1);}</style>';sub_filter_once on;
```

然后nginx -t测试配置正常无误

nginx -s reload 重启nginx即可
