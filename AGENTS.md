# Repository Guidelines

Contributor guide for a personal website built with [Jekyll](https://jekyllrb.com/) and the [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) theme, deployed via GitHub Pages. The repository is a clean framework scaffold with placeholder content.

## Project Structure & Module Organization

- `_pages/` — standalone pages (`about.md`, `categories.md`, `tags.md`, `404.md`) with a `permalink` front-matter field
- `_shousi/` — Jekyll collection for "Harness Agent → 手撕Agent" (`/harness-agent/shousi/`)
- `_framework/` — Jekyll collection for "Harness Agent → 前沿Harness框架学习" (`/harness-agent/framework/`)
- `_rag/` — Jekyll collection for "论文阅读 → RAG" (`/papers/rag/`)
- `_memory/` — Jekyll collection for "论文阅读 → Memory" (`/papers/memory/`)
- `_hot100/` — Jekyll collection for "秋招 → hot100" (`/qiuzhao/hot100/`)
- `_agent/` — Jekyll collection for "秋招 → Agent八股" (`/qiuzhao/agent/`)
- `_high-concurrency/` — Jekyll collection for "秋招 → 高并发 AI 工程链路建设" (`/qiuzhao/high-concurrency/`)
- `harness-agent/`, `papers/`, `qiuzhao/` — section landing pages (one `index.md` per section / subsection)
- `_data/` — site data (`navigation.yml`, `authors.yml`, `ui-text.yml`)
- `_config.yml` — site metadata, navigation, and comment settings
- `_includes/`, `_layouts/`, `_sass/` — theme components and styles
- `assets/` — images, CSS, and JS
- `_scripts/` — build helper scripts (math entity fixing, inline-math protection)
- `_site/` — generated build output (gitignored)

Note: site search has been removed (`search.json`, `assets/js/search.js`, `_pages/search.md` deleted; `_config.yml` search settings cleared). Re-enable via Minimal Mistakes docs if needed.

## Build, Test, and Development Commands

Uses Ruby + Bundler with the `github-pages` gem for parity with GitHub Pages.

```bash
bundle install            # install dependencies (Gemfile)
bundle exec jekyll serve  # local preview at http://127.0.0.1:4000
bundle exec jekyll build  # generate the site into _site/
```

There is no test suite. Verify new content locally with `bundle exec jekyll serve`.

## Coding Style & Naming Conventions

- Content uses YAML front matter: `title`, `date`, and `tags` for collection docs; `permalink` for pages
- Collection docs use lowercase hyphenated slugs (e.g. `what-is-agent.md`); the `date` field drives list ordering (newest first)
- Keep `_config.yml` settings commented; restart the server after editing it
- No linters are configured; use 2-space indentation for YAML and follow existing Markdown style

## Testing Guidelines

Automated tests are not used. Validate changes by:

1. Running `bundle exec jekyll build` and confirming it exits cleanly
2. Serving locally and checking the affected pages and links

## Commit & Pull Request Guidelines

- Commit messages are short and imperative; match the language of the change
- Create a descriptive branch off `master` before opening a PR
- Fill out `.github/PULL_REQUEST_TEMPLATE.md`; note whether the change is a bug fix, feature, or content addition
- Reference related issues and include screenshots for visual changes
- Push to `master`; GitHub Pages builds and deploys automatically

## Security & Configuration Tips

- Never commit real API keys or tokens
- Giscus comments (`_config.yml` → `comments.giscus`) need a `repo_id` and `category_id` from [giscus.app](https://giscus.app); keep the `YOUR_GISCUS_*` placeholders until configured
- Search for `TODO` and placeholder values (`YOUR_NAME`, `your-email@example.com`, `your-username`, `YOUR_SITE_TITLE`) and replace them before going live
- Social links are limited to GitHub / zhihu / xiaohongshu; replace the `TODO` URLs in `author.links` and `footer.links`
- Preserve `.gitignore` entries for `_site/`, `.jekyll-cache`, and `Gemfile.lock`
