---
abbrlink: ''
categories: []
date: '2024-01-30T18:15:18.733398+08:00'
tags: []
title: Serv00搭建各种服务
updated: '2024-01-31T11:12:08.305+08:00'
---
# [Serv00](https://www.serv00.com/)白嫖记录

这个平台是个Virtual Host，没有Root，还是FreeBSD的系统，不是Linux，不太好用。但是优点是隔离性差，Memory和vCPU能短时间内超过100%进行调用。

已经玩了不少时间了，起初看到Github上有使用Serv00搭建Vless节点的[仓库](https://github.com/qwer-search/serv00-vless)，就上手玩了一下，后来发现极其不稳，screen运行的进程总是过一段时间就掉了，又得ssh上去启动，相当不友好，且后来又发现了Hax这样的玩具，就对Serv00视如敝履了。

但是这两天有[群友](https://jq.qq.com/?_wv=1027&k=qssjFvAs)突然提醒我才想起，我在Hax上用的很舒服的pm2也可以在Serv00上使用，这个十年有效期的玩具突然显得有用了起来。

经过我的尝试，成功在Serv00上部署了一些服务，接下来进行记录：

## pm2

这个是重中之重，如果不是成功安装了pm2，我甚至不会尝试探索Serv00这个玩具有什么用，所以pm2的安装方法记录在开头。

首先，在Panel中的Additional services选项卡中找到Run your own applications项目，将其设置为Enabled。

在SSH连接serv00之后，直接使用一键脚本安装pm2：

**SHELL**

|

```
1
```

|

```
bash <(curl -s https://raw.githubusercontent.com/k0baya/alist_repl/main/serv00/install-pm2.sh)
```


|  |  |
| - | - |

想要使用 `pm2`，请直接用路径调用：`~/.npm-global/bin/pm2`。

## Vless

这个肯定是第一时间部署的，每次遇到这样的平台，第一时间总是想着能不能搭建节点。

创建并进入vless工作路径，并克隆源仓库：

**SHELL**

|

```
1
```

|

```
cd ~/domains && git clone https://github.com/qwer-search/serv00-vless && mv -f serv00-vless vless && cd vless && rm -f README.md
```


|  |  |
| - | - |

在Panel中Port Reservation选项卡中放行一个TCP端口，随机即可，记住端口号。

使用vim编辑或者直接去Panel中的File Manager选项卡在线编辑app.js文件，修改端口为刚刚放行的端口。

安装依赖：

**SHELL**

|

```
1
```

|

```
npm install
```


|  |  |
| - | - |

安装完毕后，使用pm2启动并守护vless进程：

**SHELL**

|

```
1
```

|

```
~/.npm-global/bin/pm2 start app.js --name vless
```


|  |  |
| - | - |

接着去你的代理客户端软件中手动添加vless配置即可：


| 地址                                         | 端口         | 用户id                               | 传输协议 | 伪装域名 | ws path |
| -------------------------------------------- | ------------ | ------------------------------------ | -------- | -------- | ------- |
| Panel中WWW Websites选项卡里的你的Domain name | 你放行的端口 | 37a0bd7c-8b9f-4693-8916-bd1e2da0a817 | ws       | 同地址   | /       |

上表没有给出的可以不填。

## WordPress

实际上在部署完Vless节点后我去查看了serv00的[文档](https://docs.serv00.com/)，其中有搭建网站的示例，没错，示例用的是WordPress，实际上WordPress确实可以搭建，十分简单好用。这里不做过多介绍，按照文档一步步操作即可。

除了WordPress外，文档中还详细介绍了Redis、Memcached、Imapsync、WP-CLI、Tomcat等服务的搭建方法，有需求的都可以照着抄。

## Alist

Alist官方仓库没有构筑FreeBSD系统下能够运行的Alist可执行文件，但是我在Github上发现了一个使用Github Workflow自动构筑FreeBSD适用的Alist的[仓库](https://github.com/uubulb/alist-freebsd)，使用这个仓库就可以很便利的在Serv00上部署Alist。

新建并进入Alist的工作目录：

**SHELL**

|

```
1
```

|

```
mkdir -p ~/domains/alist && cd ~/domains/alist
```


|  |  |
| - | - |

接着使用一键命令安装Alist：

**SHELL**

|

```
1
```

|

```
wget -O alist-freebsd.sh https://raw.githubusercontent.com/k0baya/alist_repl/main/serv00/alist-freebsd.sh && sh alist-freebsd.sh
```


|  |  |
| - | - |

接着在Panel中Port Reservation选项卡中放行一个TCP端口，随机即可，再找到MySQL选项卡，使用Add database功能新建一个数据库。

> 密码要求含有大写字母、小写字母和数字三种字符，且长度必须超过6个字符。

接下来进入File manager选项卡，进入 `~/domains/alist/data`路径，可以看到一个名为 `config.json`的文件，右键点击，选择View/Edit > Source Editor，进行编辑：

我主要修改了CDN、database、scheme三个部分，其中CDN可以在[Alist的官方文档](https://link.zhihu.com/?target=https://alist.nn.ci/zh/config/configuration.html%23cdn)找到，请选择你本地网络连接速度最快的一个。

scheme部分，我选择修改adress为 `127.0.0.1`本地回环，是为了避免被他人使用 `http://ip:port<span> </span>`的方式进行访问。至于自己怎么访问，我在本文后面的部分会进行介绍。port要改成自己前面放行的端口。

database部分，type需要改成\`mysql\`，host填写你在注册邮件中看到的mysql的地址，port是默认的3306，用户名、密码、数据库名则按照你创建的情况进行填写。

改完之后，点击save保存，接着回到SSH窗口中进行操作：

测试启动Alist：

**SHELL**

|

```
1
```

|

```
./alist server
```


|  |  |
| - | - |

> 确定运行没有问题后，按 `Ctrl+c`即可停止运行。

使用pm2启动并管理alist：

**SHELL**

|

```
1
```

|

```
~/.npm-global/bin/pm2 start ./alist -- server
```


|  |  |
| - | - |

到这里你还无法访问Alist，在下一个部分中我将介绍如何使用自己的域名访问Alist。

## Cloudflared

和Alist一样，Cloudflared官方仓库并没有构筑FreeBSD系统上能够使用的二进制文件，但是同样的，我找到了[第三方的构筑](https://cloudflared.bowring.uk/)。使用第三方构筑的二进制文件，就能愉快的使用隧道了。

关于Cloudflared是什么，有什么用，ARGO\_TOKEN如何获取等部分，这里不再赘述，详细可以查看我的关于CodeSandbox和Hax的文章。

创建并进入Cloudflared的工作目录：

**SHELL**

|

```
1
```

|

```
mkdir -p ~/domains/cloudflared && cd ~/domains/cloudflared
```


|  |  |
| - | - |

下载Cloudflared：

**SHELL**

|

```
1
```

|

```
wget https://cloudflared.bowring.uk/binaries/cloudflared-freebsd-2023.10.0.7z && 7z x cloudflared-freebsd-2023.10.0.7z && rm cloudflared-freebsd-2023.10.0.7z && mv -f ./temp/cloudflared-freebsd-2023.10.0 ./cloudflared && rm -rf temp
```


|  |  |
| - | - |

测试运行：

**SHELL**

|

```
1
```

|

```
./cloudflared tunnel --edge-ip-version auto --protocol http2 --heartbeat-interval 10s run --token ARGO_TOKEN
```


|  |  |
| - | - |

> 其中ARGO\_TOKEN要替换成自己的。确定运行没有问题后，按 `Ctrl+c`即可停止运行。

使用pm2启动Cloudflared：

**SHELL**

|

```
1
```

|

```
~/.npm-global/bin/pm2 start ./cloudflared -- tunnel --edge-ip-version auto --protocol http2 --heartbeat-interval 10s run --token ARGO_TOKEN
```


|  |  |
| - | - |

> 其中ARGO\_TOKEN要替换成自己的。

接着去CLoudflare的面板中设置域名对应端口，即可使用域名访问自己搭建的服务了。

## KodBox

其实Serv00虽然能够部署KodBox，但是实在是不太好用。最直观的感受就是卡，因为KodBox运行期间需要调用多个PHP组件，而Serv00限制同时处理三个PHP进程，所以显得特别慢。其次，Serv00没有Root权限，部分PHP插件没有安装，也无法安装，导致有一些KodBox的插件无法正常运行。

当然如果只是图新奇搭一个玩玩，也是可以的。下面是步骤：

进入PHP网站路径：

**SHELL**

|

```
1
```

|

```
cd ~/domains/用户名.serv00.net/public_html/
```


|  |  |
| - | - |

安装KodBox：

**SHELL**

|

```
1
```

|

```
bash <(curl -s https://pan.rappit.site/d/shell/kodbox1.49/serv00-kodbox-install.sh)
```


|  |  |
| - | - |

然后去Panel中的MySQL选项卡，新建数据库和用户，用以接入KodBox。接着打开 `https://用户名.serv00.net/`进行KodBox的安装，数据库填写你刚刚新建的数据库即可。初次启动需要较长的时间，请耐心等待。

## Uptime-Kuma

受限于FreeBSD的平台限制，1.23版本内置了PlayWright，无法运行，所以只能安装1.22版本。切记先去Panel中放行TCP端口。

下载1.22.1版本源代码并进入工作路径：

**SHELL**

|

```
1
```

|

```
cd ~/domains && wget https://github.com/louislam/uptime-kuma/archive/refs/tags/1.22.1.zip && unzip 1.22.1.zip && mv -f uptime-kuma-1.22.1 kuma && rm -f 1.22.1.zip && cd kuma
```


|  |  |
| - | - |

设置生产模式：

**SHELL**

|

```
1
```

|

```
npm ci --production
```


|  |  |
| - | - |

下载dist文件：

**SHELL**

|

```
1
```

|

```
wget https://github.com/louislam/uptime-kuma/releases/download/1.22.1/dist.tar.gz && tar -xzvf dist.tar.gz && rm dist.tar.gz
```


|  |  |
| - | - |

安装补充依赖：

**SHELL**

|

```
1
```

|

```
npm install
```


|  |  |
| - | - |

安装过程中多少会有报错，无视就好，实际上最后可以正常运行。内置的Cloudflared反向代理在FreeBSD平台上无法使用，但是可以使用上述的外置的Cloudflared进行反代，使用自己的域名。

测试运行：

**SHELL**

|

```
1
```

|

```
node server/server.js --port=PORT
```


|  |  |
| - | - |

> 记得把PORT替换成你放行的端口。确定运行没有问题后，按 `Ctrl+c`即可停止运行。

使用pm2管理后台运行：

**SHELL**

|

```
1
```

|

```
~/.npm-global/bin/pm2 start server/server.js --name uptime-kuma -- --port=PORT
```


|  |  |
| - | - |

> 记得把PORT替换成你放行的端口。

> 如果你不希望自己的Uptime-Kuma被人使用 `http://IP:PORT`的方式访问，你可以在最后的执行命令添加 `--host=127.0.0.1`的尾缀，这样就只能通过反向代理的域名进行访问了:
>
> **SHELL**
>
> |
>
> ```
> 1
> ```
>
> |
>
> ```
> ~/.npm-global/bin/pm2 start server/server.js --name uptime-kuma -- --port=PORT --host=127.0.0.1
> ```
>
>
> |  |  |
> | - | - |

## 自动续期

我在Panel中看到的有效期是10年，但是网上有些消息说3个月不登录面板或SSH的话就会删号。可以用青龙面板的自动任务定期登录SSH解决。

在青龙面板中添加Linux依赖 `sshpass`，然后添加定时任务：名称随意，命令/脚本 `sshpass -p '密码' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -tt 用户名@地址 "exit"`，定时规则 `1 1 1 * *`。这样就会每个月自动ssh连接一次，实现续期。

> 你还可以使用自身SSH自身的方式进行自动续期，操作如下：
>
> 在Panel中找到File manager选项卡，进入一个自己喜欢的路径，然后找到上方Send按钮左边的+，选择New empty file，文件名命名为 `auto-renew.sh`， 右键点击 `auto-renew.sh`，选择View/Edit > Source Editor，进行编辑，把下面的代码块的内容都复制进去：
>
> **SHELL**
>
> |
>
> ```
> 1
> 2
> 3
> 4
> 5
> 6
> ```
>
> |
>
> ```
> #!/bin/bash
>
> while true; do
>   sshpass -p '密码' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -tt 用户名@s1(s0).serv00.com "exit"
>   sleep 259200  #30天为259200秒
> done
> ```
>
>
> |  |  |
> | - | - |
>
> 记得把其中的密码、用户名、ssh的地址修改为你自己的。
>
> 保存后回到SSH中，进入 `auto-renew.sh` 所在的路径：
>
> **SHELL**
>
> |
>
> ```
> 1
> ```
>
> |
>
> ```
> cd xxx    #其中xxx为你的auto-renew.sh文件的存放路径
> ```
>
>
> |  |  |
> | - | - |
>
> 给 `auto-renew.sh`添加可执行权限：
>
> **SHELL**
>
> |
>
> ```
> 1
> ```
>
> |
>
> ```
> chmod +x auto-renew.sh
> ```
>
>
> |  |  |
> | - | - |
>
> 使用pm2启动：
>
> **SHELL**
>
> |
>
> ```
> 1
> ```
>
> |
>
> ```
> ~/.npm-global/bin/pm2 start ./auto-renew.sh
> ```
>
>
> |  |  |
> | - | - |
>
> 这样就会每隔一个月自动执行一次SSH连接，自己SSH自己进行续期。

## 自动启动

听说Serv00的主机会不定时重启，所以需要添加自启任务。

在Panel中找到Cron jobs选项卡，使用Add cron job功能添加任务，Specify time选择After reboot，即为重启后运行。Form type选择Advanced，Command写：

**SHELL**

|

```
1
```

|

```
/home/你的用户名/.npm-global/bin/pm2 resurrect
```


|  |  |
| - | - |

> 记得把你的用户名改为你的用户名

添加完之后，在SSH窗口保存pm2的当前任务列表快照：

**SHELL**

|

```
1
```

|

```
~/.npm-global/bin/pm2 save
```


|  |  |
| - | - |

这样每次serv00不定时重启任务时，都能自动调用pm2读取保存的任务列表快照，恢复任务列表。
