---
title: "GNN-RAG"
date: 2026-10-10
---

**目录**

- [图神经网络 GNN](#图神经网络-gnn)
  - [种子节点](#种子节点)
  - [PageRank Nibble 获得子图](#pagerank-nibble-获得子图)
  - [计算问题 q 与关系 r 的得分](#计算问题-q-与关系-r-的得分)
  - [GNN 多层关系消息的传递](#gnn-多层关系消息的传递)
  - [局部子图的提取](#局部子图的提取)

---

GraphRAG 全局汇总 = 社区，GNN-RAG 借助 GNN 的高效图检索，**多跳推理**

## 图神经网络 GNN

### 种子节点

问题 q 中的实体结合上下文到图中定位种子节点

### PageRank Nibble 获得子图

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791452609819-25fd16e6-4eaf-4081-a7a4-55c80f0d23b3.png" width="489" alt="PageRank Nibble 子图获取">

### 计算问题 q 与关系 r 的得分

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791452700694-765d27b1-a758-4107-ab35-28e2d7b1461b.png" width="487" alt="问题与关系得分计算">

### GNN 多层关系消息的传递

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791452726517-108821b1-3a70-4491-af87-bd55165a54c1.png" width="489" alt="GNN 多层关系消息传递">

> <img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791452791216-e433dbbc-2e28-49e1-ad70-ac9fe997f1dc.png" width="493" alt="GNN 消息传递细节">

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791452762889-95e90f41-2d4f-4bb5-9015-8131e52b339e.png" width="485" alt="GNN 消息传递图示">

### 局部子图的提取

<img src="https://cdn.nlark.com/yuque/0/2026/png/47122292/1791452973533-8ad5f603-615b-4c96-baf9-de345a8c175b.png" width="535" alt="局部子图提取">
