---
title: Windows 11 构建下载
date: 2026-07-23 15:00:00
aside: false
comments: false
toc: false
description: 番茄酱自动构建的 Windows 11 LTSC 2024 简体中文 X64 ISO 镜像下载，含版本号、构建日期、文件大小、SHA256 校验与国内镜像加速下载。
keywords:
  - Windows 11
  - LTSC 2024
  - ISO 下载
  - 镜像加速
  - GitHub Releases
---

<link rel="stylesheet" href="/css/win-iso.css">

<div class="win-iso win11" id="winIsoRoot" data-page="win11">
  <div class="wi-hero">
    <div class="wi-hero-text">
      <div class="wi-hero-badge"><i class="fas fa-windows"></i> 自动构建 · GitHub Actions</div>
      <h1>Windows 11 构建下载</h1>
      <p id="wiSub">正在加载构建数据…</p>
      <div class="wi-stats" id="wiStats"></div>
    </div>
    <div class="wi-hero-art" aria-hidden="true">
      <div class="wi-hero-icon win11-icon"><i class="fab fa-windows"></i></div>
    </div>
  </div>

  <div class="wi-notice">
    <i class="fas fa-info-circle"></i>
    <span>GitHub Releases 直链在国内访问受限，下方「加速下载」已默认走
    <b>ghproxy.net</b> 等镜像；若某镜像缓慢或失败，请点开「其他镜像」切换备用节点或官方直链。</span>
  </div>

  <div class="wi-subfilter" id="wiSubfilter"></div>

  <div class="wi-toolbar">
    <div class="wi-search">
      <i class="fas fa-search"></i>
      <input id="wiSearch" type="text" placeholder="搜索版本号或构建日期，如 26200 或 2026-07" />
    </div>
    <select id="wiSort" aria-label="排序方式">
      <option value="date-desc">构建日期（新→旧）</option>
      <option value="date-asc">构建日期（旧→新）</option>
      <option value="size-desc">体积（大→小）</option>
      <option value="build-desc">版本号（高→低）</option>
    </select>
  </div>

  <div class="wi-list" id="wiList"></div>
  <div class="wi-pager" id="wiPager"></div>

  <div class="wi-note">
    <h3><i class="fas fa-puzzle-piece"></i> 分卷合并与校验说明</h3>
    <p>每个构建由 <code>.iso.zip.001</code> / <code>.002</code> / <code>.003</code> 三个分卷组成，需<strong>全部下载到同一文件夹</strong>后合并：</p>
    <pre><code>rem Windows（CMD）
copy /b *.001 + *.002 + *.003 iso.zip

# macOS / Linux
cat *.001 *.002 *.003 &gt; iso.zip</code></pre>
    <p>合并后解压 <code>iso.zip</code> 得到 <code>.iso</code>，并用下方「复制 SHA256」校验完整性：</p>
    <pre><code>certutil -hashfile iso.iso SHA256        # Windows
shasum -a 256 iso.iso                     # macOS / Linux</code></pre>
  </div>
</div>

<script src="/js/win-iso-data.js"></script>
<script src="/js/win-iso-page.js"></script>
