---
title: Sublime Text_v4.0_Build_4134_Dev
date: 2022-06-12 22:30:00
tags: 办公学习
categories: 办公学习
cover: https://vkceyugu.cdn.bspapp.com/VKCEYUGU-6f00c918-7a62-47b5-8e8a-9578acfb171c/b70bc4b7-eaf3-4a03-a1c1-dc951d49b187.png
---

# 软件介绍

Sublime Text - 性感的代码编辑器、程序员之必备神器！Sublime Text 是个功能强大的代码编辑器，也是HTML和散文先进的文本编辑器。其主要功能包括：Python的插件，完整的Python API ， Goto功能，代码段，代码缩略图，拼写检查，书签，即时项目切换，多选择，多窗口，自定义键绑定，主题方案等。

Sublime Text支持C, C++, C#, CSS, D, Erlang, HTML, Groovy, Haskell, HTML, Java, JavaScript, LaTeX, Lisp, Lua, Markdown, Matlab, OCaml, Perl, PHP, Python, R, Ruby, SQL, TCL, Textile, XML等语法文件。

# 软件截图

![Sublime Text](https://vkceyugu.cdn.bspapp.com/VKCEYUGU-6f00c918-7a62-47b5-8e8a-9578acfb171c/b5f11fd6-85ac-4b62-a1d4-91fee9094ebb.png)

# 新版变化

Sublime Text 4 - News - Sublime HQ
[https://www.sublimetext.com/blog/articles/sublime-text-4](https://www.sublimetext.com/blog/articles/sublime-text-4)

# 特点描述

1.暴力破解无需许可证，禁止联网检查授权、禁止检查更新!
2.集成多语言插件包（LocalizedMenu）已预设默认为中文
3.集成增强侧边栏操作插件中文版（SideBarEnhancements）
4.集成编码插件（ConvertToUTF8）解决原版不支持的编码文件
5.集成插件控制器（PackageControl）解决原版装插件报错问题
6.原生绿色便携式，并提供了批处理快速「添加/删除右键菜单项」

**如何安装插件？**
按快捷键Ctrl+Shift+P，输入 install 回车，选择相应插件安装即可
或者依次点击"首选项 – 插件控制 – Install Package"进行安装插件

```
<!--暴力破解，无需依赖许可证密钥-->

使用反汇编神器x64dbg附加载入主程序SublimeText.exe搜索关键词：update_check（第一处)
49:8B?? ?? ?? 0000   mov rax,qword ptr ds:[r14+2B8]   | r14+2B8:"ted in DLL at base 0x%p.\n"
8078 ?? 00           cmp byte ptr ds:[rax+5],0        | 这里改为mov byte ptr ds:[rax+0x5], 0x1
74 ??                je sublime_text.7FF76A8B7FE2     |
49:???? ????0000     mov rcx,qword ptr ds:[r14+128]   | r14+128:"previously, ModuleState: %d\n"
48:8D?? ??????00     lea rax,qword ptr ds:[xxxxxxxxxx]| xxxxxx:"update_check"

<!--禁止联网检查授权状态以及升级-->

字符串：license.sublimehq.com 改为NOP（90填充）
/updates/4/dev_update_check  改为NOP（90填充）
然后点菜单设置->无干扰设置->打开在底部添加2行参数
{
"enable_telemetry": false,
"update_check": false,
}
```

Sublime Text 第三方本地化菜单多语言化插件包
[https://github.com/zam1024t/LocalizedMenu](https://github.com/zam1024t/LocalizedMenu)

Sublime Text 第三方侧边栏右键增强插件中文版
[https://github.com/52fisher/SideBarEnhancements](https://github.com/52fisher/SideBarEnhancements)

PackageControl: 插件安装控制管理器（必装的）
[https://packagecontrol.io/installation](https://packagecontrol.io/installation)
[https://github.com/wbond/package_control/releases](https://github.com/wbond/package_control/releases)

# 下载地址

Sublime Text 4.0 Build 4134 Dev + Portable (2022/05/27)
[https://download.sublimetext.com/sublime_text_build_4134.zip](https://download.sublimetext.com/sublime_text_build_4134.zip)
[https://download.sublimetext.com/sublime_text_build_4134_x64.zip](https://download.sublimetext.com/sublime_text_build_4134_x64.zip)
[https://download.sublimetext.com/sublime_text_build_4134_x32_setup.exe](https://download.sublimetext.com/sublime_text_build_4134_x32_setup.exe)
[https://download.sublimetext.com/sublime_text_build_4134_x64_setup.exe](https://download.sublimetext.com/sublime_text_build_4134_x64_setup.exe)
[123盘](https://www.123pan.com/s/CDiA-pDNF3)
提取码

```
wwmw
```

[蓝奏网盘](https://wwu.lanzoub.com/b0374dxxe)
提取码

```
gr3f
```



