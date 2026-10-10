---
title: "ArcAligner: Adaptive Recursive Aligner for Compressed Context Embeddings in RAG"
date: 2026-10-10
---

> Embeddings in RAG

- [为什么要用 embedding，不用标准的基于检索的 RAG 进行回答？](#为什么要用-embedding不用标准的基于检索的-rag-进行回答)
- [训练过程](#训练过程)

---

## 为什么要用 embedding，不用标准的基于检索的 RAG 进行回答？

1. 长文档文本包含大量的非核心信息。直接拼接几千上万 Token 的原始文本，不仅会迅速挤爆 LLM 的上下文窗口，还会导致首字延迟（TTFT）极高、API 计算成本暴增。

   Embedding 可以实现高达 **24× 到 72× 的超高压缩率**。原本需要 1000 个文字 Token 表达的信息，压缩后仅需几十个向量槽位（Slots）即可承载，极大节省了计算开销与推理耗时。

2. 避免"硬截断/丢词"造成的信息丢失

   **Embedding 软压缩**：在连续的高维向量空间中对整段文本的语义进行分布式编码。它将细节隐藏在隐层维度中，**保留了全局上下文语义，避免了直接删词造成的断章取义**。

3. 在面对复杂的多跳（Multi-Hop）问答时，答案依赖于分布在不同文档中的多处线索。若直接把分散的文本全丢给 LLM，大模型容易受到"迷失在中间"或注意力分散现象的干扰。

   **Embedding + 递归对齐**：ArcAligner 这类方案把片段转化为 Embedding 槽位后，利用**深层 LoRA 和门控递归循环**，让 LLM 可以在极短的向量槽位上跨层反复"交叉注意力"与融合。模型能**在隐空间内部自动关联并提炼多处证据，显著提升了多跳推理与长尾 QA 的准确率**。

---

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791453148363-4a4d6701-2c79-4cf0-ad7f-82928e4a4b5d.png" width="414" alt="ArcAligner 架构示意">

**embedding 和 LLM 的深度对齐**：除了 projector，还有 LLM 中的 LoRA

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791453210392-83c3ec52-bf1f-4860-8a0d-95c78be8efa3.png" width="1668" alt="embedding 与 LLM 深度对齐示意">

## 训练过程

1. 只训练了 doc embedding
2. 门控自适应递归：计算继续精炼的概率
3. embedding 和 LLM 对齐预训练：大规模 Wikipedia 语料库，输入压缩向量槽位，要求 LLM 自回归重构并输出原始文本内容
4. 基于 RAG 微调：引入 RAG HotpotQA 问答数据，关闭 Gate 机制（每个槽位仅进行默认 1 次单步精炼），按标准的生成 Loss 训练
5. 感知门控的自适应微调：解锁门控参数，让模型自动学会根据问题复杂度为不同的记忆槽位分配不同深度的循环计算量

4 张 NVIDIA H20-3e GPU
