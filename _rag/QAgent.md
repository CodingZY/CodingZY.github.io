---
title: "QAgent: A modular Search Agent with Interactive Query Understanding"
date: 2026-10-10
---

- [RAG 路线图](#rag-路线图)
- [轨迹间利用结果奖励计算 GRPO](#轨迹间利用结果奖励计算-grpo)
- [增强检索正确率](#增强检索正确率)

---

## RAG 路线图

> **传统 RAG**
>
> - 优化查询、意图识别
> - rerank
> - 插入可训练的中间件
>
> **Agentic RAG**
>
> - Self-RAG：Reflection Tokens 是否需要检索、检索是否和 query 相关（相关性）、回答时候得到检索的支持（忠实性）、回答是否对 query 有用（有用性）
> - MetaRAG：基于 Prompt + Agent
> - Search-o1：深度推理 CoT
>
> **基于强化学习的 Search Agent**
>
> - **Search-R1：依赖结果正确的奖励**。倾向于去优化自身的"生成和知识利用能力"来凑出正确答案，导致模型的检索质量并未持续提升。
> - R1-Searcher：引导模型学会如何用最少的搜索轮次获取有效信息。
> - Deeprearcher：赋予点击网页的能力
> - ZeroSearch：另一个大模型模拟网页答案

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791548744951-7af2cd39-811a-4246-8ba2-2cfa3c0a0a9f.png" width="534" alt="QAgent 框架示意">

作用：将传统单次强行改写 Query 的做法，严格数学化地抽象为一个多步随机顺序决策过程。

QAgent 并不需要硬性写死树状展开或固定的拆解规则，模型可以根据过去的检索反馈（`C <t`和 `I <tpost`），在概率上动态决定"下一步是深化（Serial）、平行扩展（Parallel）还是重写（Rewrite）"。

## 轨迹间利用结果奖励计算 GRPO

$\mathcal{J}(\theta) = \mathbb{E}_{x \sim \mathcal{D}, \{y_i\}}\left[ \frac{1}{\sum \vert{}y_i\vert{}} \sum_{i=1}^G \sum_{t=1}^{\vert{}y_i\vert{}} \min\left( \rho_{i,t} A_i, \text{clip}(\rho_{i,t}, 1-\epsilon, 1+\epsilon) A_i \right) - \beta \mathbb{D}_{KL}(\pi_\theta \vert{}\vert{} \pi_{ref}) \right]$

**是怎么用于损失函数的计算的？**

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791549040714-f03ddc42-5d01-4a26-b730-64bb934526c8.png" width="516" alt="GRPO 目标函数示意">

采样 G 个独立的 Rollout 轨迹：同一个 prompt 温度设为 1（概率随机采样）

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791549445882-05dca3f1-27f1-4b76-be51-5778992636ac.png" width="522" alt="Rollout 轨迹采样示意">

$A_i > 0$：说明这个动作比平均水平好（应该奖励/增加该动作概率）。

$A_i < 0$：说明这个动作比平均水平差（应该惩罚/降低该动作概率）。

## 增强检索正确率

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791548889710-1a80ce91-2df5-4000-b1ec-c1132d473e26.png?x-oss-process=image%2Fcrop%2Cx_0%2Cy_0%2Cw_1819%2Ch_1445" width="514" alt="增强检索正确率示意">
