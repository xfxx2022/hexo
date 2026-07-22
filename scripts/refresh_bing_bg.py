#!/usr/bin/env python3
"""刷新 Hexo Butterfly 背景图为当日 Bing 官方原始图（直链 bing.com CDN）。

- 数据源：https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN （官方，无需鉴权）
- 取 images[0].url 拼接 https://www.bing.com 得到官方直链（1920x1080，非 UHD，加载更快）
- 更新 _config.butterfly.yml：
    index_img                 -> 官方直链
    cover.default_cover 中含 bing-imgapi.1314151.xyz 的项 -> 官方直链
    inject.head 中 preconnect / dns-prefetch 的 https://bing-imgapi.1314151.xyz -> https://www.bing.com
- 仅当内容变化才写回，并打印 CHANGED / UNCHANGED；抓取失败退出码 1。
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "_config.butterfly.yml"
API = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN"
OLD_PROXY = "https://bing-imgapi.1314151.xyz"
NEW_PRECONNECT = "https://www.bing.com"


def fetch_bing_url():
    req = urllib.request.Request(API, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode("utf-8"))
    url = data["images"][0]["url"]
    return "https://www.bing.com" + url


def update_config(official_url):
    text = CONFIG.read_text(encoding="utf-8")
    new_text = text
    changed = False

    # 1) index_img（首页 banner）
    new_text, n = re.subn(
        r"(?m)^(index_img:\s*).*$",
        lambda m: f'{m.group(1)}"{official_url}"',
        new_text,
    )
    if n:
        changed = True

    # 2) default_cover 列表中旧代理项 -> 官方直链
    new_text, n2 = re.subn(
        r"(?m)^\s*-\s*" + re.escape(OLD_PROXY) + r"[ \t]*$",
        f'     - "{official_url}"',
        new_text,
    )
    if n2:
        changed = True

    # 3) inject.head 中剩余的旧代理（preconnect / dns-prefetch）-> bing.com
    new_text, n3 = re.subn(re.escape(OLD_PROXY), NEW_PRECONNECT, new_text)
    if n3:
        changed = True

    if changed:
        CONFIG.write_text(new_text, encoding="utf-8")
        print("CHANGED")
    else:
        print("UNCHANGED")
    return changed


def main():
    try:
        official_url = fetch_bing_url()
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] 获取 Bing 官方图失败: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"[INFO] 当日 Bing 官方直链: {official_url}")
    update_config(official_url)


if __name__ == "__main__":
    main()
