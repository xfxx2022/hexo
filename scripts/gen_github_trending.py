#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成「GitHub 热门项目」Hexo 文章。

数据源（--source）：
  - trending（默认）：抓取 github.com/trending 真实热榜，按 24h/7d/30d 星标增速排序，
                      天然每天变化，最贴近官方热榜。可加 --lang 按语言筛选。
  - api：回退到 GitHub Search（created 窗口），保证变化；trending 抓取失败时使用。

特性：
  - 自动按排名抓取项目 README 首个图片或 GitHub Open Graph 作为封面并落盘
  - 令牌优先取自 `gh auth token`，其次环境变量 GITHUB_TOKEN
  - 自带 SSL 瞬时中断重试 + HTTP(S)_PROXY 代理识别
  - 写入 Hexo 的 source/_posts/，标签为「GitHub热门项目」，自动生成标签页

用法:
    python3 gen_github_trending.py                          # 抓取今日真实热榜 + 封面并写文章
    python3 gen_github_trending.py --source api             # 用 Search API 回退
    python3 gen_github_trending.py --lang python            # 仅 Python 语言热榜
    python3 gen_github_trending.py --since weekly           # 本周热榜
    python3 gen_github_trending.py --period weekly          # 同 --since weekly
    python3 gen_github_trending.py --json                   # 仅输出 JSON（含封面候选与已落盘封面路径），供翻译后撰写
    python3 gen_github_trending.py --dry-run                # 仅打印，不写文件
    python3 gen_github_trending.py --force                  # 覆盖已存在的当日文章
    python3 gen_github_trending.py --download-cover "URL"   # 下载指定 URL 作为封面（配合自动化）
"""

import argparse
import base64
import datetime
import io
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
IMG_DIR = os.path.join(ROOT_DIR, "source", "img")
TAG = "GitHub热门项目"
CATEGORY = "技术分享"
AI_KEYWORDS = ("ai", "agent", "llm", "gpt", "ml", "machine learning", "deep learning",
               "chatbot", "assistant", "automation", "workflow", "rag", "transformer")


def cover_paths_for(date_str):
    """返回 (本地目录 Path, web 引用前缀)。

    按项目已有 source/img/YYYY/MM/DD 日期目录逻辑存放每日爬取的封面图。
    """
    y, m, d = date_str.split("-")
    cover_dir = Path(IMG_DIR) / y / m / d
    web_prefix = f"/img/{y}/{m}/{d}"
    return cover_dir, web_prefix

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


# 全局 opener（自动识别 HTTP(S)_PROXY 代理）
_OPENER = None


def _build_opener():
    proxies = {}
    for proto in ("http", "https"):
        env = os.environ.get(f"{proto.upper()}_PROXY") or os.environ.get(f"{proto}_proxy")
        if env:
            proxies[proto] = env
    if proxies:
        return urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
    return urllib.request.build_opener()


def http_get_bytes(url, headers=None, retries=3, timeout=20):
    """带重试的通用 HTTP GET，返回 (bytes, headers)。自动识别 HTTP(S)_PROXY。"""
    global _OPENER
    if _OPENER is None:
        _OPENER = _build_opener()
    headers = dict(headers or {})
    headers.setdefault(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    )
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with _OPENER.open(req, timeout=timeout) as resp:
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


# ---------------------------------------------------------------------------
# 真实 GitHub Trending 抓取
# ---------------------------------------------------------------------------

def scrape_github_trending(since="daily", language=""):
    """抓取 github.com/trending 真实热榜。

    since: daily / weekly / monthly
    language: 语言 slug（如 python、typescript），为空表示全部
    返回 item 列表（含 full_name/description/language/stargazers_count 等）。
    """
    url = "https://github.com/trending"
    if language:
        url += "/" + urllib.parse.quote(language, safe="")
    url += f"?since={since}"
    html, _ = http_get_bytes(url, retries=3, timeout=25)
    if not html:
        return None
    try:
        text = html.decode("utf-8", errors="ignore")
    except Exception:
        return None
    return parse_trending_html(text)


def parse_trending_html(text):
    """解析 github.com/trending HTML，提取每个仓库信息。"""
    items = []
    blocks = re.split(r'<article class="Box-row">', text)[1:]
    for block in blocks:
        # 仓库名链接位于 <h2> 内；GitHub 的 <a> 带有 data-hydro-click 等属性，
        # 故在 h2 范围内抓取首个 "owner/repo" 形式的链接（避开 /login?... 等）
        hm = re.search(r'<h2.*?</h2>', block, re.S)
        h2 = hm.group(0) if hm else block
        m = re.search(r'href="/([\w.\-]+/[\w.\-]+)"', h2)
        if not m:
            continue
        full = m.group(1).strip("/")
        if full.count("/") != 1:
            continue
        owner, repo = full.split("/", 1)

        dm = re.search(r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>\s*(.*?)\s*</p>', block, re.S)
        desc = ""
        if dm:
            desc = re.sub(r"<[^>]+>", "", dm.group(1)).strip()
            desc = re.sub(r"\s+", " ", desc)

        lm = re.search(r'<span itemprop="programmingLanguage">([^<]+)</span>', block)
        lang = lm.group(1).strip() if lm else ""

        sm = re.search(r'href="/[^"]*stargazers"[^>]*>.*?([\d,]+)\s*</a>', block, re.S)
        stars = int(sm.group(1).replace(",", "")) if sm else 0

        tm = re.search(r'([\d,]+)\s+stars (today|this week|this month)', block)
        stars_period = int(tm.group(1).replace(",", "")) if tm else None

        items.append({
            "full_name": full,
            "owner": owner,
            "repo": repo,
            "html_url": f"https://github.com/{full}",
            "description": desc,
            "language": lang,
            "stargazers_count": stars,
            "stars_period": stars_period,
            "topics": [],
            "default_branch": "main",
        })
    return items


def _fetch_via_api(period, limit, token):
    """Search API 回退：用 created 窗口保证每天变化（展示近期新建高星项目）。"""
    days = PERIOD_DAYS.get(period, 1)
    window = max(days, 3)
    since = (datetime.date.today() - datetime.timedelta(days=window)).isoformat()
    query = f"created:>={since} stars:>=20"
    items = github_search(query, token)
    seen = set()
    unique = []
    for it in items:
        full = it.get("full_name", "")
        if full in seen:
            continue
        seen.add(full)
        unique.append(it)
    return unique[:limit]


def fetch_trending(period, limit, token, source="trending", language="", since=None):
    """获取趋势项目。

    source=trending：抓取 github.com/trending 真实热榜（按星标增速，天然每天变化）。
    source=api：回退到 GitHub Search（created 窗口）。
    """
    since = since or period  # daily / weekly / monthly
    if source == "api":
        return _fetch_via_api(period, limit, token)
    items = scrape_github_trending(since=since, language=language)
    if items:
        print(f"[INFO] 抓取 github trending 成功：{len(items)} 项（since={since}, lang={language or '全部'}）")
        return items[:limit]
    print("[WARN] 抓取 github trending 失败，回退到 Search API", file=sys.stderr)
    return _fetch_via_api(period, limit, token)


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
        desc = (it.get("description_zh") or it.get("description") or "").replace("\n", " ").strip()
        if len(desc) > 60:
            desc = desc[:60] + "…"
        proj = f"[{full}]({url})"
        lines.append(f"| {idx} | {proj} | {lang} | {stars} | {desc} |")
    lines.append("")
    lines.append("## 趋势观察")
    lines.append("")
    lines.append(f"- 本期样本中 AI / 自动化 / Agent 方向占比约 **{pct}%**，仍是当前最热赛道。")
    lines.append(f"- 语言分布领先者为：{lang_str}。")
    lines.append("- 数据来源 GitHub Trending（github.com/trending，按近期星标增速排序），每天自然变化，与官方热榜口径一致。")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> 本文由自动化脚本每日定时生成并发布，数据来源 GitHub Trending，项目简介已译为中文。")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 中文翻译（无人值守环境：GitHub Actions 等）
# 优先级：GitHub Models (gpt-4o-mini, 免费) -> MyMemory (免费) -> 原文(英文)
# 任一环节失败都安全回退，绝不中断生成流程。
# ---------------------------------------------------------------------------
GITHUB_MODELS_ENDPOINT = "https://models.inference.ai.azure.com/openai/v1/chat/completions"
TRANSLATE_MODEL = os.environ.get("TRENDING_MODEL", "gpt-4o-mini")
MYMEMORY_ENDPOINT = "https://api.mymemory.translated.net/get"


def _post_json(url, payload, headers, timeout=30):
    """发送 JSON POST，返回解析后的 dict；失败抛异常。"""
    global _OPENER
    if _OPENER is None:
        _OPENER = _build_opener()
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with _OPENER.open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _parse_translation_block(content, n):
    """把模型返回解析成正好 n 条的翻译列表；格式不符返回 None。"""
    content = (content or "").strip()
    if not content:
        return None
    # 1) 直接 JSON 数组
    if content.startswith("["):
        try:
            arr = json.loads(content)
            if isinstance(arr, list) and len(arr) == n:
                return [str(x).strip() for x in arr]
        except Exception:  # noqa: BLE001
            pass
    # 2) 每行一条（容错去编号）
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    cleaned = []
    for ln in lines:
        m = re.match(r"^\d+[.、)]\s*(.*)$", ln)
        cleaned.append(m.group(1).strip() if m else ln)
    if len(cleaned) == n:
        return cleaned
    return None


def translate_via_github_models(descriptions):
    """用 GitHub Models (GITHUB_TOKEN) 翻译，返回 n 条列表或 None。"""
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "hexo-trending-generator",
    }
    joined = "\n".join(f"{i+1}. {d}" for i, d in enumerate(descriptions))
    payload = {
        "model": TRANSLATE_MODEL,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": "你是专业的技术文档翻译，请将 GitHub 仓库英文简介准确、简洁地译为简体中文，保留专有名词。只输出翻译结果。"},
            {"role": "user", "content": f"请将以下 {len(descriptions)} 条 GitHub 仓库简介译为简体中文，严格按原顺序、每行一条、不要编号、不要任何额外说明：\n{joined}"},
        ],
    }
    try:
        resp = _post_json(GITHUB_MODELS_ENDPOINT, payload, headers)
        content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
        return _parse_translation_block(content, len(descriptions))
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] GitHub Models 翻译失败: {e}", file=sys.stderr)
        return None


def translate_via_mymemory(descriptions):
    """用 MyMemory 免费翻译逐条兜底，失败则保留原文。始终返回 n 条列表。"""
    out = []
    for d in descriptions:
        d = (d or "").strip()
        if not d:
            out.append(d)
            continue
        try:
            url = f"{MYMEMORY_ENDPOINT}?q={urllib.parse.quote(d)}&langpair=en|zh-CN"
            data, _ = http_get_bytes(url, retries=2, timeout=15)
            if data:
                j = json.loads(data.decode("utf-8"))
                txt = (j.get("responseData") or {}).get("translatedText", "")
                if txt and "MYMEMORY WARNING" not in txt:
                    out.append(txt.strip())
                    continue
        except Exception as e:  # noqa: BLE001
            print(f"[WARN] MyMemory 翻译失败: {e}", file=sys.stderr)
        out.append(d)  # 失败回退原文
        time.sleep(0.3)  # 轻量限速，避免触发频率限制
    return out


def translate_descriptions(items):
    """为 items 注入 description_zh。GitHub Models -> MyMemory -> 英文原文。"""
    descs = [(it.get("description") or "").strip() for it in items]
    if not any(descs):
        for it in items:
            it["description_zh"] = it.get("description") or ""
        return
    zh = translate_via_github_models(descs)
    if zh is None:
        print("[INFO] 回退到 MyMemory 翻译", file=sys.stderr)
        zh = translate_via_mymemory(descs)
    for it, t in zip(items, zh):
        it["description_zh"] = t if t else (it.get("description") or "")


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


def save_cover_webp(data, content_type, cover_dir, web_prefix, date_str, rank):
    """落盘封面图：优先转 WebP（quality=82）。

    - 依赖 Pillow 做格式转换；若环境无 Pillow / 转换异常 / 源为矢量图，
      则回退为原格式落盘，保证生成流程永不中断。
    - 透明通道（RGBA/LA/P）白底合成，避免透明区变黑。
    返回 (filename, web_path)。
    """
    webp_name = f"github-trending-cover-{date_str}-{rank}.webp"
    webp_path = cover_dir / webp_name
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data))
        mode = img.mode
        if mode in ("RGBA", "LA", "P"):
            rgb = img.convert("RGBA")
            bg = Image.new("RGB", rgb.size, (255, 255, 255))
            bg.paste(rgb, mask=rgb.split()[-1])
            img = bg
        elif mode != "RGB":
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, "WEBP", quality=82, method=4)
        webp_path.write_bytes(buf.getvalue())
        return webp_name, f"{web_prefix}/{webp_name}"
    except Exception as e:
        ext = ext_from_image(data, content_type)
        fallback_name = f"github-trending-cover-{date_str}-{rank}.{ext}"
        (cover_dir / fallback_name).write_bytes(data)
        print(f"[WARN] WebP 转换失败，回退原格式 {ext}：{e}", file=sys.stderr)
        return fallback_name, f"{web_prefix}/{fallback_name}"


def extract_readme_image_urls(readme_text, owner, repo, default_branch):
    """从 README 文本中提取首个及后续图片 URL，并转换为绝对地址。"""
    urls = []
    for m in re.finditer(r'!\[[^\]]*\]\(([^)\s]+)(?:\s+["\'][^"\']*["\'])?\)', readme_text):
        urls.append(m.group(1))
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
    cover_dir, web_prefix = cover_paths_for(date_str)
    cover_dir.mkdir(parents=True, exist_ok=True)

    # 若当日已有手动提供的封面，直接复用（优先 WebP 版本）
    existing = sorted(cover_dir.glob(f"github-trending-cover-{date_str}-*"))
    if existing:
        webp_hits = [f for f in existing if f.suffix == ".webp"]
        chosen = (webp_hits or existing)[0]
        rank_match = re.search(r"-(\d+)\.\w+$", chosen.name)
        rank = int(rank_match.group(1)) if rank_match else 1
        print(f"[INFO] 复用已有封面：{chosen.name}")
        return rank, f"{web_prefix}/{chosen.name}"

    for rank, it in enumerate(items, 1):
        full = it.get("full_name", "")
        if not full or "/" not in full:
            continue
        owner, repo = full.split("/", 1)
        default_branch = it.get("default_branch") or "main"

        # 1) 优先 README 首个非 badge 图片
        readme_urls = fetch_readme_image_urls(owner, repo, default_branch, token)
        for img_url in readme_urls:
            lower = img_url.lower()
            if any(host in lower for host in ("shields.io", "img.shields.io", "badge")):
                continue
            data, content_type = download_image(img_url, token)
            if data:
                filename, rel = save_cover_webp(data, content_type, cover_dir, web_prefix, date_str, rank)
                print(f"[OK] 封面来自 README #{rank} {full}: {filename}")
                return rank, rel

        # 2) 回退到 GitHub Open Graph 卡片图（稳定兜底）
        og_url = f"https://opengraph.githubassets.com/1/{full}"
        data, content_type = download_image(og_url, token)
        if data:
            filename, rel = save_cover_webp(data, content_type, cover_dir, web_prefix, date_str, rank)
            print(f"[OK] 封面来自 OpenGraph #{rank} {full}: {filename}")
            return rank, rel

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
    parser.add_argument("--json", action="store_true", help="仅输出 JSON 原始数据（含封面候选与已落盘封面路径），不写文章，供翻译后撰写")
    parser.add_argument("--source", "-s", default="trending", choices=["trending", "api"],
                        help="数据源：trending=抓取 github.com/trending 真实热榜；api=GitHub Search 回退")
    parser.add_argument("--lang", default="", help="按编程语言筛选热榜（如 python、typescript），仅 trending 源有效")
    parser.add_argument("--since", default=None, choices=["daily", "weekly", "monthly"],
                        help="trending 时间窗口，默认同 --period")
    parser.add_argument("--no-cover", action="store_true", help="跳过封面图抓取")
    parser.add_argument("--download-cover", metavar="URL", help="下载指定 URL 作为封面图，输出保存的本地路径（配合自动化使用）")
    args = parser.parse_args()

    # 辅助模式：仅下载单张封面图并输出路径
    if args.download_cover:
        token = get_token()
        data, content_type = download_image(args.download_cover, token)
        if data:
            date_str = datetime.date.today().isoformat()
            rank = os.environ.get("COVER_RANK", "1")
            cover_dir, web_prefix = cover_paths_for(date_str)
            cover_dir.mkdir(parents=True, exist_ok=True)
            filename, rel = save_cover_webp(data, content_type, cover_dir, web_prefix, date_str, rank)
            print((cover_dir / filename).as_posix())
            sys.exit(0)
        sys.exit(1)

    today = datetime.date.today()
    date_str = today.isoformat()
    period_label = {"daily": "今日", "weekly": "近 7 天", "monthly": "近 30 天"}[args.period]

    token = get_token()
    if not token:
        print("[WARN] 未获取到 GitHub 令牌，将使用匿名限额（10 次/分钟）。", file=sys.stderr)
    print(f"[INFO] 正在获取 GitHub 热门（source={args.source}, since={args.since or args.period}, lang={args.lang or '全部'}）...")

    items = fetch_trending(args.period, args.limit, token,
                           source=args.source, language=args.lang, since=args.since)
    if not items:
        print("[ERROR] 未获取到任何项目，退出。", file=sys.stderr)
        sys.exit(1)
    print(f"[INFO] 获取到 {len(items)} 个项目")

    # 注入中文翻译（GitHub Models -> MyMemory -> 英文原文），CI 无人值守可用
    translate_descriptions(items)

    if args.json:
        # 脚本内一次性抓取封面，减少自动化工具调用次数
        cover_rank, cover_path = (None, "")
        if not args.no_cover:
            cover_rank, cover_path = pick_cover(items, date_str, token)
        data = []
        for i, it in enumerate(items, 1):
            owner, repo = "", ""
            full = it.get("full_name", "")
            if "/" in full:
                owner, repo = full.split("/", 1)
            default_branch = it.get("default_branch") or "main"
            readme_urls = fetch_readme_image_urls(owner, repo, default_branch, token)
            cover_candidates = [u for u in readme_urls if "shields.io" not in u.lower() and "badge" not in u.lower()]
            cover_candidates.append(f"https://opengraph.githubassets.com/1/{full}")
            item_cover = cover_path if cover_rank == i else ""
            data.append({
                "rank": i,
                "full_name": full,
                "html_url": it.get("html_url", ""),
                "language": it.get("language") or "",
                "stargazers_count": it.get("stargazers_count", 0),
                "description": it.get("description") or "",
                "description_zh": it.get("description_zh") or "",
                "topics": it.get("topics") or [],
                "cover_candidates": cover_candidates,
                "cover_path": item_cover,
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
