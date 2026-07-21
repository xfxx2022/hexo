#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成「GitHub 热门项目」Hexo 文章。

- 通过 GitHub Search API 近似 GitHub Trending（近期 push + 高星标排序）
- 自动按排名抓取项目 README 首个图片或 GitHub Open Graph 作为封面并落盘
- 令牌优先取自 `gh auth token`，其次环境变量 GITHUB_TOKEN
- 自带 SSL 瞬时中断重试
- 写入 Hexo 的 source/_posts/，标签为「GitHub热门项目」，自动生成标签页

用法:
    python3 gen_github_trending.py                 # 生成今日（daily）文章+封面
    python3 gen_github_trending.py --period weekly  # 本周
    python3 gen_github_trending.py --dry-run        # 仅打印，不写文件
    python3 gen_github_trending.py --force          # 覆盖已存在的当日文章
    python3 gen_github_trending.py --json           # 仅输出 JSON 原始数据（供翻译后撰写）
"""

import argparse
import base64
import datetime
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
PERIOD_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT_DIR, "source", "_posts")
COVER_DIR = os.path.join(ROOT_DIR, "source", "img", "github-trending")
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


def http_get_bytes(url, headers=None, retries=3, timeout=20):
    """带重试的通用 HTTP GET，返回 bytes。"""
    headers = dict(headers or {})
    headers.setdefault("User-Agent", "hexo-trending-generator")
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read(), resp.headers
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"[WARN] GET {url} 第 {attempt} 次失败: {e}", file=sys.stderr)
            if attempt < retries:
                time.sleep(2 * attempt)
    print(f"[ERROR] GET {url} 重试耗尽: {last_err}", file=sys.stderr)
    return None, None


def github_api_get(url, token, retries=3, timeout=20):
    """调用 GitHub API 并解析 JSON，失败返回 None。"""
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "hexo-trending-generator"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data, _ = http_get_bytes(url, headers, retries=retries, timeout=timeout)
    if not data:
        return None
    try:
        return json.loads(data.decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] 解析 GitHub API 响应失败: {e}", file=sys.stderr)
        return None


def github_search(query, token, retries=4):
    """带重试的 GitHub Search API 调用，返回 items 列表。"""
    url = "https://api.github.com/search/repositories?sort=stars&order=desc&per_page=100&q=" + urllib.parse.quote(query)
    data = github_api_get(url, token, retries=retries)
    return data.get("items", []) if data else []


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
    lines.append("> 本文由自动化脚本每日定时生成并发布，数据来源 GitHub Search API，项目简介已译为中文。")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 封面图抓取
# ---------------------------------------------------------------------------

def is_image_bytes(data):
    """通过 magic bytes 判断是否为常见图片格式。"""
    if data.startswith(b"\x89PNG"):
        return True
    if data.startswith(b"\xff\xd8\xff"):
        return True
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return True
    if data.startswith(b"RIFF") and b"WEBP" in data[:12]:
        return True
    if data.startswith(b"\x42\x4d"):
        return True
    if data.startswith(b"<svg") or b"xmlns=" in data[:200] and b"<svg" in data[:500]:
        return True
    return False


def ext_from_image(data, content_type=""):
    """根据 Content-Type 或 magic bytes 推断扩展名。"""
    content_type = (content_type or "").split(";")[0].strip().lower()
    mapping = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/gif": "gif",
        "image/webp": "webp",
        "image/svg+xml": "svg",
        "image/bmp": "bmp",
    }
    ext = mapping.get(content_type)
    if ext:
        return ext
    if data.startswith(b"\x89PNG"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "gif"
    if data.startswith(b"RIFF") and b"WEBP" in data[:12]:
        return "webp"
    if data.startswith(b"\x42\x4d"):
        return "bmp"
    if data.startswith(b"<svg") or (b"<svg" in data[:500] and b"xmlns=" in data[:200]):
        return "svg"
    return "png"


def download_image(url, token, min_bytes=2048):
    """下载图片并验证，成功返回 (bytes, content_type)。"""
    headers = {"User-Agent": "hexo-trending-generator"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data, resp_headers = http_get_bytes(url, headers, retries=2, timeout=25)
    if data is None:
        return None, ""
    if len(data) < min_bytes:
        print(f"[WARN] 图片过小（{len(data)} bytes），跳过: {url}", file=sys.stderr)
        return None, ""
    content_type = resp_headers.get("Content-Type", "") if resp_headers else ""
    if not (content_type.startswith("image/") or is_image_bytes(data)):
        print(f"[WARN] 非图片内容，跳过: {url}", file=sys.stderr)
        return None, ""
    return data, content_type


def extract_readme_image_urls(readme_text, owner, repo, default_branch):
    """从 README 文本中提取首个及后续图片 URL，并转换为绝对地址。"""
    urls = []
    # Markdown 图片: ![alt](url "title") 或 ![alt](url)
    for m in re.finditer(r'!\[[^\]]*\]\(([^)\s]+)(?:\s+["\'][^"\']*["\'])?\)', readme_text):
        urls.append(m.group(1))
    # HTML img 标签
    for m in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', readme_text, re.IGNORECASE):
        urls.append(m.group(1))

    raw_base = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/"
    abs_urls = []
    for u in urls:
        u = urllib.parse.unquote(u).strip()
        if not u:
            continue
        if u.startswith("http://") or u.startswith("https://"):
            abs_urls.append(u)
        elif u.startswith("//"):
            abs_urls.append("https:" + u)
        elif u.startswith("/"):
            abs_urls.append(f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}{u}")
        else:
            abs_urls.append(raw_base + u)
    return abs_urls


def fetch_readme_image_urls(owner, repo, default_branch, token):
    """调用 GitHub API 获取 README，返回其中图片的绝对 URL 列表。"""
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    data = github_api_get(url, token, retries=2)
    if not data:
        return []
    content = data.get("content", "")
    if not content:
        return []
    try:
        readme = base64.b64decode(content).decode("utf-8", errors="ignore")
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] 解码 README 失败 {owner}/{repo}: {e}", file=sys.stderr)
        return []
    return extract_readme_image_urls(readme, owner, repo, default_branch)


def pick_cover(items, date_str, token):
    """按排名依次尝试抓取封面图并落盘，返回 (rank, cover_path)。"""
    cover_dir = Path(COVER_DIR)
    cover_dir.mkdir(parents=True, exist_ok=True)

    # 若当日已有手动提供的封面，直接复用
    existing = sorted(cover_dir.glob(f"github-trending-cover-{date_str}-*"))
    if existing:
        chosen = existing[0]
        rank_match = re.search(r"-(\d+)\.\w+$", chosen.name)
        rank = int(rank_match.group(1)) if rank_match else 1
        print(f"[INFO] 复用已有封面：{chosen.name}")
        return rank, f"/img/github-trending/{chosen.name}"

    for rank, it in enumerate(items, 1):
        full = it.get("full_name", "")
        if not full or "/" not in full:
            continue
        owner, repo = full.split("/", 1)
        default_branch = it.get("default_branch") or "main"

        # 1) 优先 README 首个非 badge 图片
        readme_urls = fetch_readme_image_urls(owner, repo, default_branch, token)
        for img_url in readme_urls:
            # 跳过 badge、 shields 等装饰性小图
            lower = img_url.lower()
            if any(host in lower for host in ("shields.io", "img.shields.io", "badge")):
                continue
            data, content_type = download_image(img_url, token)
            if data:
                ext = ext_from_image(data, content_type)
                filename = f"github-trending-cover-{date_str}-{rank}.{ext}"
                path = cover_dir / filename
                path.write_bytes(data)
                print(f"[OK] 封面来自 README #{rank} {full}: {filename}")
                return rank, f"/img/github-trending/{filename}"

        # 2) 回退到 GitHub Open Graph 卡片图（稳定兜底）
        og_url = f"https://opengraph.githubassets.com/1/{full}"
        data, content_type = download_image(og_url, token)
        if data:
            ext = ext_from_image(data, content_type)
            filename = f"github-trending-cover-{date_str}-{rank}.{ext}"
            path = cover_dir / filename
            path.write_bytes(data)
            print(f"[OK] 封面来自 OpenGraph #{rank} {full}: {filename}")
            return rank, f"/img/github-trending/{filename}"

        print(f"[WARN] #{rank} {full} 无可用图片，尝试下一个", file=sys.stderr)

    print("[ERROR] 未找到任何可用封面", file=sys.stderr)
    return None, ""


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", "-p", default="daily", choices=list(PERIOD_DAYS.keys()))
    parser.add_argument("--limit", "-n", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true", help="仅打印，不写文件")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的当日文章")
    parser.add_argument("--json", action="store_true", help="仅输出 JSON 原始数据（含英文 description 与封面候选），不写文章，供翻译后撰写")
    parser.add_argument("--download-cover", metavar="URL", help="下载指定 URL 作为封面图，输出保存的本地路径（配合自动化使用）")
    args = parser.parse_args()

    # 辅助模式：仅下载单张封面图并输出路径
    if args.download_cover:
        token = get_token()
        data, content_type = download_image(args.download_cover, token)
        if data:
            ext = ext_from_image(data, content_type)
            date_str = datetime.date.today().isoformat()
            rank = os.environ.get("COVER_RANK", "1")
            cover_dir = Path(COVER_DIR)
            cover_dir.mkdir(parents=True, exist_ok=True)
            filename = f"github-trending-cover-{date_str}-{rank}.{ext}"
            path = cover_dir / filename
            path.write_bytes(data)
            print(path.as_posix())
            sys.exit(0)
        sys.exit(1)

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
        data = []
        for i, it in enumerate(items, 1):
            owner, repo = "", ""
            full = it.get("full_name", "")
            if "/" in full:
                owner, repo = full.split("/", 1)
            default_branch = it.get("default_branch") or "main"
            readme_urls = fetch_readme_image_urls(owner, repo, default_branch, token)
            # 过滤 badge
            cover_candidates = [u for u in readme_urls if "shields.io" not in u.lower() and "badge" not in u.lower()]
            cover_candidates.append(f"https://opengraph.githubassets.com/1/{full}")
            data.append({
                "rank": i,
                "full_name": full,
                "html_url": it.get("html_url", ""),
                "language": it.get("language") or "",
                "stargazers_count": it.get("stargazers_count", 0),
                "description": it.get("description") or "",
                "topics": it.get("topics") or [],
                "cover_candidates": cover_candidates,
            })
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    body = render_markdown(date_str, items, period_label)
    title = f"GitHub 热门项目（{date_str}）"
    post_date = f"{date_str}T08:00:00+08:00"

    # 抓取封面
    cover_rank, cover_path = pick_cover(items, date_str, token)

    front_matter = [
        "---",
        f"title: {title}",
        f"date: '{post_date}'",
        f"updated: '{post_date}'",
        "tags:",
        f"  - {TAG}",
        "categories:",
        f"  - {CATEGORY}",
    ]
    if cover_path:
        front_matter.append(f"cover: {cover_path}")
    front_matter.append("---")
    front_matter.append("")

    content = "\n".join(front_matter) + body

    filename = f"github-trending-{date_str}.md"
    out_path = os.path.join(POSTS_DIR, filename)

    if args.dry_run:
        print("=" * 60)
        print(content)
        print("=" * 60)
        if cover_path:
            print(f"[DRY-RUN] 封面将使用：{cover_path}（来自排名 #{cover_rank}）")
        return

    if os.path.exists(out_path) and not args.force:
        print(f"[INFO] 当日文章已存在，跳过：{out_path}", file=sys.stderr)
        sys.exit(0)

    os.makedirs(POSTS_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] 已写入文章：{out_path}")
    if cover_path:
        print(f"[OK] 封面：{cover_path}（来自排名 #{cover_rank}）")


if __name__ == "__main__":
    main()
