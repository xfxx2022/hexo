/**
 * 静态资源压缩管线
 * 在 `hexo generate` 之后对 public/ 下的 HTML / CSS / JS 做 minify。
 * 通过 package.json 的 `build` 脚本自动串联：hexo generate && gulp
 */
const gulp = require('gulp');
const { Transform } = require('stream');
const fs = require('fs');
const path = require('path');
const cleanCSS = require('gulp-clean-css');
const terser = require('terser');
const htmlmin = require('gulp-html-minifier-terser');

// 压缩 HTML（折叠空白 + 去注释 + 内联 CSS 压缩）。
// 注意：minifyJS 设为 false，避免破坏 Butterfly 内联脚本；外部 .js 由 terser 处理。
function minifyHtml() {
  return gulp.src('public/**/*.html', { encoding: false })
    .pipe(htmlmin({
      collapseWhitespace: true,
      removeComments: true,
      minifyCSS: true,
      minifyJS: false,
      ignoreCustomComments: [/^\s*<!--\s*#/], // 保留形如 <!-- #xxx 的 Hexo 注释
    }))
    .on('error', function (err) {
      console.error('[minifyHtml] 出错，保留原 HTML:', err.message);
      this.emit('end');
    })
    .pipe(gulp.dest('public'));
}

// 压缩 CSS
function minifyCss() {
  return gulp.src('public/**/*.css', { encoding: false })
    .pipe(cleanCSS({ compatibility: 'ie11', level: 1 }))
    .on('error', function (err) {
      console.error('[minifyCss] 出错，保留原 CSS:', err.message);
      this.emit('end');
    })
    .pipe(gulp.dest('public'));
}

// 压缩 JS（跳过已压缩的 .min.js）
// 逐文件容错：单个文件解析失败时保留原文件并继续，确保整条 stream 必定完成
function minifyJs() {
  const processor = new Transform({
    objectMode: true,
    async transform(file, enc, cb) {
      if (file.isNull() || file.isStream()) {
        return cb(null, file);
      }
      try {
        const code = file.contents.toString('utf8');
        const result = await terser.minify(code, {
          compress: { drop_console: false },
          ecma: 2020,
        });
        if (result.error) throw result.error;
        if (result.code != null) {
          file.contents = Buffer.from(result.code, 'utf8');
        }
      } catch (e) {
        console.error('[minifyJs] 跳过:', file.relative, '-', e.message);
      }
      cb(null, file);
    },
  });
  return gulp.src(['public/**/*.js', '!public/**/*.min.js'], { encoding: false })
    .pipe(processor)
    .pipe(gulp.dest('public'));
}

// 删除主题自动 copy 进 public 但配置已不再引用的孤儿资源，避免部署无用体积。
// - friend_404.gif：error_img.flink 已改为 webp，但主题 source/img 仍会被整包拷贝。
// - pluginsSrc 下 19 个第三方库：经逐包核查 built public(html/css/js) 引用，确认均未被加载
//   （对应功能已关闭或用外部 CDN）：
//     @fancyapps(fancybox 已换 medium_zoom)、@waline/valine/gitalk/disqusjs(评论用 twikoo 外部 CDN)、
//     algoliasearch+instantsearch.js(搜索用 /js/search/local-search.js)、aplayer(未启用)、
//     blueimp-md5(valine/waline 关闭)、flickr-justified-gallery(无画廊)、katex/mathjax(math 未启用)、
//     mermaid(未启用)、node-snackbar(未启用)、pangu(Butterfly5 已移除)、pjax(未启用)、
//     prismjs(主题用 highlight.js)、twikoo(外部 CDN)、typed.js(副标题关闭)
function cleanup() {
  const orphans = [
    'public/img/friend_404.gif',
    'public/pluginsSrc/@fancyapps',
    'public/pluginsSrc/@waline',
    'public/pluginsSrc/algoliasearch',
    'public/pluginsSrc/aplayer',
    'public/pluginsSrc/blueimp-md5',
    'public/pluginsSrc/disqusjs',
    'public/pluginsSrc/flickr-justified-gallery',
    'public/pluginsSrc/gitalk',
    'public/pluginsSrc/instantsearch.js',
    'public/pluginsSrc/katex',
    'public/pluginsSrc/mathjax',
    'public/pluginsSrc/mermaid',
    'public/pluginsSrc/node-snackbar',
    'public/pluginsSrc/pangu',
    'public/pluginsSrc/pjax',
    'public/pluginsSrc/prismjs',
    'public/pluginsSrc/twikoo',
    'public/pluginsSrc/typed.js',
    'public/pluginsSrc/valine',
  ];
  let removed = 0;
  orphans.forEach((rel) => {
    const p = path.join(__dirname, rel);
    if (fs.existsSync(p)) {
      try {
        if (fs.statSync(p).isDirectory()) {
          fs.rmSync(p, { recursive: true, force: true });
        } else {
          fs.unlinkSync(p);
        }
        removed++;
        console.log('[cleanup] 删除孤儿资源:', rel);
      } catch (e) {
        console.error('[cleanup] 删除失败:', rel, '-', e.message);
      }
    }
  });
  console.log(`[cleanup] 完成，共移除 ${removed} 个孤儿资源`);
  return Promise.resolve();
}

exports.default = gulp.series(minifyHtml, minifyCss, minifyJs, cleanup);
exports.html = minifyHtml;
exports.css = minifyCss;
exports.js = minifyJs;
exports.cleanup = cleanup;
