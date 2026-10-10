---
title: "Python asyncio 的运行本质"
date: 2026-10-10
---

**目录**

- [🏗️ 一、 三大核心角色的职责划分](#-一-三大核心角色的职责划分)
- [🔄 二、 Future 的双向持有与唤醒机制](#-二-future-的双向持有与唤醒机制)
- [⏱️ 三、 核心驱动的时间轴与顺序表](#-三-核心驱动的时间轴与顺序表)
  - [当协程处于 await 状态、CPU 在跑其他 Task 时，数据是怎么产生的？](#当协程处于-await-状态cpu-在跑其他-task-时数据是怎么产生的)
- [🎯 总结金句](#-总结金句)
- [任务编排：asyncio.run 与 asyncio.gather](#任务编排asynciorun-与-asynciogather)
- [跳出单线程：剥离同步阻塞与 CPU 密集型任务](#跳出单线程剥离同步阻塞与-cpu-密集型任务)

---

**await 交出 CPU 控制权，把 CPU 控制权还给 Event Loop（事件循环），让 Event Loop 去调度另一个 Task（协程）**

**前置知识**：task 的 `.send()` 本质上是 yield

```python
def my_generator():
    val = yield 1  # 暂停并返回 1；当外部 send 数据时，val 接收数据并继续向下
    print(f"Received: {val}")
    yield 2

gen = my_generator()
res1 = gen.send(None)  # 启动生成器，运行到第一个 yield 处，res1 = 1
gen.send("Hello")      # 恢复生成器，把 "Hello" 传给 val，运行到下一个 yield，打印 Received: Hello
```

## 🏗️ 一、 三大核心角色的职责划分

`asyncio` 的高效运行依赖于 **协程**、**Task** 与 **事件循环** 的精妙配合：

| 角色 | 物理形态 | 核心职责 | 对应底层动作 |
| --- | --- | --- | --- |
| **协程 (Coroutine)** | `async def` 生成的状态机对象 | **定义业务逻辑**：遇到耗时操作时主动挂起，让出 CPU。 | 执行到 `await` 时抛出（`yield`）内部等待的 `Future`。 |
| **任务 (Task)** | `Future` 的子类（包装协程的外壳） | **驱动状态演进**：将协程与事件循环绑定，监听 `Future` 状态。 | 调用 `coro.send()` 推动协程，挂载 `_wakeup` 回调。 |
| **事件循环 (Event Loop)** | 单线程无限循环 (`_run_once`) | **调度与响应**：管理队列、监听 OS 事件与定时器。 | 维护 `Ready Queue`、`Timer Heap` 及 `epoll_selector`。 |

asyncio.run(某异步函数()) 会自动**把协程包装成 Task 对象 → Task 初始化时会自动调用 loop.call_soon(self.step) 把任务塞进事件循环的就绪队列 = task 进入调度状态**，如果此时 CPU 刚好有空闲（比如遇到了某个 `await`），事件循环立刻就会去执行这个 task

```python
class Task(Future):
    def __init__(self, coro):
        super().__init__()
        self._coro = coro
        # 1. 创建 Task 时，立刻把自己投递到 Event Loop 的 Ready Queue 中
        loop = asyncio.get_running_loop()
        loop.call_soon(self._step)

    def _step(self, exc=None):
        """这是 Task 的核心驱动循环，负责调用 coro.send() 并处理返回的 Future"""
        try:
            if exc is None:
                # 驱动协程向前推进！协程遇到 await 时会 yield 出一个 child_future
                result_future = self._coro.send(None)
            else:
                result_future = self._coro.throw(exc)
        except StopIteration as e:
            # 协程执行完毕（return），设置 Task 自己的结果
            self.set_result(e.value)
            return

        # -------------------------------------------------------------
        # 【最核心的关键实现在这里！】
        # 协程 yield 出了一个正在等待的 result_future
        # Task 负责把自己的唤醒函数 `_wakeup` 挂到这个 result_future 的 callbacks 列表中！
        # -------------------------------------------------------------
        result_future.add_done_callback(self._wakeup)

    def _wakeup(self, future):
        """当被等待的 Future 完成时，此回调被触发！"""
        try:
            # 拿到 future 的结果（如果报错会在这里抛出）
            future.result()
        except Exception as exc:
            # 如果 future 报错了，带上异常重新驱动协程
            self._step(exc=exc)
        else:
            # 恢复驱动协程继续向前走！
            self._step()
```

---

## 🔄 二、 Future 的双向持有与唤醒机制

`Future` 是连接上层业务协程与底层 I/O 驱动的**数据桥梁**。

```text
                  ┌───────────────────────────────┐
                  │          Task (上层)          │
                  └──────────────┬────────────────┘
                                 │
                 add_done_callback(self._wakeup)
                                 │
                                 ▼
                         【 Future 对象 】
                    (初始状态: PENDING, _result=None)
                                 ▲
                                 │
                        set_result(data)
                                 │
                  ┌──────────────┴────────────────┐
                  │    Event Loop / OS (底层)     │
                  └───────────────────────────────┘
```

1. **上层 (Task)**：通过 `coro.send(None)` 拿到 `Future` 后，在其上绑定 `add_done_callback(self._wakeup)`（设置唤醒闹钟）。
2. **底层 (Event Loop / OS)**：在创建 `Future` 之初，已将其指针存入底层的 `fd_map`（Socket 映射表）或 `Timer Heap`（小顶堆）。
3. **闭环解耦**：当底层数据准备就绪，底层模块直接取出指针执行 `future.set_result(data)`，自动触发上层绑定的 `_wakeup` 回调，将 Task 重新塞入 `Ready Queue`。

---

## ⏱️ 三、 核心驱动的时间轴与顺序表

很多初学者的误区在于以为“协程在后台异步跑”，而真相是：**所有 Python 代码都在主线程同步运行，只有等待 I/O 时才是真正的非阻塞。**

```text
时刻 T1 (Task._step 执行):
  └─▶ 执行 child_future = coro.send(None)
  └─▶ CPU 控制权切入协程内部，同步运行至 await child_future
  └─▶ 协程冻结挂起！将 child_future 返回给 Task

时刻 T2 (挂钩子):
  └─▶ Task 拿到 child_future，执行 child_future.add_done_callback(self._wakeup)
  └─▶ Task._step 退出，控制权交还 Event Loop

时刻 T3 (硬件/OS 准备就绪):
  └─▶ epoll_wait 被唤醒，Event Loop 拿到可用 Socket FD
  └─▶ Event Loop 执行 child_future.set_result(data)：数据保存起来，遍历执行注册的回调函数
  └─▶ 触发 _wakeup 回调，将 Task._step 压入 Ready Queue

时刻 T4 (恢复运行):
  └─▶ Event Loop 弹出并执行 Task._step
  └─▶ 执行 coro.send(data)，将数据塞回协程，协程从 await 处恢复向下运行！
```

### 当协程处于 await 状态、CPU 在跑其他 Task 时，数据是怎么产生的？

```text
1. CPU 忙碌期 ──▶ 网卡硬件 + DMA 控制器 + 操作系统内核：
                 数据包到达网卡 ──(DMA直接传输)──▶ 写入 OS 内核缓冲区（完全不占用 CPU）。

2. epoll 唤醒 ──▶ Event Loop (主线程)：
                 epoll_wait 返回 ──▶ 借用微秒级 CPU 执行 data = sock.recv()（从内核拷贝到内存）。

3. 数据传递 ──▶ Future 状态机：
                 执行 future.set_result(data) ──▶ 将 data 指针沿着回调链注入协程。
```

---

## 🎯 总结金句

1. **`await` 的本质**：不是启动异步任务，而是**主动暂停自己**，把等待的 `Future` 向上抛出。
2. **`create_task` 的本质**：把协程包装成 Task，并**立刻往 `Ready Queue` 里塞入一次 `_step` 驱动指令**。
3. **`Event Loop` 的本质**：一个在死循环里不停平衡 **“内存就绪队列（`Ready Queue`）”、“定时器小顶堆（`Timer Heap`）”** 和 **“操作系统 I/O 监听（`epoll`）”** 的调度员。

## 任务编排：`asyncio.run` 与 `asyncio.gather`

asyncio.run(某异步函数()) 启动事件循环并运行某异步函数

- 将 `say_hello()` 协程包装为一个 **Task** 并注册进事件循环。
- 驱动事件循环运行，直到 `say_hello` 彻底执行完毕。

`asyncio.gather` 到底做了什么？

主协程（比如你的 `main` 函数）在这里挂起，一直等，直到 `tasks` 列表里的**每一个** Task 都运行结束 + 按顺序收集结果

如果不写 `gather` 会发生什么？

主程序瞬间就执行完了！虽然后台的 `tasks` 已经被启动，但主程序并没有等它们，拿不到结果。

## 跳出单线程：剥离同步阻塞与 CPU 密集型任务

Event Loop 是单线程的，如果碰到**无法异步化的耗时任务**怎么办？这就需要用到线程池与进程池剥离。

```text
耗时任务的分类与剥离策略
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
   【同步阻塞 I/O 或 释放 GIL 的 C 扩展】                    【纯 Python 实现的 CPU 密集型】
   如: requests, 文件读写, NumPy 计算                     如: 大列表密集循环, 复杂数学计算
            │                                                     │
            ▼                                                     ▼
   asyncio.to_thread(func, *args)                        loop.run_in_executor(ProcessPoolExecutor)
            │                                                     │
            ▼                                                     ▼
   • 提交到全局默认 ThreadPoolExecutor                   • 通过 IPC (Pipe/Socket) 将任务序列化
   • 主线程拿到 Future 后 await 挂起                       • 发送给独立 Python 子进程执行
   • 避免主线程 Event Loop 被卡死                        • 突破 GIL 限制，真正利用多核 CPU
```

`asyncio.to_thread()`：基于**线程池**的轻量剥离

- **底层机制**：Python 在后台维护了一个全局默认的 `ThreadPoolExecutor`（线程池）。调用 `await asyncio.to_thread(func, *args)` 时，`asyncio` 会把 `func` 提交给线程池里的空闲线程执行，同时**在主线程返回一个 `Future`**。主线程遇到 `await` 挂起，继续去调度其他请求；直到子线程执行完毕并设置 `Future` 的结果，主线程再唤醒后续代码。
- **适用场景**：同步阻塞 I/O 操作、释放了 GIL（全局的 Python 解释器相关的东西）的 C 扩展库任务

`ProcessPoolExecutor`：基于**进程池**的硬核隔离

- **底层机制**：通过 `loop.run_in_executor(process_pool, func)` 将任务序列化后通过 IPC（进程间通信，如 Pipe/Socket）发送给独立的 Python 子进程执行。
- **适用场景**：纯 Python 实现的 CPU 密集型任务

> 抢占通过占用 CPU 的时间衡量

**保持 Event Loop 主线程极度轻量**

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1785985083862-ee0f1fdb-ee8e-444c-8f74-8aad5955d6c1.png" width="588" alt="Event Loop 轻量化示意">
