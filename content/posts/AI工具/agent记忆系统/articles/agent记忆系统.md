---
title: Agent记忆系统——omp + Hindsight + pgvector 配合记录
type: categories
categories: AI工具
abbrlink: ai-memory-stack
description: 记录本机 AI 编码代理的记忆链路:三个组件各自干什么、一次会话里怎么串起来跑
draft: true
date: 2026-10-22 00:00:00
---

# 1、这一套用哪三件工具

| 工具 | 角色 | 跑在哪 |
|---|---|---|
| omp | AI 编码代理本体,会话客户端 | 宿主机进程,配置在 `~/.omp/agent/config.yml` |
| Hindsight | 记忆服务(存、取、整理事实的服务器) | Docker 容器 `hindsight`,API `localhost:8888`,管理页 `9998` |
| pgvector | 向量数据库,Hindsight 的持久层 | Docker 容器 `hindsight-pg`,端口 `5432` |

omp 不自己存记忆,`memory.backend` 指到 hindsight;Hindsight 不自己存数据,底下挂 pgvector。三件各管一段:对话归 omp,记忆逻辑归 Hindsight,字节落地归 pgvector。

关键配置就这几行:

```yaml
memory:
  backend: hindsight
hindsight:
  apiUrl: http://localhost:8888
  recallBudget: high
  recallMaxTokens: 8000
  retainEveryNTurns: 1
```

# 2、一次会话里它们怎么配合

按时序走一遍,这是全文核心:

```
会话开始
   │
   ├─ autoRecall(首回合)
   │     omp 按当前任务向 Hindsight 发起检索
   │     预算 budget=high / 上限 8000 tokens
   │     取两类记忆: world(事实) + experience(经历)
   │     结果以记忆块形式注入系统提示
   │
   ├─ 心智模型注入(mentalModelsEnabled + autoSeed)
   │     Hindsight 里沉淀出的三份摘要一起进上下文:
   │     项目约定 / 项目决策 / 用户偏好
   │
每进行一回合
   │
   ├─ autoRetain(retainEveryNTurns: 1)
   │     每回合把整会话(full-session)交给 Hindsight
   │     服务端与已有记忆做去重,再 upsert 写入 pgvector
   │
会话结束
   └─ flush 收尾,最后一批事实落库
```

配合的实质:**读一次(开场),写每回合(结束)**。我正常干活,不感知它;需要感知的时候看第 4 节。

# 3、存储结构:一个仓库存多项目

服务端物理上只有一个 bank(名为 omp),逻辑上按项目标签隔离——比如这台机器上的项目会打成 `project:xxx` 标签,检索时"本项目标签 + 全局无标签记忆"一起命中。

好处是零配置、互不丢失;代价是**物理全局**:知道接口就能跨标签看到别的标签内容,个人自用无所谓,多人共用不行。

# 4、我能主动按的按钮

| 入口 | 作用 |
|---|---|
| `recall` 工具 | 手动检索,验证"某件事记没记住" |
| `retain` 工具 | 手动写入一条事实(不等自动流程) |
| `reflect` 工具 | 对多个记忆片段做综合,给结论 |
| `/memory view` / `stats` | 看本地缓存与统计 |
| `/memory clear` | **只清本地会话缓存,不删服务端 bank**;彻底清理要进 Hindsight 的 Web 页(9998)或它的 API |
| `GET /v1/default/banks` | 直接问 API:有几个仓、多少条事实、最近写入时间 |

另外两条边界认知(踩过的坑):上游来源的记忆不可逐条修改(memory_edit 不可用);记忆文件没有 `memory://` 这种 URL 可读。

# 5、今天的一次体检

容器 13 分钟前刚重启过,验证读链路:

```
docker ps → hindsight Up / hindsight-pg Up
curl http://localhost:8888/v1/default/banks → 200
recall("...") → 命中 54 条,时间戳新鲜
```

结论:重启后数据没丢(持久卷挂对了),开场召回、手动检索两条路都通。

# 6、后记

这套的价值要到换会话才体现:新开窗口,项目约定、上次做到哪、我个人的提交格式偏好,都是自带进来的,不用重讲。记错了就手动 retain 一条对的覆盖,或者进 9998 页面手工清理。
