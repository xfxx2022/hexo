/**
 * 静态资源压缩管线
 * 在 `hexo generate` 之后对 public/ 下的 HTML / CSS / JS 做 minify。
 * 通过 package.json 的 `build` 脚本自动串联：hexo generate && gulp
 */
const gulp = require('gulp');
const { Transform } = require('stream');
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
    .pipe(gulp.dest('public'));
}

// 压缩 CSS
function minifyCss() {
  return gulp.src('public/**/*.css', { encoding: false })
    .pipe(cleanCSS({ compatibility: 'ie11', level: 2 }))
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

exports.default = gulp.series(minifyHtml, minifyCss, minifyJs);
exports.html = minifyHtml;
exports.css = minifyCss;
exports.js = minifyJs;
