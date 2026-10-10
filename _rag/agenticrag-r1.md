---
title: "AGENTICRAG-R1: Agentic Reinforcement Learning with Stack Memory for Multi-Step Reasoning, Retrieval and Memorizing"
date: 2026-10-10
---

- [可逆 memory 适用场景：多步推理](#可逆-memory-适用场景多步推理)
- [格式奖励](#格式奖励)
- [通用奖励模型](#通用奖励模型)

---

## 可逆 memory 适用场景：多步推理

```text
                            [ 初始 Query ]
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 1. 结构化动作空间与栈内存 (Stack Memory)                             │
│                                                                        │
│   Push 动作:  <Plan>  <Think>  <Search>  <Conclusion>                  │
│   Pop  动作:  <Backtrack> (弹栈+修正)  <Summary> (弹栈+压缩)          │
│                                                                        │
│   Attention 机制: Pop-based Attention Masking (遮蔽已被 Pop 的历史 Token) │
└────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. 分层与动作感知的奖励函数 (Hierarchical & Action-Aware Reward)        │
│                                                                        │
│   最终结果奖励 r_out : EM / F1 评价 (仅作用于非 Mask 的 Token)          │
│   过程奖励 r_proc   : 格式正确性 (r_fmt) + 检索相关度 (r_rag)             │
│                       + 内存操作合理性 (r_mem)                          │
└────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. 信息感知轨迹拒绝策略 (Information-Aware Trajectories Rejection)    │
│                                                                        │
│   计算 Batch 内每个问题的 Reward 均值 μ 和方差 σ²                      │
│   UCB 打分: r_tilde = σ² * r + μ (优先保留高方差、高奖励的长链条轨迹)    │
└────────────────────────────────────────────────────────────────────────┘
```

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791549878062-fd8c13f1-7b4e-48d4-9564-a32ff22809ef.png" width="517" alt="AgenticRAG-R1 方法示意">

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791549920530-29c38a73-b588-4196-b573-8c7c41d80733.png" width="515" alt="AgenticRAG-R1 方法示意（续）">

## 格式奖励

没有标签闭合错误得分 1，else 0

## 通用奖励模型

判断检索到的是否有用，内存操作是否合理（prompt + 通用奖励模型判断）
