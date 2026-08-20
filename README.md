# 个人主页（Jekyll + Minimal Mistakes）

基于 [Jekyll](https://jekyllrb.com/) 与 [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) 主题构建的个人网站，通过 GitHub Pages 部署。本仓库已清空原模板作者的个人内容，只保留可复用的站点框架，供你在其上编写自己的内容。

> **开始前**：请全局搜索 `TODO` 与占位符 `YOUR_NAME`、`your-email@example.com`、`your-username`、`YOUR_SITE_TITLE`、`TODO`（链接占位），把它们替换为你的真实信息。

## 站点结构

| 栏目 | 路径 | 内容目录 | 说明 |
|---|---|---|---|
| 首页 | `/` | `index.html` | 欢迎语与最新文章列表 |
| 关于我 | `/about/` | `_pages/about.md` | 中文简历，另见 `/about-en/` 英文版 |
| 技术share | `/blog/` | `_posts/` | 博客文章（按 `YYYY-MM-DD-slug.md` 命名） |
| 科研学习 | `/research/` | `_research/` | 科研集合 |
| AI脑洞 | `/idea/` | `_idea/` | 观点 / 脑洞集合 |

## 本地构建

本地使用与 GitHub Pages 一致的环境（通过 `github-pages` gem）：

```bash
bundle install
bundle exec jekyll serve   # 本地预览 http://127.0.0.1:4000
bundle exec jekyll build    # 构建到 _site/
```

若 gem 安装较慢，可参照 GitHub 官方文档配置 Ruby 与 Bundler，或更换镜像源。

## 如何新增内容

- **博客文章（技术share）**：在 `_posts/` 下新建 `YYYY-MM-DD-slug.md`，front matter 参考 `layout: single`、`categories`、`tags` 等。
- **集合文章（科研学习 / AI脑洞）**：在对应集合目录（`_research/`、`_idea/`）下新建文档，front matter 参考现有格式。
- **页面**：在 `_pages/` 下新建 `.md`，通过 `permalink` 控制访问路径。

## 配置说明

站点元信息、导航、评论等均在 `_config.yml` 中配置。需要替换的占位项：

- **站点信息**：`title` / `subtitle` / `name` / `description` / `url` / `repository` / `masthead_title`
- **导航**：`_data/navigation.yml`（当前为「关于我 / 技术share / 科研学习 / AI脑洞」四项，可按需增删）
- **作者信息**：`_config.yml` 的 `author` 段（姓名、头像、简介、所在地、邮箱、社交链接），以及 `_data/authors.yml`
- **社交链接**：`author.links` 与 `footer.links` 当前仅保留 GitHub / 知乎 / 小红书 三项（占位 URL，需替换 `TODO`）；如需更多平台，参考 Minimal Mistakes 文档添加
- **页脚链接**：`footer.links`
- **评论（Giscus）**：需先在仓库启用 Discussions，然后在 [giscus.app](https://giscus.app) 生成 `repo_id` / `category_id`，填入 `_config.yml` 的 `comments.giscus` 字段（当前为 `YOUR_GISCUS_*` 占位）
- **统计**：如需 Google Analytics，填 `analytics.google.tracking_id`
- **图片**：`assets/images/` 下的站点图标占位（`logo.jpg`、`favicon-32x32.png`、`apple-touch-icon.png`、`og-default.png`、`404.jpg`）请替换为你自己的
- **搜索**：已移除（原 `search.json` / `assets/js/search.js` / `_pages/search.md` 已删除）；如需恢复站内搜索，可参考 Minimal Mistakes 文档重新接入

## 部署

推送 `master`（或 `main`）分支后，GitHub 自动通过 GitHub Pages 构建并发布。仓库设置中的 Pages 需指向正确的分支与目录（通常为 `/ (root)`）。

## 目录速览

```
_pages/       页面（关于、分类、标签、404）
_posts/       博客文章（技术share）
_idea/        AI脑洞集合
_research/    科研学习集合
_data/        站点数据（navigation、authors、ui-text）
_includes/    主题组件
_layouts/     页面布局
_sass/        Sass 样式
_scripts/     构建辅助脚本（数学公式处理）
assets/       图片、CSS、JS 资源
```

## 许可

个人内容归作者所有；主题代码基于 [MIT License](LICENSE) 的 Minimal Mistakes。
