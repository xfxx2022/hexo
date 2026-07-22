---
abbrlink: 42f8de21
categories:
  - - 教程
cover: 'https://blog.1314151.xyz/img/2023/12/22/cloudflare workers.webp'
date: '2023-12-22T15:16:34.423669+08:00'
tags:
  - 教程
title: cloudflare workers反向代理可以+ip加端口
updated: '2023-12-22T15:31:37.233+08:00'
---
代码如下：

```
addEventListener('fetch', event => {
    const request = event.request;
    const url = new URL(request.url);
    const response = fetch('http://173.82.110.36:5230' + url.pathname + url.search, {
        method: request.method,
        headers: request.headers,
        body: request.body,
    });
    event.respondWith(response);
});
```
