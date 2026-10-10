---
title: "GraphRAG"
date: 2026-10-10
---

**目录**

- [GraphRAG](#graphrag)
- [RAG vs. GraphRAG](#rag-vs-graphrag)
  - [更新](#更新)

---

## GraphRAG

**GraphRAG：在查询时进行提示增强**

GraphRAG 方法在查询中发现了一个实体 Novorossiya。这使得 LLM 能够扎根于图表，并通过链接到原始支持文本获得更优的答案。

数据中前五大**主题**是什么？

LLM 创建源数据中所有实体和关系的引用，生成的知识图谱。

该图随后用于创建自下而上的**聚类**，将数据按语义簇层次组织（使用颜色表示）。这种划分允许对语义概念和主题进行预总结，有助于整体理解数据集。

在查询时，这两个结构都用于为回答问题时的 LLM 上下文窗口提供材料。

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1786545656440-b85536d8-e9fc-4e80-a158-f3e9d8561c30.png" width="1920" alt="GraphRAG 流程示意">

- chunk（256 tokens）提取实和关系：结构上的 & 事件上的
- 合并同实体的信息为知识
- 分层划分社区覆盖所有节点，无递归之社区可划分，高层社区知识可借助底层知识总结
- query 去图中某个层级的 community summaries 去 map answers 打分排序成 global answer 返回给 user
- 评估：因为没有 GT，采用 LLM 作为 Judge，全面性、多样性、是否对问题有帮助三方面进行评估

## RAG vs. GraphRAG

**RAG 和 GraphRAG 擅长的领域区别，以及不同的 GraphRAG、在不同类型的数据集上表现差异的原因**

| 方案 | 离线构建耗时排序（由慢到快） | 在线检索延迟排序（由高到低） | 底层核心原因 |
| --- | --- | --- | --- |
| KG-Graph | 1（最慢） | 1（最高） | 全量细粒度三元组抽取 + 多跳遍历爆炸 |
| Community-Graph | 2 | 4（最低） | 抽取但社区聚合压缩，Global 检索免遍历 |
| HippoRAG | 3 | 3 | 仅实体 - chunk 二分图，无复杂关系抽取 |
| RAPTOR | 4（最快 GraphRAG） | 2 | 完全跳过实体关系抽取，仅文本聚类 |

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1786545656377-8549108a-a97b-4e2c-a3ca-10902060945b.png" width="535" alt="各方案对比结果">

- KG-Graph：纯 3 元组、无社区，Null 表现最好（因为信息丢失最严重）
- Community-Graph：Comprison Temporal 时序表现最好
- HippoRAG：均衡
- RAPTOR：树形分层索引，推理能力有限
- RAG 在纯细节、单跳任务由于 GraphRAG（因为 LLM 抽取实体无法 100 覆盖原文关键实体 65%）

### 更新

- 纯 KG-Graph：仅更新节点、边，无社区；
- Community Graph（微软原版）：局部社区追加，全局社区可选定时全量重算；
- HippoRAG：更新实体 - chunk 二分关联图；
- RAPTOR：树形摘要局部更新，不涉及实体
