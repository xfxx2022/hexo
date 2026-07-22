// scripts/canonical.js
// 为每页注入 <link rel="canonical">，改善 SEO（避免分页/标签页重复内容）。
// 注意：Butterfly 主题自身也会在 head.pug 注入 canonical（默认带 /index.html 后缀），
// 因此本脚本先移除已有 canonical，再注入规范化后的版本，确保：
//   首页 -> https://blog.1314151.xyz/
//   文章 -> https://blog.1314151.xyz/posts/xxx/
//   标签页 -> https://blog.1314151.xyz/tags/
hexo.extend.filter.register('after_render:html', function (str, data) {
  if (!str || !data || !data.page) return str;
  var config = hexo.config;
  var page = data.page;
  var canonical = page.permalink;
  if (!canonical && page.path) {
    canonical = (config.url || '').replace(/\/$/, '') + '/' + page.path.replace(/index\.html$/, '');
  }
  if (!canonical) return str;
  // 去掉末尾 index.html，规范为目录形式
  canonical = canonical.replace(/index\.html$/, '');
  // 移除主题/Hexo 可能已注入的 canonical（往往带 /index.html 后缀），避免重复与错误
  str = str.replace(/<link[^>]*rel=["']canonical["'][^>]*>/i, '');
  var tag = '<link rel="canonical" href="' + canonical + '">';
  if (str.indexOf('</head>') !== -1) {
    return str.replace('</head>', tag + '\n</head>');
  }
  return str;
});
