#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""刷新 Hexo Butterfly 背景图/默认封面为当日 Bing 官方图（下载到本地，避免外链大图）。

数据源：https://www.bing.com/HPImageArchive.aspx?format=js&idx={idx}&n=1&mkt=zh-CN （官方，无需鉴权）
流程：取 images[0].url -> 拼接 https://www.bing.com 得到官方直链 -> 下载并压为 source/img/bing-daily.webp
      -> 更新 _config.butterfly.yml 的 index_img 与 default_cover 为 /img/bing-daily.webp
容错：API/下载连续失败时使用昨日已落盘的本地图（不回退外链），退出 0 不阻断每日自动化。
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "_config.butterfly.yml"
IMG_DIR = ROOT / "source" / "img"
LOCAL_IMG = "bing-daily.webp"
LOCAL_PATH = IMG_DIR / LOCAL_IMG
LOCAL_REF = "/img/" + LOCAL_IMG

API_TMPL = "https://www.bing.com/HPImageArchive.aspx?format=js&idx={idx}&n=1&mkt=zh-CN"
MAX_RETRIES = 3
RETRY_BACKOFF = 2
TIMEOUT = 15
FALLBACK_IDX = (0, 1, 2)


def _http_get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read() if binary else json.loads(r.read().decode("utf-8"))


def fetch_bing_url(api_url):
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            data = _http_get(api_url)
            return "https://www.bing.com" + data["images"][0]["url"]
        except Exception as e:
            last_err = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF ** attempt)
    print("[WARN] 获取失败（重试 %d 次）: %s" % (MAX_RETRIES, last_err), file=sys.stderr)
    return None


def download_and_save(remote_url):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            raw = _http_get(remote_url, binary=True)
            IMG_DIR.mkdir(parents=True, exist_ok=True)
            try:
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(raw)).convert("RGB")
                buf = io.BytesIO()
                img.save(buf, "WEBP", quality=82, method=4)
                LOCAL_PATH.write_bytes(buf.getvalue())
            except Exception:
                LOCAL_PATH.write_bytes(raw)
            print("[OK] 已保存本地封面: %s" % LOCAL_PATH)
            return True
        except Exception as e:
            last_err = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF ** attempt)
    print("[WARN] 下载失败: %s" % last_err, file=sys.stderr)
    return False


def update_config():
    text = CONFIG.read_text(encoding="utf-8")
    new_text = re.sub(r"(?m)^(index_img:\s*).*$", lambda m: '%s"%s"' % (m.group(1), LOCAL_REF), text)
    new_text = re.sub(r"(?m)^\s*-\s*\S+bing\S*1920x1080\S*\s*$", '     - "%s"' % LOCAL_REF, new_text)
    if new_text != text:
        CONFIG.write_text(new_text, encoding="utf-8")
        return True
    return False


def main():
    official_url = None
    for idx in FALLBACK_IDX:
        u = fetch_bing_url(API_TMPL.format(idx=idx))
        if u and download_and_save(u):
            official_url = u
            break
    if official_url is None:
        if LOCAL_PATH.exists():
            print("[FALLBACK] Bing 获取/下载失败，保留昨日本地封面，未改动配置")
            sys.exit(0)
        print("[ERROR] 无本地封面且下载失败", file=sys.stderr)
        sys.exit(1)
    print("CHANGED" if update_config() else "UNCHANGED")


if __name__ == "__main__":
    main()
