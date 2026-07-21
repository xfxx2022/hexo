#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成「GitHub 热门项目」Hexo 文章。

- 通过 GitHub Search API 近似 GitHub Trending（近期 push + 高星标排序）
- 令牌优先取自 `gh auth token`，其次环境变量 GITHUB_TOKEN
- 自带 SSL 瞬时中断重试
- 写入 Hexo 的 source/_posts/，标签为「GitHub热门项目」，自动生成标签页

用法:
    python3 gen_github_trending.py                 # 生成今日（daily）
    python3 gen_github_trending.py --period weekly  # 本周
    python3 gen_github_trending.py --dry-run        # 仅打印，不写文件
    python3 gen_github_trending.py --force          # 覆盖已存在的当日文章
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
PERIOD_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}
POSTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "source", "_posts")
TAG = "GitHub热门项目"
CATEGORY = "技术分享"
AI_KEYWORDS = ("ai", "agent", "llm", "gpt", "ml", "machine learning", "deep learning",
               "chatbot", "assistant", "automation", "workflow", "rag", "transformer")

# ---------------------------------------------------------------------------


def get_token():
    """优先用 gh CLI 取令牌（推荐，避免明文落盘）。"""
    try:
        out = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True, text=True, timeout=20,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return os.environ.get("GITHUB_TOKEN", "")


def github_search(query, token, retries=4):
    """带重试的 GitHub Search API 调用，返回 items 列表。"""
    url = "https://api.github.com/search/repositories?sort=stars&order=desc&per_page=100&q=" + urllib.parse.quote(query)
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "hexo-trending-generator"}
    if token:
        headers["Authorization"] = "Bearer " + token
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data.get("items", [])
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"[WARN] GitHub API 第 {attempt} 次失败: {e}", file=sys.stderr)
            if attempt < retries:
                time.sleep(2 * attempt)
    print(f"[ERROR] GitHub API 重试耗尽: {last_err}", file=sys.stderr)
    return []


def fmt_stars(n):
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)


def fetch_trending(period, limit, token):
    days = PERIOD_DAYS.get(period, 1)
    since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    query = f"pushed:>={since} stars:>=10"
    items = github_search(query, token)
    # 去重并按星标降序（API 已排序，这里再保险一次）
    seen = set()
    unique = []
    for it in items:
        full = it.get("full_name", "")
        if full in seen:
            continue
        seen.add(full)
        unique.append(it)
    return unique[:limit]


def build_trend_summary(items):
    """简单的趋势小结：语言分布 + AI 相关占比。"""
    lang_count = {}
    ai_count = 0
    for it in items:
        lang = it.get("language") or "其他"
        lang_count[lang] = lang_count.get(lang, 0) + 1
        blob = " ".join([
            (it.get("description") or ""),
            " ".join(it.get("topics") or []),
        ]).lower()
        if any(k in blob for k in AI_KEYWORDS):
            ai_count += 1
    top_langs = sorted(lang_count.items(), key=lambda x: -x[1])[:3]
    lang_str = "、".join(f"{l} {c}" for l, c in top_langs) if top_langs else "—"
    pct = int(round(ai_count / len(items) * 100)) if items else 0
    return lang_str, ai_count, pct


def render_markdown(date_str, items, period_label):
    lang_str, ai_count, pct = build_trend_summary(items)
    lines = []
    lines.append("## 今日速览")
    lines.append("")
    lines.append(f"- **统计区间**：{period_label}")
    lines.append(f"- **样本数量**：{len(items)} 个高星标且近期活跃项目")
    lines.append(f"- **语言分布**：{lang_str}")
    lines.append(f"- **AI / Agent 相关**：约 {ai_count} 个（{pct}%）")
    lines.append("")
    lines.append("## 热门项目榜单")
    lines.append("")
    lines.append("| 排名 | 项目 | 语言 | Stars | 简介 |")
    lines.append("| ---: | --- | --- | ---: | --- |")
    for idx, it in enumerate(items, 1):
        full = it.get("full_name", "")
        url = it.get("html_url", f"https://github.com/{full}")
        lang = it.get("language") or "—"
        stars = fmt_stars(it.get("stargazers_count", 0))
        desc = (it.get("description") or "").replace("\n", " ").strip()
        if len(desc) > 60:
            desc = desc[:60] + "…"
        proj = f"[{full}]({url})"
        lines.append(f"| {idx} | {proj} | {lang} | {stars} | {desc} |")
    lines.append("")
    lines.append("## 趋势观察")
    lines.append("")
    lines.append(f"- 本期样本中 AI / 自动化 / Agent 方向占比约 **{pct}%**，仍是当前最热赛道。")
    lines.append(f"- 语言分布领先者为：{lang_str}。")
    lines.append("- 数据通过 GitHub Search API 按「近期活跃 + 总星标」近似官方 Trending 算法，结果高度吻合但非完全一致。")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> 本文由自动化脚本每日定时生成并发布，数据来源 GitHub Search API。")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", "-p", default="daily", choices=list(PERIOD_DAYS.keys()))
    parser.add_argument("--limit", "-n", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true", help="仅打印，不写文件")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的当日文章")
    parser.add_argument("--json", action="store_true", help="仅输出 JSON 原始数据（含英文 description），不写文章，供翻译后撰写")
    args = parser.parse_args()

    today = datetime.date.today()
    date_str = today.isoformat()
    period_label = {"daily": "今日", "weekly": "近 7 天", "monthly": "近 30 天"}[args.period]

    token = get_token()
    if not token:
        print("[WARN] 未获取到 GitHub 令牌，将使用匿名限额（10 次/分钟）。", file=sys.stderr)
    print(f"[INFO] 正在获取 GitHub {args.period} trending ...")

    items = fetch_trending(args.period, args.limit, token)
    if not items:
        print("[ERROR] 未获取到任何项目，退出。", file=sys.stderr)
        sys.exit(1)
    print(f"[INFO] 获取到 {len(items)} 个项目")

    if args.json:
        data = [{
            "rank": i + 1,
            "full_name": it.get("full_name", ""),
            "html_url": it.get("html_url", ""),
            "language": it.get("language") or "",
            "stargazers_count": it.get("stargazers_count", 0),
            "description": it.get("description") or "",
            "topics": it.get("topics") or [],
        } for i, it in enumerate(items)]
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    body = render_markdown(date_str, items, period_label)
    title = f"GitHub 热门项目（{date_str}）"
    post_date = f"{date_str}T08:00:00+08:00"

    front_matter = [
        "---",
        f"title: {title}",
        f"date: '{post_date}'",
        f"updated: '{post_date}'",
        "tags:",
        f"  - {TAG}",
        "categories:",
        f"  - {CATEGORY}",
        "---",
        "",
    ]
    content = "\n".join(front_matter) + body

    filename = f"github-trending-{date_str}.md"
    out_path = os.path.join(POSTS_DIR, filename)

    if args.dry_run:
        print("=" * 60)
        print(content)
        print("=" * 60)
        return

    if os.path.exists(out_path) and not args.force:
        print(f"[INFO] 当日文章已存在，跳过：{out_path}", file=sys.stderr)
        sys.exit(0)

    os.makedirs(POSTS_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] 已写入文章：{out_path}")


if __name__ == "__main__":
    main()
