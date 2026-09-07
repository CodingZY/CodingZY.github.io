---
title: ZhangYing
description: ZhangYing 的个人简历。
permalink: /about/
---

> **保持好奇心，想和有趣的人一起做有挑战的事！**

<div style="display: flex; flex-wrap: wrap; gap: 2rem; align-items: flex-start; justify-content: space-between; margin: 1.5rem 0;">
  <div>
    <p><strong>电话 / 微信：</strong>13554005764</p>
    <p><strong>邮箱：</strong><a href="mailto:393354431@qq.com">393354431@qq.com</a></p>
    <p><strong>擅长领域：</strong>Agent、开放词汇目标检测（文本+视觉模态）</p>
  </div>
  <img src="/assets/images/photo.jpg" alt="ZhangYing" width="220" loading="lazy" decoding="async" style="border-radius:8px;">
</div>

## 教育背景

**武汉理工大学** ｜ 软件工程（硕士） <span style="float:right;">2024.09 – 2027.06</span>

- GPA **3.55/4**（前 20%）
- 荣誉成果：校一等奖学金；开放词汇增量目标检测论文已被 **CCF** 会议接收

## 专业能力

- **追踪 Agent 前沿论文**：上下文管理、Memory、RAG 知识库建设、Agent 评测（[CodingZY.github.io 学习笔记](https://codingzy.github.io/)）
- **掌握 Harness Engineering**：缓存机制、消息队列、Temporal 任务编排、Python 异步并发、安全防护机制、Skill 评测
- **多模态与工具开发**：具有多模态对齐 CV 基础，熟练使用 Claude Code 和 Skill 辅助 Spec 驱动开发

## 实习经历

### 金山集团 ｜ AI 应用开发工程师 <span style="float:right; font-weight:normal;">2026.06 – 2026.09</span>

**瀚海平台**（[Agentic_Paper_RAG GitHub 地址](https://github.com/CodingZY/Paper-Agentic-RAG)）

- **企业级开源 RAG 平台测评**：源码学习 RAGFlow、WeKnora、PageIndex、Dify、金山企业内部瀚海平台的实现思路，使用多元数据（海量游戏客服数据、复杂排版学术论文、金融 100 页以上超长 PDF）对各平台进行回答准确率、忠实度的量化评测。根据评测结果提出用 **MinerU** 升级自训练的 kmd 侧重工程流水线文档解析、WeKnora 面包屑导航代替 kmd 根据几何运算推理得到的 proto 结构化数据，针对企业内部游戏客服数据集特点采用 **wiki** 正则搜索和 chunk 语义补充的检索策略被采纳。
- **沉淀 Agentic_Paper_RAG 项目**：智能 RAG 论文研究助手，可本地导入批量语雀笔记、支持 Agentic 检索顶会 arXiv 论文补充。针对用户提出问题的类型，智能路由数据源（metadata｜chunk｜report｜graph），在海量文献中梳理脉络、对比总结、挖掘创新点。
  - 论文级 **ChunkMetadata** 支持快速过滤，chunk 级引入**面包屑标题**层级结构，丰富 chunk 语义层级结构并可关联相应图片，tokens 关键词辅助语义检索。
  - 设计相似**论文连边**，利用**知识图谱**推理增强：论文摘要计算相似度 paper_cos，结合 AxB 论文摘要实体对相似度取最高的 top3 均值 entity_cos 加权求和，超过阈值则连边；基于 keywords 和 entities 语义向量化多路检索并重排 RRF，将知识图谱命中的一跳相连论文的 paper_analysis_reports 送入 LLM 用于对比/归纳总结。

**智能化运营平台 X-Scraper**

- **项目背景**：监控 X 平台上关注的大 V 发帖，根据主号游戏素材库，用 **claude_agent_sdk** 消费 + AdsPower 模拟矩阵号在大 V 帖底下根据主号素材库进行自动个性化回复，增加自己游戏曝光度。心跳监控消费端 Agent 运行状态，接入企业协作平台进行异常播报。
- 设计大 V 账号**抓取间隔分级算法**：结合发帖活跃度、转化潜力、影响力加权，添加错峰保护防止同一级账号同时访问抓取 API 限流；优化原有异步管线，将抓取到发布的时效从 2h 优化到 30min。
- 智能化**矩阵号人设配置**：支持用户输入运营目标，LLM 一键进行角色规划和组间差异性检查；为使矩阵号发帖更加拟人化，构造矩阵号游戏人设知识库，并根据运营反馈结果将优秀回复内容沉淀为人设的 Long-Term Memory 记忆库复用。

## 项目 / 科研经历

### AI_Cowork_Game（[GitHub 地址](https://github.com/CodingZY/AI_Cowork_Game)）

- **项目背景**：基于 **Claude Code CLI 和自定义 Game Skills** 打通自动化生成中型网页游戏最后一公里——将用户一句简单的想法，落地成游戏整体设计文档 **GDD**、进行美术资产生成、编码和自动化测试，并支持用户试玩反馈修改、使用 **git tag** 版本管理、**langfuse** 对各阶段成功率、耗时、token 用量进行监控，用于优化现有流程和 skill。
  - 引入**持久化状态机流程编排 Temporal**，适配暂停等人、重启回滚、并行编排、长流程超时｜重试｜取消精细化管理，把头脑风暴 skill 得到 GDD 的过程变成可暂停、可恢复、可人工干预的流程。
  - 针对美术素材风格难统一、数量过多、质量不高的问题，采用「全局风格约束 → 美术资产清单 → 正负 prompt 文生图 → 校验」流程保证素材正确性，结合 Canvas API 弥补本地模型对控件 UI 生成效果差的问题。AutoDL 部署对比开源文生图模型 SDXL1.0｜SD3.5 Large｜Flux.1 Dev｜Hunyuan-DiT｜Kolors，选用中文支持性更好的 **Hunyuan-DiT + rembg** 实现生图抠图 pipeline。
  - 为解决 **spawn agent** 上下文窗口爆掉和代码一致性问题，采用顶层 Planner 将 spec 拆分 MVP 版本、设计 Shared API、给出子 coder spawn 编码交付约束 Contract，将串行编码优化为基于依赖关系的 Wave 间串行、Wave 内并行；重复性高的试玩反馈记录进 memory.md 作为知识沉淀自进化开发，完成的游戏支持自动上传到 GitHub 游戏仓库管理。

### RAD-DETR: Efficient Few-Shot Retrieval Augmented Adaptation OVD <span style="float:right; font-weight:normal;">2026.08</span>

- **论文发表（CCF）**：针对增量开放词汇目标检测场景，提出高效少样本检索增强适配框架，已被环太平洋人工智能国际学术会议 **PRICAI 2026** 接收。
  - 将闭集目标检测转化为开放词汇目标检测，用户可不受类别数量限制地输入 text prompt 进行检测。为适应持续学习下检测类别的不断扩增，同时避免对已学习类别发生灾难性遗忘，将 LLMs 的 RAG 范式引入开放词汇增量目标检测：框架采用具备解耦模态交互的预训练视觉-语言模型，结合语言引导参数高效自适应模块（LGPEA）与原型引导动态检索机制（PGDR），将一部分专家权重保存为外部知识、推理阶段动态调取，以此适配新增任务。RAD-DETR 实现无需原始数据的持续自适应，缓解新旧类别之间的语义冲突。实验表明，小样本条件下 RAD-DETR 在 ODinW 数据集上已见类别 mAP 达到 **55.7%（提升 4.2%）**，在 COCO 数据集上达到 **51.8%（提升 1.2%）**。
