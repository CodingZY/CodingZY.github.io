---
title: "GainRAG"
date: 2026-10-10
---

# GainRAG: Preference Alignment in Retrieval-Augmented Generation through Gain Signal Synthesis

**目录**

- [检索器内容偏好和 LLM 回答偏好不一致](#检索器内容偏好和-llm-回答偏好不一致)
- [困惑度与增益](#困惑度与增益)
- [伪文档策略](#伪文档策略)
- [增益分类器](#增益分类器)

---

## 检索器内容偏好和 LLM 回答偏好不一致

- 高相关文档不等于有用：即便检索出的文档包含了正确答案，LLM 依然有近 half 的概率生成错误答案（可能是由于复杂的干扰信息或逻辑冲突）。
- 不显式包含答案的文档反而有用：在 LLM 回答正确的样本中，大部分使用的文档并不直接包含答案，而是提供了暗示、背景或逻辑线索。

```text
                            [ 原始 Query q ]
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
          [ 外部检索器 R ]                    [ LLM 内部生成 ]
                  │                                   │
       检索 Top-k 真实文档 (c1..ck)           生成伪文档 c0 (Pseudo-Passage)
                  │                                   │
                  └─────────────────┬─────────────────┘
                                    ▼
                     候选文档集合 C = {c0, c1, ..., ck}
                                    │
                                    ▼
                ┌───────────────────────────────────────┐
                │ 偏好选择器 (Selector / BGE-Reranker)  │
                │ 预测各文档对 LLM 的 Gain 值: v_i       │
                └───────────────────────────────────────┘
                                    │
                                    ▼ 挑选 Gain 最大的 c*
                        [ 最佳文档 c* + Query q ]
                                    │
                                    ▼
                        [ LLM 最终生成 Answer a ]
```

**度量某个文档 c 到底给 LLM 解答问题 q 带来了多少真正的"增益"**

## 困惑度与增益

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791550291623-b987b8b9-8537-4e21-a1a1-421bfaa74d96.png" width="446" alt="困惑度与增益公式">

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791550656138-41c7212c-17ab-4a6c-a9f1-11f9f8ed3da7.png" width="448" alt="困惑度与增益公式">

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791550524740-1f1e292b-fcca-4f9c-ac01-707572364ea6.png" width="453" alt="困惑度与增益公式">

## 伪文档策略

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791550393649-7c7ce929-b037-4783-9954-c6eb67508c1d.png" width="451" alt="伪文档策略示意">

## 增益分类器

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791550561044-9498be1c-4380-4f6c-95f0-0658ac317d4c.png" width="455" alt="增益分类器示意">
