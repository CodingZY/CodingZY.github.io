---
title: "OptiSet"
date: 2026-10-10
---

# OptiSet: Unified Optimizing Set Selection and Ranking for Retrieval-Augmented Generation

**目录**

- [在跨多文档回答时，基于语义相似度的 topK 不适合](#在跨多文档回答时基于语义相似度的-topk-不适合)
- [无文档基线（H_0）与分段映射公式的作用](#无文档基线h_0与分段映射公式的作用)
- [对比 DPO 等强化学习/偏好对齐方法](#对比-dpo-等强化学习偏好对齐方法)

---

## 在跨多文档回答时，基于语义相似度的 topK 不适合

1. 忽略文档间内容的互补性
2. 容易选入高度重复信息

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791453885216-f4ee7cfd-e76e-4593-82f6-479896dcf223.png" width="356" alt="chunk 集合选择示意">

→ 单个 chunk 变成多个 chunk set

Query 分解为多个子问题，挑选可以回答子问题的文档 `Sraw`，用原始 query 过滤 `Sraw` 得到 `Srefined`

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791454179850-8f0c850c-4df0-40e2-ac35-ff6831a14119.png" width="379" alt="文档集合过滤示意">

**把“生成质量”转化为“可量化的数学得分”。如果喂给生成器文档集合 S 后，生成器预测正确答案 a 的熵 H 越低，说明这组文档 S 越有价值，它帮助生成器更自信、更准确地输出了正确答案。**

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791454201077-3eb4a4c3-5c58-4597-bd6f-13d4bb150c54.png" width="513" alt="质量得分公式示意">

## 无文档基线（H_0）与分段映射公式的作用

（1）$H_0$ 是指不提供任何参考文档（即仅给问题 $q$），生成器直接输出答案 $a$ 时的熵；而 $H_p$（即 $H$）是提供了文档集合 $S$ 后的熵。

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791454315212-c83f2cce-70e2-4076-bf1b-eac261f24eb5.png" width="541" alt="分段映射公式">

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791454377385-0ce34622-0852-4a0d-973a-ad26d3695025.png?x-oss-process=image%2Fcrop%2Cx_0%2Cy_0%2Cw_1811%2Ch_1918" width="530" alt="分段映射示意">

$\mathcal{L}_{all} = \mathcal{L}_{CE} + \lambda \mathcal{L}_{KL}$

通过这种联合训练，Selector 既学会了精准生成最高质量的文档集合（$\mathcal{L}_{CE}$ 的功劳），又学会了对不同文档组合的高阶辨别能力与鲁棒性（$\mathcal{L}_{KL}$ 的功劳）。

## 对比 DPO 等强化学习/偏好对齐方法

直接使用基于 KL 散度的 Set-List Wise 损失，比标准的 DPO 训练更稳定，收敛更快且效果更好。解释原因

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791454489955-834edc7a-4160-4579-801c-e5ab4a64ba50.png" width="559" alt="DPO 对比实验">

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791454519190-595a4f7b-3b05-4829-92eb-9b1aca1dc8db.png" width="559" alt="DPO 对比实验（续）">
