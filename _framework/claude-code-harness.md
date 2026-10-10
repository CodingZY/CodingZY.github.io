---
title: "Claude Code Harness"
date: 2026-10-10
tags: [Harness Agent, 前沿Harness框架学习]
---

**目录**

- [安全与权限](#安全与权限)
- [可扩展性](#可扩展性)
- [上下文与记忆](#上下文与记忆)
  - [5 层渐进式压缩](#5-层渐进式压缩)
    - [如何保护 prompt cache？](#如何保护-prompt-cache)
  - [会话历史](#会话历史)
    - [mark 为什么要写道 seession transcript 中？](#mark-为什么要写道-seession-transcript-中)
  - [记忆](#记忆)
- [子智能体委托](#子智能体委托)
- [Agent 设计空间的新信号](#agent-设计空间的新信号)
  - [介绍 Graph Engineering](#介绍-graph-engineering)
    - [为什么有了 harness 还要 Graph Engineering，两者的关系和区别？](#为什么有了-harness-还要-graph-engineering两者的关系和区别)
    - [Graph Engineering 是什么，综述介绍](#graph-engineering-是什么综述介绍)
- [跨系统对比：Claude Code vs OpenClaw vs Hermes-Agent](#跨系统对比claude-code-vs-openclaw-vs-hermes-agent)

---

## 安全与权限

- 7 种权限类型
- 过滤 → `PreToolUse` → 有一个 deny 就拒绝 → 权限判断模型：小模型做权限分类器、交互式让用户判断

## 可扩展性

插件是 tool skill 的组合

## 上下文与记忆

### 5 层渐进式压缩

1. 【每轮触发】单个 `tool_result` 超过 50K 字符，将完整结果持久化到磁盘，然后将文件路径写入上下文 + 2K 预览
   - 超 token 截断上下文，保留最近的消息 + 插入截断标记
   - 早期工具结果替换成 `[used{tool_name}]`
2. 【90% 上下文触发】上下文折叠：非破坏性的，底层消息不被修改，查询时返回压缩的视图消息
3. 【最后触发】自动压缩：破坏性的

#### 如何保护 prompt cache？

本地历史不变 + 服务端加入逻辑删除：

原始上下文不动，在请求最后加入 `cache_edits` 块 → 前缀 hash 仍然匹配，已有的 Prompt Cache 可以继续命中

```json
{
  "type": "cache_edits",
  "edits": [
    { "type": "delete", "cache_reference": "toolu_xxx" },
    { "type": "delete", "cache_reference": "toolu_yyy" }
  ]
}
```

### 会话历史

| 通道 | 存储形式 | 作用 |
| --- | --- | --- |
| **仅追加的 JSONL 转录稿** | `Session Transcript`（`.jsonl`） | 主会话的完整、不可变事件流。所有用户消息、助手回复、工具调用与结果都按时间顺序追加。 |
| **全局提示历史** | 与会话相关的 prompt / 系统级历史 | 跨轮次复用的稳定前缀（system prompt、CLAUDE.md、工具定义等），服务于 Prompt Cache。 |
| **子智能体侧链（Sidechain）** | 独立的子智能体日志 | 每个子智能体有自己的对话记录，不直接污染主转录稿，只通过最终摘要回传。 |

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1790221580236-21a587c7-f5d3-4ac3-b774-218b6477d52b.png" width="535" alt="会话历史存储示意">

#### mark 为什么要写道 seession transcript 中？

- 磁盘上形成：完整历史₁ → boundary₁ → 摘要₁ → 完整历史₂ → boundary₂ → 摘要₂ → ...
- 加载时只需要找到最新的 boundary，就能正确重建当前上下文。
- 旧的 boundary 和原始消息仍然存在，方便调试、审计、回放或从更早的点 fork。

### 记忆

- 不使用 RAG，分目录、主题 `.md` 记忆文件让 LLM 读取目录选择
- 索引读取 → 读取文件前 30 行描述 → 选择 top 5

## 子智能体委托

SubAgent 构造（项目级 / 用户级）：`subagent_type`、`name`、**任务描述**、`isolation`（worktree）、`model`、`tools`

子智能体三种隔离程度：

- **与主智能体共享工作目录**
  - 全新空上下文 + 自己的 system prompt
  - 继承父对话
- **独立工作目录**
  - 独立 git worktree

## Agent 设计空间的新信号

### 介绍 Graph Engineering

#### 为什么有了 harness 还要 Graph Engineering，两者的关系和区别？

| 维度 | Harness Engineering | Graph Engineering |
| --- | --- | --- |
| **关注点** | 单个 Agent 的运行环境 | 多个节点之间的工作流拓扑 |
| **解决的问题** | 模型如何安全、可靠地行动 | 工作如何被分解、路由、并行、汇合、恢复 |
| **核心对象** | 工具、权限、记忆、上下文压缩、Hooks、沙箱、可观测性 | 节点（Nodes）、边（Edges）、共享状态（Shared State） |
| **典型问题** | “这个 Agent 能不能安全读文件、跑命令、记住上下文？” | “任务该如何拆分？谁先谁后？失败走哪条边？如何并行？” |
| **类比** | 给司机一辆好车（方向盘、刹车、仪表盘、油箱） | 设计整条公路网与交通规则（路口、分流、汇合、信号灯） |

Harness 解决的是「**一个 Agent 如何可靠地干活**」。

当任务复杂到需要：

- 多个专业化角色协作（探索者、实现者、审查者、验证者）
- 明确的分支、并行、汇合、重试、人工检查点
- 可控的状态传递与失败恢复路径

单靠一个 Agent 的内部循环已经不够。这时必须把**控制流显式化**，这就是 Graph Engineering 的职责。

- Harness 是 Graph 中每个节点的「运行时底座」。
- 一个 Graph 的每个节点，本身可以是一个完整的「模型 + Harness + Loop」。

#### Graph Engineering 是什么，综述介绍

Graph Engineering 是通过构建显式、动态、可演化的图结构，来组织任务、协调异构 Agent、管理执行状态的工程范式。它把系统从「单个 Agent 的智能」提升到「系统级智能」。

- **节点（Nodes）**：一个可执行单元。可以是确定性代码、单次 LLM 调用、完整 Agent（带自己的 Harness 和 Loop）、甚至人工检查点。
- **边（Edges）**：路由规则。包括顺序、条件分支、并行 fan-out、汇合 fan-in、失败回边、循环等。
- **共享状态（Shared State）**：沿边流动的数据（任务描述、中间产物、验证结果、决策记录等）。

##### 两种主流实现路径

1. **Code-as-Graph**（代码即图）
   用代码（LangGraph、Claude Code Dynamic Workflows、自定义 DAG 运行时）显式声明节点与边。控制流由运行时确定性执行。
2. **LLM-as-Graph**（模型读图）
   把 SOP / 流程图 / 结构化步骤写成 Skill 或 Markdown，让模型自己阅读并遵循。Harness 提供确定性部分（权限、验证、工具），模型负责路由决策。

在 Claude Code 生态中，两者都已出现：

- 子智能体 + 主 Agent 委托 ≈ 隐式图
- 自定义 Skill + Agent Teams + Task 系统 ≈ 更显式的图
- 社区插件（如 graph-engineering、Graph Skill）则把 DAG 执行做成一等公民

##### 典型模式

- **Orchestrator-Worker**：主节点规划，派生多个并行 Worker，再汇合。
- **Pipeline**：严格顺序阶段（分析 → 实现 → 测试 → 审查）。
- **Fan-out / Fan-in**：并行探索后汇总。
- **Verifier / Critic 回路**：实现节点后接独立验证节点，失败走回边。
- **Human-in-the-loop**：把 user_input 或 checkpoint 作为显式节点。

## 跨系统对比：Claude Code vs OpenClaw vs Hermes-Agent
