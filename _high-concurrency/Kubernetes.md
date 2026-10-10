---
title: "Kubernetes"
date: 2026-10-10
---

**目录**

- [架构概览](#架构概览)
  - [1. 控制平面（Control Plane）组件](#1-控制平面control-plane组件)
  - [2. 工作节点（Worker Node）组件](#2-工作节点worker-node组件)
  - [3. 组件如何协作（简化流程）](#3-组件如何协作简化流程)
- [核心对象与工作负载](#核心对象与工作负载)
  - [无状态应用（Stateless）](#无状态应用stateless)
  - [有状态应用（Stateful）](#有状态应用stateful)
- [网络与服务发现](#网络与服务发现)
  - [Service（服务发现与负载均衡）](#service服务发现与负载均衡)
- [调度与高可用](#调度与高可用)
  - [1. 调度过程（kube-scheduler）](#1-调度过程kube-scheduler)
  - [2. 关键调度机制](#2-关键调度机制)

---

> Kubernetes 可实现部署与扩展应用、负载均衡、自我修复等运维任务的自动化

## 架构概览

> 集群 = 控制平面 + 多个工作节点

### 1. 控制平面（Control Plane）组件

这些组件共同维护集群的“期望状态”，并不断把实际状态调谐到期望状态。

| 组件 | 作用 | 关键点 |
| --- | --- | --- |
| **kube-apiserver** | 集群的唯一入口（前端） | 所有请求（kubectl、控制器、节点）都必须经过它。**负责认证、授权、准入控制，然后写入 etcd。**设计为可水平扩展。 |
| **etcd** | 集群的“数据库” | 高可用键值存储，**保存所有集群状态（Pod、Service、Config 等）**。数据一致性的核心。 |
| **kube-scheduler** | 调度器 | 监听未绑定节点的 **Pod**，根据资源需求、亲和性、污点等规则，选择最合适的**节点**，并完成**绑定**。 |
| **kube-controller-manager** | 控制器管理器 | 运行多个控制器（Deployment Controller、Node Controller、EndpointSlice Controller 等）。每个控制器不断做“**调谐循环**”（Reconciliation Loop）：观察实际状态 → 与期望状态对比 → 采取行动。 |

### 2. 工作节点（Worker Node）组件

| 组件 | 作用 | 关键点 |
| --- | --- | --- |
| **kubelet** | 节点代理 | 接收 apiserver 下发的 PodSpec，确保容器按规格运行并保持健康。**负责与容器运行时交互、上报节点和 Pod 状态**。 |
| **kube-proxy** | 网络代理 | 在节点上维护网络规则（iptables 或 IPVS 模式），**实现 Service 的负载均衡和流量转发**。 |
| **容器运行时**（Container Runtime） | 真正运行容器 | 常见有 containerd、CRI-O 等。通过 CRI（Container Runtime Interface）与 kubelet 通信。Docker 已不再是默认运行时。 |

### 3. 组件如何协作（简化流程）

1. 用户通过 kubectl apply **提交 YAML** → 请求到 kube-apiserver
2. apiserver 验证后**写入 etcd**
3. kube-controller-manager 发现新资源，**创建对应的 Pod 对象**
4. kube-scheduler 为 Pod 选择节点并**绑定**
5. 目标节点的 kubelet 收到通知，调用容器运行时**启动容器**
6. kube-proxy 根据 Service **更新网络规则**
7. 各控制器**持续监控**，保证实际状态与期望状态一致

## 核心对象与工作负载

> Kubernetes 中几乎所有东西都是对象（Object），通过 YAML 声明。

**什么是无状态 vs 有状态？**

### 无状态应用（Stateless）

- **副本等价**：任意一个 Pod 挂掉或被替换，**另一个 Pod 都能无差别地接管工作**。
- **不留痕迹**：Pod 内部不产生必须持久保存的数据，数据一般存储在外部数据库或缓存**中（如 Redis/MySQL）。
- **网络无依赖**：Pod 的 IP 随机变动，不需要固定的网络标识或启动顺序。
- **典型代表**：Web 前端、Nginx 网关、微服务 API 接口、静态网页服务器。
- **对应资源**：Deployment

### 有状态应用（Stateful）

- **唯一身份**：每个 Pod 拥有固定的网络标识（固定主机名，如 pod-0, pod-1），重启或重建后标识不变。
- **绑定存储**：每个 Pod 通常需要独立的持久化卷（PVC），即便 Pod 迁移到其他节点，也要精准挂载回自己原本的数据盘。
- **集群顺序**：副本间往往存在主从/协同关系，启动、更新或扩缩容时必须按严格顺序（如 0 → 1 → 2）进行。
- **典型代表**：**MySQL 主从集群**、MongoDB、Kafka、Zookeeper、Elasticsearch。
- **对应资源**：StatefulSet + Headless Service（无头服务）

## 网络与服务发现

Kubernetes 网络模型有三条铁律：

1. 每个 Pod 有独立 IP
2. 所有 Pod 之间可以直接通信（不需要 NAT）
3. 节点上的 Agent 可以与所有 Pod 通信

### Service（服务发现与负载均衡）

> Pod IP 是动态的，Service 提供稳定入口。

工作原理：

- Service 通过 Selector 关联一组 Pod
- EndpointSlice 记录后端 Pod 的 IP 和端口
- kube-proxy 在节点上维护规则，把流量转发到真实 Pod

## 调度与高可用

### 1. 调度过程（kube-scheduler）

调度分为两个主要阶段：

1. **过滤（Filtering）**：排除不满足条件的节点
   （资源不足、端口冲突、亲和性不满足、污点不容忍等）
2. **打分（Scoring）**：对剩余节点打分，选择最高分节点

常见调度影响因素：

- 资源 requests / limits
- nodeSelector / Node Affinity
- Pod Affinity / Anti-Affinity
- Taints & Tolerations
- Topology Spread Constraints（拓扑分布约束）
- 镜像本地性、优先级等

### 2. 关键调度机制

- **Taints & Tolerations**：节点“排斥”某些 Pod，Pod 需要“容忍”才能调度上去（常用于控制平面节点、GPU 节点、特殊硬件节点）
- **Affinity**：吸引（把相关 Pod 放在一起或同一区域）
- **Anti-Affinity**：排斥（把副本分散，提高高可用性）
- **Topology Spread Constraints**：控制 Pod 在不同故障域（zone、node）的分布均匀度
