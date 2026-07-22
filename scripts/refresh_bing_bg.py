#!/usr/bin/env python3
"""刷新 Hexo Butterfly 背景图为当日 Bing 官方原始图（直链 bing.com CDN）。

- 数据源：https://www.bing.com/HPImageArchive.aspx?format=js&idx={idx}&n=1&mkt=zh-CN （官方，无需鉴权）
- 取 images[0].url 拼接 https://www.bing.com 得到官方直链（1920x1080，非 UHD，加载更快）
- 更新 _config.butterfly.yml：
    index_img                 -> 官方直链
    cover.default_cover 中含 bing-imgapi.1314151.xyz 的项 -> 官方直链
    inject.head 中 preconnect / dns-prefetch 的 https://bing-imgapi.1314151.xyz -> https://www.bing.com
- 容错设计：
    1) API 调用带自动重试（默认 3 次，指数退避 2s / 4s / 8s）；
    2) 当日图(idx=0)不可用时，依次回退到昨天(idx=1)、前天(idx=2) 的近期官方图；
    3) 所有来源均失败（网络整体不可达）时，保留配置现状（即昨日已部署的图），输出
       FALLBACK 并以退出码 0 结束，避免每日自动化因背景刷新失败而中断文章生成。
- 仅当内容变化才写回，打印 CHANGED / UNCHANGED。
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "_config.butterfly.yml"
API_TMPL = "https://www.bing.com/HPImageArchive.aspx?format=js&idx={idx}&n=1&mkt=zh-CN"
OLD_PROXY = "https://bing-imgapi.1314151.xyz"
NEW_PRECONNECT = "https://www.bing.com"

MAX_RETRIES = 3       # 单次 API 调用的最大重试次数
RETRY_BACKOFF = 2     # 退避基数（秒），指数增长：2s / 4s / 8s
TIMEOUT = 15          # 单次 HTTP 请求超时（秒）
# 兜底候选顺序：今天(0) -> 昨天(1) -> 前天(2)
FALLBACK_IDX = (0, 1, 2)


def _http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_bing_url(api_url):
    """带重试地获取指定 API 的 Bing 官方直链；连续失败返回 None。"""
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            data = _http_get_json(api_url)
            raw = data["images"][0]["url"]
            return "https://www.bing.com" + raw
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF ** attempt)
    print(f"[WARN] 获取失败（重试 {MAX_RETRIES} 次）: {last_err}", file=sys.stderr)
    return None


def verify_reachable(url):
    """快速验证直链可访问（带重试），避免写入裂图。"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-0"},
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                if r.status in (200, 206):
                    return True
        except Exception:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF ** attempt)
    return False


def update_config(official_url):
    text = CONFIG.read_text(encoding="utf-8")
    new_text = text

    # 1) index_img（首页 banner）
    new_text = re.sub(
        r"(?m)^(index_img:\s*).*$",
        lambda m: f'{m.group(1)}"{official_url}"',
        new_text,
    )

    # 2) default_cover 列表中旧代理项 -> 官方直链
    new_text = re.sub(
        r"(?m)^\s*-\s*" + re.escape(OLD_PROXY) + r"[ \t]*$",
        f'     - "{official_url}"',
        new_text,
    )

    # 3) inject.head 中剩余的旧代理（preconnect / dns-prefetch）-> bing.com
    new_text = new_text.replace(OLD_PROXY, NEW_PRECONNECT)

    # 仅当文本真正变化才写回，避免同日重复运行产生无谓提交/部署
    if new_text != text:
        CONFIG.write_text(new_text, encoding="utf-8")
        print("CHANGED")
        return True
    print("UNCHANGED")
    return False


def main():
    official_url = None
    used_idx = None
    for idx in FALLBACK_IDX:
        api_url = API_TMPL.format(idx=idx)
        u = fetch_bing_url(api_url)
        if not u:
            continue
        if verify_reachable(u):
            official_url = u
            used_idx = idx
            break
        print(f"[WARN] idx={idx} 直链不可达，尝试下一张近期官方图", file=sys.stderr)

    if official_url is None:
        # 兜底：保留昨日图（配置现状），不改动，退出 0 以免阻断每日自动化
        print("[FALLBACK] 保留昨日图（Bing API 连续失败，未改动配置）")
        sys.exit(0)

    if used_idx and used_idx != 0:
        print(f"[INFO] 当日图不可用，已回退使用近期官方图 idx={used_idx}")

    print(f"[INFO] 采用 Bing 官方直链: {official_url}")
    update_config(official_url)


if __name__ == "__main__":
    main()
