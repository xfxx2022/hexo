#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
win_iso_build Releases -> Hexo 静态数据生成器

输出: source/js/win-iso-data.js  (设置 window.WIN_ISO_DATA)
- 抓取 xfxx2022/win_iso_build 全量 Releases（带重试，应对 api.github.com 间歇失败）
- 解析版本号 / 构建日期 / 分卷大小 / SHA256
- 将下载链接重写为国内可达镜像前缀（ghproxy 系列）
- 分类为 win11 / win10_2021 / win10_2019 / win10_2016

用法: python tools/gen_win_iso_data.py
"""
import json
import os
import re
import subprocess
import sys
import time

REPO = "xfxx2022/win_iso_build"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JS = os.path.join(ROOT, "source", "js", "win-iso-data.js")

# 国内可达的 GitHub Releases 下载镜像（按顺序：主用 -> 备用）
MIRRORS = [
    {"name": "ghproxy.net", "prefix": "https://ghproxy.net/"},
    {"name": "mirror.ghproxy.com", "prefix": "https://mirror.ghproxy.com/"},
    {"name": "gh.api.99988866.xyz", "prefix": "https://gh.api.99988866.xyz/"},
]

CATEGORY_MAP = [
    (r"^Windows_11_LTSC_2024", "win11", "Windows 11 LTSC 2024"),
    (r"^Windows_10_LTSC_2021", "win10_2021", "Windows 10 LTSC 2021"),
    (r"^Windows_10_LTSC_2019", "win10_2019", "Windows 10 LTSC 2019"),
    (r"^Windows_10_LTSB_2016", "win10_2016", "Windows 10 LTSB 2016"),
]
CATEGORY_ORDER = ["win11", "win10_2021", "win10_2019", "win10_2016"]
CATEGORY_LABEL = {
    "win11": "Windows 11 LTSC 2024",
    "win10_2021": "Windows 10 LTSC 2021",
    "win10_2019": "Windows 10 LTSC 2019",
    "win10_2016": "Windows 10 LTSB 2016",
}

# 页面分组：导航子标签 -> 该页聚合哪些详细分类
# Windows 10 页聚合 2021 / 2019 / 2016 三代表，子版本以 chip 形式筛选
PAGE_DEFS = [
    {"key": "win11", "label": "Windows 11", "tag": "Windows 11", "categories": ["win11"]},
    {"key": "win10", "label": "Windows 10", "tag": "Windows 10",
     "categories": ["win10_2021", "win10_2019", "win10_2016"]},
]

RETRY = 8
RETRY_WAIT = 3


def run_gh(args):
    for i in range(RETRY):
        try:
            out = subprocess.run(
                ["gh", "api"] + args, capture_output=True, text=True, timeout=90
            )
            if out.returncode == 0 and out.stdout.strip():
                return json.loads(out.stdout)
            sys.stderr.write(f"[retry {i+1}] exit={out.returncode} {out.stderr[:160]}\n")
        except Exception as e:  # noqa
            sys.stderr.write(f"[retry {i+1}] exc={e}\n")
        time.sleep(RETRY_WAIT)
    raise RuntimeError("gh api 多次重试失败: " + " ".join(args))


def classify(tag):
    for pat, cat, _title in CATEGORY_MAP:
        if re.match(pat, tag):
            return cat
    return "other"


def parse_build(tag):
    m = re.search(r"(\d{5}\.\d+)", tag)
    return m.group(1) if m else ""


def parse_date(tag, published):
    m = re.search(r"-(\d{8})-(\d{4})$", tag)
    if m:
        d = m.group(1)
        return f"{d[0:4]}-{d[4:6]}-{d[6:8]}"
    return (published or "")[:10]


def parse_sha(body):
    if not body:
        return ""
    m = re.search(r"ISO\s*SHA256[:\s]+([0-9a-fA-F]{64})", body)
    return m.group(1) if m else ""


def mirror_urls(official_url):
    return [{"name": m["name"], "url": m["prefix"] + official_url} for m in MIRRORS]


def main():
    os.makedirs(os.path.dirname(OUT_JS), exist_ok=True)
    print("拉取 Releases 列表 ...")
    releases = run_gh([f"repos/{REPO}/releases", "--paginate"])
    print(f"共 {len(releases)} 个 Releases")

    by_cat = {c: [] for c in CATEGORY_ORDER}
    for r in releases:
        tag = r.get("tag_name", "")
        cat = classify(tag)
        if cat not in by_cat:
            by_cat[cat] = []
        build = parse_build(tag)
        date = parse_date(tag, r.get("published_at", ""))
        sha = parse_sha(r.get("body", ""))
        assets = []
        total = 0
        for a in r.get("assets", []):
            size = a.get("size", 0)
            total += size
            official = a.get("browser_download_url", "")
            assets.append({
                "name": a.get("name", ""),
                "size": size,
                "official_url": official,
                "mirrors": mirror_urls(official),
            })
        assets.sort(key=lambda x: x["name"])
        by_cat[cat].append({
            "tag": tag,
            "title": CATEGORY_LABEL.get(cat, tag),
            "category": cat,
            "build": build,
            "date": date,
            "published_at": r.get("published_at", ""),
            "sha256": sha,
            "total_size": total,
            "parts": assets,
        })

    # 每个分类按构建日期倒序
    for c in by_cat:
        by_cat[c].sort(key=lambda x: x["date"], reverse=True)

    data = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "repo": REPO,
        "repo_url": f"https://github.com/{REPO}",
        "category_order": CATEGORY_ORDER,
        "category_label": CATEGORY_LABEL,
        "pages": PAGE_DEFS,
        "releases": by_cat,
    }

    js = "// 由 tools/gen_win_iso_data.py 自动生成，请勿手改\n"
    js += "window.WIN_ISO_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    with open(OUT_JS, "w", encoding="utf-8") as f:
        f.write(js)

    counts = {c: len(v) for c, v in by_cat.items()}
    print("生成完成:", OUT_JS)
    print("各分类数量:", counts)
    total_releases = sum(counts.values())
    print("Releases 总数:", total_releases)


if __name__ == "__main__":
    main()
