/* ===========================================================
   Windows ISO 构建下载页面 · 共享渲染逻辑
   依赖：window.WIN_ISO_DATA（source/js/win-iso-data.js）
   用法：页面根节点 <div class="win-iso" id="winIsoRoot" data-page="win11">
   - 按 data-page 聚合 pages[].categories 下的所有构建
   - 默认每页展示最新 2 个版本，其余翻页
   - 支持搜索（版本号/日期/标签）、排序、子版本筛选（多分类页）
   =========================================================== */
(function () {
  "use strict";

  function init() {
    var root = document.getElementById("winIsoRoot");
    if (!root) return;
    var DATA = window.WIN_ISO_DATA;
    if (!DATA || !DATA.releases) {
      var sub = document.getElementById("wiSub");
      if (sub) sub.textContent = "数据加载失败：未找到 /js/win-iso-data.js，请先运行 tools/gen_win_iso_data.py 生成。";
      return;
    }

    var pageKey = root.getAttribute("data-page") || "win11";
    var page = (DATA.pages || []).filter(function (p) { return p.key === pageKey; })[0]
      || { key: pageKey, label: pageKey, tag: pageKey, categories: [pageKey] };

    var PAGE_SIZE = 2; // 默认展示最新 2 个版本
    var state = { search: "", sort: "date-desc", sub: null, page: 1 };

    function fmtSize(bytes) {
      if (!bytes && bytes !== 0) return "-";
      var gb = bytes / 1024 / 1024 / 1024;
      if (gb >= 1) return gb.toFixed(2) + " GB";
      var mb = bytes / 1024 / 1024;
      return mb.toFixed(1) + " MB";
    }

    function esc(s) {
      return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
      });
    }

    function allReleases() {
      var list = [];
      page.categories.forEach(function (c) {
        (DATA.releases[c] || []).forEach(function (r) { list.push(r); });
      });
      return list;
    }

    // ---- 搜索过滤（可被外部单测复用：window.__winIsoFilter） ----
    function applyFilters(list) {
      if (state.sub) list = list.filter(function (r) { return r.category === state.sub; });
      if (state.search) {
        var q = state.search.toLowerCase();
        list = list.filter(function (r) {
          return (r.build + " " + r.date + " " + r.tag + " " + (r.title || "")).toLowerCase().indexOf(q) !== -1;
        });
      }
      return list;
    }

    function sortList(list) {
      return list.sort(function (a, b) {
        switch (state.sort) {
          case "date-asc": return a.date < b.date ? -1 : 1;
          case "size-desc": return b.total_size - a.total_size;
          case "build-desc": return (b.build || "").localeCompare(a.build || "");
          default: return a.date < b.date ? 1 : -1; // date-desc
        }
      });
    }

    function currentList() {
      return sortList(applyFilters(allReleases()));
    }

    function mirrorBtn(p) {
      var primary = p.mirrors[0];
      var links = "";
      p.mirrors.forEach(function (m) {
        links += '<li><a href="' + esc(m.url) + '" target="_blank" rel="noopener">' + esc(m.name) + "</a></li>";
      });
      links += '<li><a href="' + esc(p.official_url) + '" target="_blank" rel="noopener">官方直链（GitHub）</a></li>';
      return "" +
        '<a class="wi-btn wi-btn-primary" href="' + esc(primary.url) + '" target="_blank" rel="noopener">' +
          '<i class="fas fa-bolt"></i> 加速下载</a>' +
        '<details class="wi-mirrors"><summary>其他镜像</summary>' +
          "<ul>" + links + "</ul>" +
          '<p class="wi-mirror-tip">主用 ' + esc(primary.name) + "，备用节点请按需切换</p>" +
        "</details>";
    }

    function cardHTML(r) {
      var parts = r.parts.map(function (p) {
        return "" +
          '<li class="wi-part">' +
            '<div class="wi-part-info">' +
              '<span class="wi-part-name" title="' + esc(p.name) + '">' + esc(p.name) + "</span>" +
              '<span class="wi-part-size">' + fmtSize(p.size) + "</span>" +
            "</div>" +
            '<div class="wi-part-dl">' + mirrorBtn(p) + "</div>" +
          "</li>";
      }).join("");

      var sha = r.sha256
        ? '<button class="wi-sha" data-sha="' + esc(r.sha256) + '" type="button" title="点击复制 SHA256">' +
            '<i class="fas fa-fingerprint"></i> <code>' + esc(r.sha256.slice(0, 16)) + "…</code> 复制</button>"
        : '<span class="wi-sha-empty">无 SHA256</span>';

      var subBadge = page.categories.length > 1
        ? '<span class="wi-badge wi-badge-sub">' + esc(DATA.category_label[r.category] || r.category) + "</span>"
        : "";

      return "" +
        '<article class="wi-card">' +
          '<header class="wi-card-head">' +
            '<span class="wi-badge">' + esc(page.label) + "</span>" + subBadge +
            '<div class="wi-card-title">' +
              "<h3>Build " + esc(r.build || "—") + "</h3>" +
              '<span class="wi-date"><i class="far fa-calendar-alt"></i> 构建日期 ' + esc(r.date || "—") + "</span>" +
            "</div>" +
          "</header>" +
          '<div class="wi-meta">' +
            '<div class="wi-meta-item"><span>总大小</span><b>' + fmtSize(r.total_size) + "</b></div>" +
            '<div class="wi-meta-item"><span>分卷</span><b>' + r.parts.length + " 个</b></div>" +
            '<div class="wi-meta-item wi-meta-sha"><span>SHA256</span>' + sha + "</div>" +
          "</div>" +
          '<ul class="wi-parts">' + parts + "</ul>" +
        "</article>";
    }

    function renderStats() {
      var all = allReleases();
      var latest = all[0];
      var totalGB = all.reduce(function (s, r) { return s + (r.total_size || 0); }, 0) / 1024 / 1024 / 1024;
      var stats = [
        [String(all.length), "个构建版本"],
        [latest ? esc(latest.build) : "—", "最新版本"],
        [latest ? esc(latest.date) : "—", "最近构建"],
        [totalGB.toFixed(1) + " GB", "累计体积"]
      ].map(function (kv) {
        return '<div class="wi-stat"><b>' + kv[0] + "</b><span>" + kv[1] + "</span></div>";
      }).join("");
      document.getElementById("wiStats").innerHTML = stats;
    }

    function renderSubfilter() {
      var box = document.getElementById("wiSubfilter");
      if (!box) return;
      if (page.categories.length <= 1) { box.innerHTML = ""; box.style.display = "none"; return; }
      box.style.display = "flex";
      var chips = ['<button class="wi-chip' + (state.sub ? "" : " active") + '" data-sub="">全部</button>'];
      page.categories.forEach(function (c) {
        if (!DATA.releases[c] || !DATA.releases[c].length) return;
        var cls = "wi-chip" + (state.sub === c ? " active" : "");
        chips.push('<button class="' + cls + '" data-sub="' + esc(c) + '">' + esc(DATA.category_label[c] || c) + "</button>");
      });
      box.innerHTML = chips.join("");
    }

    function renderList() {
      var list = currentList();
      var box = document.getElementById("wiList");
      var pager = document.getElementById("wiPager");

      if (!list.length) {
        box.innerHTML = '<div class="wi-empty">没有匹配的构建版本</div>';
        pager.innerHTML = "";
        return;
      }

      var totalPages = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
      if (state.page > totalPages) state.page = totalPages;
      if (state.page < 1) state.page = 1;
      var start = (state.page - 1) * PAGE_SIZE;
      var pageItems = list.slice(start, start + PAGE_SIZE);

      box.innerHTML = pageItems.map(cardHTML).join("");
      renderPager(list.length, totalPages);
    }

    function renderPager(total, totalPages) {
      var pager = document.getElementById("wiPager");
      if (totalPages <= 1) { pager.innerHTML = ""; return; }
      var html = '<div class="wi-pager-info">共 ' + total + " 个版本 · 第 " + state.page + " / " + totalPages + " 页（每页 " + PAGE_SIZE + " 个）</div>";

      html += '<button data-page="' + (state.page - 1) + '"' + (state.page <= 1 ? " disabled" : "") + '><i class="fas fa-chevron-left"></i></button>';
      for (var i = 1; i <= totalPages; i++) {
        html += '<button data-page="' + i + '" class="' + (i === state.page ? "active" : "") + '">' + i + "</button>";
      }
      html += '<button data-page="' + (state.page + 1) + '"' + (state.page >= totalPages ? " disabled" : "") + '><i class="fas fa-chevron-right"></i></button>';

      pager.innerHTML = html;
    }

    function renderAll() {
      renderStats();
      renderSubfilter();
      renderList();
    }

    // ---- 事件 ----
    root.addEventListener("click", function (e) {
      var chip = e.target.closest(".wi-chip");
      if (chip) {
        state.sub = chip.getAttribute("data-sub") || null;
        state.page = 1;
        renderAll();
        return;
      }
      var pg = e.target.closest(".wi-pager button[data-page]");
      if (pg && !pg.disabled) {
        state.page = parseInt(pg.getAttribute("data-page"), 10);
        renderList();
        window.scrollTo({ top: root.offsetTop - 80, behavior: "smooth" });
        return;
      }
      var shaBtn = e.target.closest(".wi-sha");
      if (shaBtn) {
        var txt = shaBtn.getAttribute("data-sha");
        var done = function () {
          var old = shaBtn.innerHTML;
          shaBtn.innerHTML = '<i class="fas fa-check"></i> 已复制';
          setTimeout(function () { shaBtn.innerHTML = old; }, 1500);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(txt).then(done, function () { fallbackCopy(txt, done); });
        } else {
          fallbackCopy(txt, done);
        }
      }
    });

    function fallbackCopy(text, cb) {
      var ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); } catch (err) {}
      document.body.removeChild(ta); cb();
    }

    document.getElementById("wiSearch").addEventListener("input", function (e) {
      state.search = e.target.value.trim();
      state.page = 1;
      renderList();
    });
    document.getElementById("wiSort").addEventListener("change", function (e) {
      state.sort = e.target.value;
      state.page = 1;
      renderList();
    });

    renderAll();

    // 数据加载完成后更新副标题
    var subEl = document.getElementById("wiSub");
    if (subEl) subEl.textContent = "数据来源：xfxx2022/win_iso_build Releases";

    // 暴露过滤函数，便于自动化单测（搜索功能验证）
    window.__winIsoFilter = function (q) {
      state.search = (q || "").trim();
      return applyFilters(allReleases());
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
