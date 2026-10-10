---
title: "Harness Engineering"
date: 2026-10-10
tags: [系统过Harness Agent基础]
---

**目录**

- [Harness 层级结构](#harness-层级结构)
  - [层间通信](#层间通信)
  - [Agent 循环](#agent-循环)
  - [消息](#消息)
- [展望](#展望)
- [工具执行流水线](#工具执行流水线)
- [缓存](#缓存)
- [任务图](#任务图)
- [状态机](#状态机)
- [双向通信模式](#双向通信模式)
- [提示词缓存](#提示词缓存)
- [流式处理](#流式处理)
- [状态管理](#状态管理)
- [消息管理](#消息管理)
- [长时任务的漂移检测与纠正](#长时任务的漂移检测与纠正)
- [插件扩展](#插件扩展)
- [可观测体系](#可观测体系)
- [人类在环](#人类在环)
- [容错+恢复](#容错恢复)
- [幻觉防护](#幻觉防护)

---

## Harness 层级结构

- **接入层**
  - CLI / Web API / SDK
- **编排层**
  - 编排引擎：依赖管理
- **智能体核心层**
  - 运行时引擎：状态机管理
  - 工具层
  - 记忆层
  - 模型集成与输出治理：模型选择、输出验证、降级策略
- **安全层**：权限管理、沙箱
- **观测层**：日志、追踪、指标

### 层间通信

- 上调用下：接口
- 下上报上：回调函数（`[ExecutionEvent]`）

### Agent 循环

- **感知**：上下文加载（系统提示 + 用户消息 + 记忆 + 工具）
- **推理**
- **决策**：工具是否存在、参数格式、参数值是否正确
- **执行**
- **学习**：本轮循环的记录写入记忆系统。短期记忆总是写入，如果这一步具有较高的学习价值，还会写入长期记忆
- **判断**：是否下一轮循环

- `initialize(agent, task)` — 初始化执行环境
- `step()` — 单步循环
- `run(task, max_step, timeout)` — 内部反复调用 `step()` 完成 task
- `pause()` / `resume()` — 支持长任务的中断和继续
- `get_state()`

`step()` 和 `run()` 的分离是一个重要的设计决策。**`step()` 暴露了单步粒度的控制，使得外部系统可以在每一步之间插入检查点、审批流程或日志记录；`run()` 则提供了更简洁的“一键执行”接口**，适用于不需要细粒度控制的场景。

### 消息

- 消息（Base 类）
- 事件：发布订阅，用于系统内通信
- EventBus 中：订阅 = 设置事件监听器 = 事件类型 + 事件回调函数；发布事件 = 通知对事件感兴趣的订阅者

## 展望

**Agent-as-OS**

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1789984964244-5c8fcfb7-005b-482f-94c2-86615b785698.png" width="417" alt="Agent-as-OS 示意图">

## 工具执行流水线

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1789981693131-0f0dd8ed-3055-423b-b07c-3292e13d4974.png" width="710" alt="工具执行流水线">

```python
# 工具发现
# 权限检查
# 输入验证
# 工具执行
# 结果处理: 序列化 + 截断
# 本地缓存与记录

# 并发工具执行
class StreamingToolExecutor:
    def __init__(self, pipeline: ExecutionPipeline, max_concurrent_tools: int = 5):
        self.pipeline = pipeline
        self.max_concurrent_tools = max_concurrent_tools

    async def execute_tools(self, tool_uses: List[ToolUseBlock], content: Any):
        """
        并发执行多个工具

        Args:
            tool_uses: 工具调用列表
            context: 执行上下文

        Returns:
            {tool_use_id: tool_result_block}
        """
        semaphore = asyncio.Semaphore(self.max_concurrent_tools)

        async def execute_with_semaphore(tool_use: ToolUseBlock):
            async with semaphore:
                result = await self.pipeline(tool_use, content)

        results = await asyncio.gather(
            *[execute_with_semaphore(tool_use) for tool_use in tool_uses]
        )

        # 组织结果
        for tool_use, result in zip(tool_uses, results):
            result_dict[tool_use.id] = result
```

## 缓存

避免每次工具调用都走一遍 schema 序列化

## 任务图

DAG 有向无环的依赖关系图：

1. dfs（visited + 正在运行的任务）判断是否存在循环依赖
2. 入度为 0 表示当前任务可执行，分为一组并行执行

```python
class TaskDefinition:
    task_id:
    task_type:
    description:
    dependencies:
    timeout_seconds:
    max_retries:
    execution_config:

    def add_dependency(self, dependency_task_id):
        # 添加任务依赖
        if dependency_task_id not in self.dependencies:
            self.dependencies.append(dependency_task_id)


class TaskDAG:
    # 任务依赖图
    def __init__(self):
        self.tasks = {}
        self.execution_order = []

    def add_task(self, task: TaskDefinition):
        self.tasks[task.task_id] = task
        self.execution_order.append(task.task_id)

    def validate_dag(self):
        # 检查所有依赖存在
        for task_id, task in self.tasks.items():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    raise ValueError(f"任务{task_id}依赖的任务{dep_id}不存在")

        # 检查是否存在循环依赖
        if self._has_cycles():
            raise ValueError("任务依赖图中存在循环依赖")

        return True

    def _has_cycle(self) -> bool:
        visited = set()     # 记录所有处理过的节点，避免重复搜索
        rec_stack = set()   # 记录“当前递归路径/栈”上的节点

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)  # 1. 标记当前节点入栈

            for neighbor in self.tasks[node].dependencies:
                if neighbor not in visited:
                    if dfs(neighbor):  # 2. 递归向下搜寻
                        return True
                elif neighbor in rec_stack:  # 3. 关键：邻居在递归栈中 -> 找到环！
                    return True

            rec_stack.remove(node)  # 4. 回溯：当前节点的所有依赖处理完毕，出栈
            return False

        for task_id in self.tasks:
            if task_id not in visited:
                if dfs(task_id):
                    return True
        return False

    def topological_sort(self) -> List[str]:
        """拓扑排序,生成执行顺序"""
        self.validate()

        # 入度表
        in_degree = {task_id: 0 for task_id in self.tasks}
        for task in self.tasks.values():
            for dep_id in task.dependencies:
                in_degree[task.task_id] += 1

        # Kahn算法
        queue = [task_id for task_id in self.tasks if in_degree[task_id] == 0]
        order = []

        while queue:
            node = queue.pop(0)
            order.append(node)

            # 找到依赖于这个节点的所有任务
            for task_id, task in self.tasks.items():
                if node in task.dependencies:
                    in_degree[task_id] -= 1
                    if in_degree[task_id] == 0:
                        queue.append(task_id)

        self.execution_order = order
        return order

    def get_parallelizable_groups(self) -> List[List[str]]:
        """获取可并行执行的任务组"""
        self.topological_sort()  # 确保 DAG 合法
        groups = []
        completed = set()                       # 已分发/已完成的任务集合
        remaining = set(self.execution_order)  # 待分配的任务集合

        while remaining:
            # 筛选“就绪”任务：依赖项必须完全包含在 completed 中
            ready = [
                task_id for task_id in self.execution_order
                if task_id in remaining
                and all(dep in completed for dep in self.tasks[task_id].dependencies)
            ]

            if not ready:
                raise ValueError("无法继续分组:存在循环依赖或缺失依赖")

            groups.append(ready)               # 构成当前批次（并行组）
            completed.update(ready)            # 标记这批任务已就绪/可完成
            remaining.difference_update(ready)  # 从待分配中剔除

        return groups
```

## 状态机

1. **有限状态机**：
   - claude code：python 定义状态和转移
   - openclaw：yaml 声明式的工作流
2. state 拥有多个 action

## 双向通信模式

基于 JSON 的 RPC：

1. 双向的，走 socket 全双工 → 服务器和客户端都可以发送请求
2. 格式高度规范 + 不依赖无意义的 HTTP Header 投信息 → 保证序列化出来的文本具有强确定性 + 提升了 Prompt Caching 的命中率

## 提示词缓存

向后追加不破坏 KV，因为 LLM 使用的是 Causal Self-Attention，Token 计算 KV 矩阵时只看到自己和前面的 Token

负责连接新旧 Token，是 Query 的工作：

新 Token E 会生成自己的 $Q_E$。模型拿 $Q_E$ 去和已经拼接完整的全量 K 矩阵 $[K_A, K_B, K_C, K_D, K_E]$ 做点积乘法！

## 流式处理

```python
# 初始化状态
# 构建上下文
# 检查 token 预算
# 流式调用模型
# 接收流式返回

assembler = MessageAssembler()
# 增量积累内容块，直到消息终止
async for event in stream:
    if event.type == "content_block_start":
        assembler.start_block()
    elif event.type == "content_block_delta":
        assembler.append_block_delta()
    elif event.type == "content_block_end":
        assembler.end_block()
    elif event.type == "message_delta":
        assembler.append_message_delta()
    elif event.type == "message_end":
        message = assembler.build_message()

        # 异步执行工具
        tool_results = await execute_tools(message.content, app_state)

        # 更新状态
        app_state.add_message(message)
        app_state.add_tool_results(tool_results)
        yield MessageEndEvent(message)

        # 检查是否继续调用工具


# 循环终止检查
class LoopTerminationChecker:
    def __init__(self, max_iterations):
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.token_limit =           # 假设的 token 限制
        self.current_token_count =

    # 检查轮数上限
    # 检查是否有工具调用
    # 检查 token 预算
    # 检查显示停止信号
```

## 状态管理

采用发布-订阅

```python
class AppState:
    session_id: str
    messages: List[Message]
    current_turn: int
    token_count: int
    _subscribers: List[Callable[[StateChangeEvent, Any], None]]

    def subscribe(self, callback: Callable[[StateChangeEvent, Any], None]):
        # 订阅
        self._subscribers.append(callback)

    def _notify_subscribers(self, event: StateChangeEvent, data: Any):
        # 通知订阅者
        for callback in self._subscribers:
            callback(event, self)

    def add_message(self, message: Message):
        # 添加消息,修改当前状态
        self.messages.append(message)
        self.current_turn += 1
        self.token_count += message.token_count
        # 通知订阅者
        self._notify_subscribers(StateChangeEvent.MESSAGE_ADDED, message)


app_state = AppState(session_id="session_123", messages=[], current_turn=0,
                     token_count=0, _subscribers=[])
# 添加订阅者
# 触发订阅
app_state.add_message(Message(content="Hello"))
```

## 消息管理

- 保留最后 `max_message` 条
- 按 token 数量限制

## 长时任务的漂移检测与纠正

```python
class Goal:
    gaol: str
    main_keywords: List[str]


class DriftDetector:
    def __init__(self, similarity_threshold: float, window_size: int):
        self.similarity_threshold = similarity_threshold
        self.window_size = window_size

    def check_drift(self, current_state: AgentState, goal: Goal) -> bool:
        # 检查最近 N 轮行动
        # 计算相似度:语义/关键词


class ReflectionManager:
    def __init__(self, drift_detector: DriftDetector):
        self.drift_detector = drift_detector

    def reflect(self, current_state: AgentState, goal: Goal) -> Optional[str]:
        # 检查漂移
        if self.drift_detector.check_drift(current_state, goal):
            # 生成反思内容
            reflection = self.generate_reflection(current_state, goal)
            return reflection
        return None
```

## 插件扩展

包含多个 skill、hook（构造函数）、command

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1789984106798-1694cb11-61d7-437e-bf0a-4c3a5320fd13.png" width="303" alt="插件扩展结构">

```python
class PluginMainfest:
    name:
    version:
    skills:
    hooks:
    commands:
    permissions:


class PluginManager:
    def __init__(self):

    # 加载插件
    def load_plugin(self, plugin_dir: str):
        plugin_data = self._load_plugin_manifest(plugin_dir)
        plugin_mainfest = PluginMainfest(**plugin_data)
        plugin_id = plugin_mainfest.name

        # 动态导入插件模块
        # 初始化插件类
        spec = importlib.util.spec_from_file_location(
            plugin_id, os.path.join(plugin_dir, f"{plugin_mainfest.main}"))
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)

        # 注册 Skills
        for skill in plugin_mainfest.skills:
            self._register_skill(skill, plugin_module)

        # 注册 hooks
        for hook in plugin_mainfest.hooks:
            self._register_hook(hook, plugin_module)
```

## 可观测体系

## 人类在环

状态持久保存

## 容错+恢复

## 幻觉防护

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1789984612726-8b83d013-2a7e-4277-b94c-de87be26da61.png" width="473" alt="幻觉防护机制">

- **交叉检验**：多温度下，回答一致性
- **置信度评估**：生成的 token 概率、回答是否矛盾、memory 事实评估、逻辑连贯性、忠实度
