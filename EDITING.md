# 内容编辑指南

本站由 Jekyll + Minimal Mistakes 构建，部署在 GitHub Pages。本文说明在哪些文件里编辑，就能让对应栏目、页面或配置生效。改完提交推送，GitHub 会自动重新构建，约 1-2 分钟后线上更新。

## 想改哪里，就编辑哪里

| 想做的事 | 编辑位置 | 说明 |
|---|---|---|
| 改站点标题、简介、社交链接、站点信息 | `_config.yml` | 集中配置，改完需等构建生效（见下文「改了不生效？」） |
| 发「技术share」博客文章 | `_posts/` | 文件名格式 `YYYY-MM-DD-标题英文.md` |
| 发「科研学习」文章 | `_research/` | 每篇一个 `.md` |
| 发「AI脑洞」文章 | `_idea/` | 每篇一个 `.md` |
| 改「关于我」简历 | `_pages/about.md` | 已填好基础信息，按章节骨架补充即可 |
| 改首页内容 | `index.html` | 当前是欢迎语占位，可自定义 |
| 换头像 / logo / 图标 / 图片 | `assets/images/` | 同名替换文件，或放新图后改引用路径 |

## 三类编辑的具体写法

### 1. 发一篇「技术share」博客（`_posts/`）

在 `_posts/` 下新建文件，命名 `2026-08-20-my-first-post.md`（日期 + 英文短标题）。开头是 front matter：

```markdown
---
title: 文章标题
date: 2026-08-20
categories: [技术]
tags: [Python, 笔记]
excerpt: 一两句话摘要，会显示在列表页。
---

正文从这里开始，用 Markdown 写。
```

- 文件名里的日期决定排序，`date` 字段也填同一天。
- `categories`、`tags` 按需写，会自动归到 `/categories/`、`/tags/` 页面。
- 文章会自动出现在首页和「技术share」列表。

### 2. 发「科研学习」或「AI脑洞」文章（`_research/`、`_idea/`）

这两个是独立集合，路径分别生成到 `/research/文章名/`、`/idea/文章名/`。在对应目录下新建 `任意名.md`，开头：

```markdown
---
title: 文章标题
date: 2026-08-20
tags: [多模态, 调研]
excerpt: 一两句话摘要。
---

正文。
```

- 文件名建议用英文短横线命名（如 `2026-08-20-llm-survey.md`），避免空格和中文。
- 该栏目的列表页（`/research/`、`/idea/`）会自动收录。

### 3. 改「关于我」（`_pages/about.md`）

文件已分好章节：教育背景、工作/实习经历、项目/科研经历、专业能力、竞赛/荣誉、联系方式。在每个章节下把 `<!-- TODO ... -->` 注释替换成你的内容即可，用的是普通 Markdown 或 HTML。

- 顶部右侧照片用 `assets/images/photo.jpg`，换图就同名替换或改 `img` 标签的 `src`。
- 邮箱、电话等已填在联系方式区，按需更新。

## 站点配置（`_config.yml`）改了不生效？

`_config.yml` 是站点级配置，**不会**像文章那样热更新——GitHub 构建时会读取它，所以改完推送后**等一次构建完成**（约 1-2 分钟）才生效。常见可改项：

- `title` / `subtitle` / `description`：站点标题、副标题、SEO 描述
- `author`：姓名、头像、简介、所在地、社交链接（当前为 GitHub / 知乎 / 小红书）
- `footer.links`：页脚的社交链接
- `comments.giscus`：评论功能，需先在仓库启用 Discussions 并填 `repo_id` / `category_id`（当前为占位，不填则不显示评论）

## 提交流程

1. 改完文件，在项目根目录执行：
   ```bash
   git add -A
   git commit -m "简要描述改了什么"
   git push
   ```
2. 推送后 GitHub 自动构建。进 https://github.com/CodingZY/CodingZY.github.io/actions 看进度，绿勾即成功。
3. 访问 https://codingzy.github.io 查看结果（首次更新可能有几分钟缓存延迟，强刷即可）。

## 常见问题

- **新文章没出现在列表**：检查文件名日期是否是今天或过去，front matter 的 `title`/`date` 是否写全；文章日期设在未来默认不显示（除非 `_config.yml` 的 `future: true`，当前已开启）。
- **图片不显示**：确认图片放在 `assets/images/` 下，引用路径写 `/assets/images/文件名`（开头有斜杠）。
- **构建失败**：多半是 front matter 格式错（少了引号、缩进不对），去 Actions 页面看红色报错，按提示修。

## 本地预览（可选）

如果装了 Ruby，可本地预览再推送：

```bash
bundle install
bundle exec jekyll serve   # 浏览器打开 http://127.0.0.1:4000
```

没装 Ruby 也能直接推送让 GitHub 构建，不影响使用。
