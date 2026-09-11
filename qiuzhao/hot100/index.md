---
layout: archive
title: "hot100"
permalink: /qiuzhao/hot100/
collection: hot100
description: "LeetCode Hot 100 刷题笔记与题解。"
date: 2026-09-07
---

<style>
  .hot100-list { list-style: none; margin: 1rem 0; padding: 0; }
  .hot100-list li {
    display: flex; flex-wrap: wrap; align-items: baseline; gap: .5rem;
    padding: .3rem .5rem; border-bottom: 1px solid #e0e0e0;
    font-size: 0.9rem; line-height: 1.4;
  }
  .hot100-list li:hover { background: #f5f5f5; }
  .hot100-list a.title { font-weight: 500; text-decoration: none; }
  .hot100-list a.title:hover { text-decoration: underline; }
  .hot100-list .date { color: #888; font-size: 0.8rem; }
  .hot100-list .tags { margin-left: auto; display: flex; gap: .3rem; flex-wrap: wrap; }
  .hot100-list .tag {
    font-size: 0.72rem; padding: 0 .4rem; border-radius: 3px;
    background: #eef1f6; color: #5a67d8; white-space: nowrap;
  }
</style>

{{ content }}

<ul class="hot100-list">
  {% assign posts = site.hot100 | sort: "date" | reverse %}
  {% for post in posts %}
  <li>
    <a class="title" href="{{ post.url | relative_url }}">{{ post.title }}</a>
    {% if post.date %}<span class="date">{{ post.date | date: "%Y-%m-%d" }}</span>{% endif %}
    <span class="tags">
      {% for tag in post.tags %}<span class="tag">{{ tag }}</span>{% endfor %}
    </span>
  </li>
  {% endfor %}
</ul>
