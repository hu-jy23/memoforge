# MemoForge 记忆系统设计

> 本文档记录 MemoForge 记忆系统的完整设计，包括初始架构和 notes 层扩展设计。用于 final report 写作参考。

---

## 当前 Harness 的记忆系统设计全景

### 一、整体结构：5层 + 物理映射

```
Layer 1  用户偏好        preferences.md              ← 编码风格、工作流偏好
Layer 2  环境记忆        wiki/concepts/, wiki/config/ ← 领域概念、硬件约束、配置字段
Layer 3  Repo/API记忆   wiki/api/, wiki/workflows/   ← API签名、操作流程
Layer 4  技能记忆        skills/                      ← 可复用模式（从Layer5晋升）
Layer 5  学习日志        learning/                    ← 每个task一个文件，原始证据层
```

所有内容在 `agents/memory/store/`。**Layers 2+3 统一用 LLM Wiki 承载**，这是整个记忆系统的地基。

---

### 二、LLM Wiki（Layers 2+3）的设计

Wiki 采用 Andrej Karpathy 提出的模式：**raw docs → LLM 提炼 → 结构化 wiki pages**，而不是做 RAG（向量检索）。

**为什么不用 RAG？**

| | RAG | LLM Wiki |
|---|---|---|
| 存储形式 | 向量 + 原文分块 | 人类可读的 Markdown |
| 检索方式 | 向量相似度 | Agent 直接 `Read` 文件 |
| 准确度 | 依赖 embedding 质量 | LLM 已提炼，密度高 |
| 可调试 | 难（黑盒） | 易（直接看文件内容） |
| 工具依赖 | 需要向量数据库 | 只需要文件系统 |
| 适合的内容 | 长文全文检索 | 精炼的领域知识点 |

**Wiki 不是原始文档的镜像，是提炼后的知识**。一个 35k 字的 API 文档模块，提炼成 3–5 个 wiki 页面，每页 50–100 行，只保留 agent 可能用错的地方。

#### Wiki 的目录分类

```
wiki/
  concepts/   领域术语、硬件抽象、模型架构事实
  api/        API 签名、参数语义、已知 behavioral quirks
  errors/     已知报错模式 + 根因 + 解法
  config/     配置字段、有效值、运行时 flags
  workflows/  多步骤操作流程、非标准训练流程
```

每个页面有统一的 frontmatter schema：

```yaml
---
title: 人类可读标题
category: concepts | api | errors | config | workflows
sources: ["来源描述"]
last_updated: YYYY-MM-DD
confidence: high | medium | low
---
```

`confidence` 是关键字段：`high` = 官方文档确认或 2+ 次任务验证，`medium` = 单次观察，`low` = 暂定/有冲突。Agent 看到 `low` 时应当额外谨慎。

#### Index + Log 的作用

**`index.md`**：一行一个页面的目录，是 agent 找页面的入口。Memory Agent 和 Coder/Verifier 都先读这个，再 drill 进具体页面。

**`log.md`**：append-only 操作日志，记录 init/create/update/delete/write-back/skill-promoted/contradiction/gap/orphan 等操作。不是给 agent 查的，是给人类审计用的——可以看到 wiki 是怎么演化的。

---

### 三、写入边界（关键设计决策）

```
                    写 store/    写 workspace/    运行代码
Planner             ✗            ✗（仅生成文字）  ✗
Coder               ✗            ✓（patch, summary）✗
Verifier            ✗            ✓（verify_result）✓（测试）
Memory Agent        ✓            ✗（只读）         ✗
Starter Agent       ✓（仅 wiki/） ✗                ✗
```

**Memory Agent 是 store/ 的唯一写者**。这个约束的目的：

1. **防止并发写冲突**：多 agent 同时写同一个 wiki 页面会导致内容混乱
2. **保持 wiki 质量**：Coder 直接写 wiki 可能把未验证的假设混进去；先经过 Memory Agent 过滤
3. **强制 write-back 协议**：所有学到的东西必须经过 learning log → wiki 这个路径，不能被绕过

Coder 和 Verifier **可以直接读** wiki（不需要经过 Memory Agent），这是为了速度——读操作没有冲突风险，加一层中间人只是浪费一个 Agent 调用。

---

### 四、积累机制：Write-back 流程

每个 task cycle 完成后，Planner 召唤 Memory Agent 执行 5 步 write-back（写在 Memory Agent 的 `CLAUDE.md` prompt 里，不是代码逻辑）：

```
Step 1（必做）  → 写 learning/{task_id}.md
Step 2（fail时）→ 写/更新 wiki/errors/{slug}.md（只针对 domain error，不针对普通 bug）
Step 3（pass且potential_skill=true）→ 评估是否晋升到 skills/
Step 4（pass且有新领域事实）→ 更新 wiki/api/ 或 wiki/config/
Step 5（必做）  → 追加 log.md 记录
```

**什么是 domain error（触发 Step 2）？**

判断标准：如果换一个领域这个错误就不会发生，那就是 domain error，应该写进 `wiki/errors/`。例如：

- `parallel.grad_accumulation_shard` 字段路径放错层级 → domain error（MindFormers 特定配置层级）
- Python 语法错误 → 不是 domain error，不写 wiki

**为什么 fail 也要写 learning log？**

失败记录是最有价值的。Memory Agent 在后续 Coder 重试时可以把历史失败作为 context_ref 传进去——"上次走这条路失败了，原因是 X，这次避开"。

---

### 五、Skill 晋升机制（Layer 4）

技能不是手动创建的，是从 Layer 5 自动晋升的：

```
第 1 次成功任务：learning log 标记 potential_skill: yes，附一句描述
        ↓
Memory Agent 每次 write-back 时：扫描 learning/ 目录，找相似的 potential_skill: yes 记录
        ↓
2+ 次相似成功记录 + 满足"domain-specific" + 满足"clear trigger" → 晋升到 skills/
```

**晋升的三个必要条件**（缺一不可）：

1. **2+ 次成功**：单次可能是巧合，两次以上才算模式
2. **domain-specific**：通用编程知识不值得写 skill，只有领域特有的才有价值
3. **clear trigger**：触发条件必须能用一句话说清楚，模糊的模式不能成为 skill

---

### 六、各 Agent 的记忆使用路径

**Coder 的查询顺序**（写代码前）：

```
1. index.md → 找相关页面
2. api/ → API 签名、参数、gotcha
3. concepts/ → 领域概念和心智模型
4. config/ → 环境配置、编译选项
5. errors/ → 如果任务涉及已知失败模式
6. skills/ → 有没有可以直接套用的模板
```

**Verifier 的查询顺序**（验证前，比 Coder 更偏重 errors）：

```
1. errors/ → 有没有匹配的已知报错（优先级最高，直接套解法）
2. config/ → 测试环境是否满足硬件/驱动要求
3. learning/ → 历史上有没有类似的失败
```

**Memory Agent 的查询方式**：
- write-back 模式：读 verify_result.json + coder_summary.md，据此判断写哪些 layer
- query 模式：先读 index.md，再 drill 相关页面，组合成回答

---

### 七、当前已有的内容（MindSpore pilot）

当前 release 里已经积累：

```
wiki/       38 个页面
  api/      mindformer-config, mindformer-register, mf-train-wrappers,
            trainer_class, training_callbacks, model_base_classes,
            lora_model, generation_config ...（共 ~15 页）
  config/   parallel_context_configuration, version-compatibility,
            environment-variables, lora_config ...（共 ~6 页）
  concepts/ parallel_training_modes, generation_strategy,
            lora_pet_overview ...（共 ~5 页）
  errors/   （目前空，第一次真实 fail 时会填充）
  workflows/ training_entry_points, config_change_validation,
             remote_monitoring ...（共 ~5 页）

learning/   1 个文件（custom-callback-norm-lr-01）
skills/     空（potential_skill: yes 已标记，等待第 2 次晋升）
```

补充结构：

- `wiki/scripts/validate_wiki.py` 检查 wiki frontmatter、index、wikilink。
- `wiki/scripts/query_wiki.py` 提供关键词查询入口。
- `skills/data/` 记录 skill schema、freshness、provenance policy。
- `skills/scripts/validate_skills.py` 检查单文件 skill 和 package skill 的结构。
- `skills/scripts/query_skills.py` 查询已晋升 skill 和 learning 中的 potential skill。
- `tools/validate_harness.py` 汇总 prefix、wiki、skills、runtime extension 与当前 workspace artifact 检查。

---

### 八、设计权衡和已知问题

**优势**：
- Wiki 可读可调试，出错容易定位
- 记忆积累是自动的，不需要用户手动管理
- 读写边界清晰，没有并发冲突

**当前已知缺口**：

| 问题 | 影响 | 现状 |
|---|---|---|
| `wiki/errors/` 为空 | Verifier 第一次遇到已知错误时没有可查的解法 | 需要真实任务积累 |
| Coder/Verifier 的 CLAUDE.md 是 scaffold | 没有做过端到端召唤测试 | Simulation 3 已验证流程，但 Agent 内部复杂逻辑未测 |
| MindSpore-docs 5 个 topic 未入库 | nn_api/communication_api 等缺失 | 已知，可随时补跑 |

---

## 记忆系统扩展设计：Notes 层与 Consolidation 机制

> 以下为对初始设计的扩展讨论。Notes 层、consolidation 协议和 sample write-back 已在当前 MemoForge 中部分落地；更完整的自动化 consolidation 仍是后续工作。

### 背景：初始设计的问题

初始设计的 Step 4 在每次 pass task 后直接更新 wiki。这导致：

- Wiki 的每一次写入质量参差不齐（单次任务观察 vs 多次验证的结论）
- Wiki 页面在不断被小幅修改，`confidence` 字段频繁变动
- 没有"草稿"阶段，所有东西要么进 wiki 要么进 learning log，中间没有过渡

**核心洞察**：既然已经舍弃了 RAG 这种机器式的记忆维护，转而使用 wiki 这种自然方式，就应该彻底遵循自然学习的节奏——学者平时 take notes，定期复习，notes 逐渐变成体系化的知识/skill。Wiki 应该是 slow and stable 的对象，不应该被每个 task 直接触碰。

---

### 一、Notes 层的定位

在现有 5 层上加一个显式的 notes 层：

```
Layer 5  learning/         per-task 结构化日志，不变
Layer 5b notes/            ← 新增，主题式笔记，快速、灵活
Layer 2+3 wiki/            wiki 由 consolidation 写入，不再被 write-back 直接触碰
```

#### Notes 与 Learning 的边界

两者是**流向关系**，不是替代关系：

```
task 完成
  │
  ├─→ learning/{task_id}.md     ← 结构化的证据存档，不可变
  │       "发生了什么"
  │
  └─→ notes/{topic}.md          ← 提炼出的领域事实，可演化
          "我们学到了什么"
               │
               │ consolidation
               ▼
          wiki/{category}/{page}.md
```

| | `learning/` | `notes/` |
|---|---|---|
| **组织维度** | 以 task 为单位（一 task 一文件） | 以主题为单位（一 API/概念一文件） |
| **可变性** | 只增不改（追加 retry 段） | 自由编辑，可合并、删除、重组 |
| **目的** | 回答"task X 发生了什么" | 回答"我们现在对 topic Y 知道什么" |
| **时序** | 严格按时间顺序 | 无时序，按知识结构 |
| **写入时机** | 每次 write-back 必写（Step 1） | 每次 write-back 有新发现才写 |
| **读取者** | Memory Agent（历史检索/技能晋升） | Coder、Verifier、Memory Agent |

`learning/` 是**法庭记录**（what happened, immutable evidence），`notes/` 是**工作笔记**（what we know, living document）。

#### Notes 页面的内部格式

不需要 frontmatter，按置信度分区：

```markdown
# notes/mf-train-wrappers.md
_Last updated: 2026-05-17_

## Confirmed（多次任务验证）

- `MFTrainOneStepCell` 输出元组固定布局：
  `[0]=loss [1]=overflow [2]=loss_scale [3]=lr [4]=global_norm`
  来源：custom-callback-norm-lr-01（2026-05-17）、[second task]（待补）

## Observed Once（单次观察，待验证）

- `use_clip_grad=false` 时 index 4 是 `None`，不会 raise，只是静默返回 None
  来源：custom-callback-norm-lr-01（2026-05-17）

## Uncertain / Conflicting

- pipeline parallel 下 `cur_step_num` 是否按 micro-batch 计数？
  coder_summary 里提到了但未实测
```

**只有 Confirmed 区块才考虑写进 wiki**，Observed Once 是候选，Uncertain 在笔记里等待澄清。

---

### 二、Write-back 协议的调整

**Step 4 的改动**：原来"直接更新 wiki"，改为"写/更新 notes"：

```
Step 4 — If pass AND new domain fact observed:
  找 notes/ 下主题最相关的文件（没有则新建）
  追加观察结果，标注 task_id 和日期
  如果此观察在 notes 里已存在（Observed Once），升级到 Confirmed，补充来源
  不触碰 wiki
```

**Wiki 只在 consolidation 时更新**，不在 write-back 中更新。

---

### 三、Consolidation 机制

三种触发方式叠加：

**机制 A：手动触发（主路径）**

```
用户: "帮我把 notes 整理进 wiki"
  或: "整理 mf-train-wrappers 这个 topic 的 notes"
```

Wiki 是 deliberate 的产物，应该由人决定"现在我认为这些足够稳定了"。

**机制 B：阈值信号（辅助提示）**

Memory Agent 在每次 write-back 结束时检查：是否有 Observed Once 条目被升级为 Confirmed（即本次 task 提供了二次验证）。如果有，在 `log.md` 里打 `consolidation-ready` 标记，并在 Planner 汇报时附带提示：

```
任务完成。注：notes/mf-train-wrappers.md 现在有 2 条 Confirmed 观察，
可以考虑 consolidation 更新 wiki/api/mf-train-wrappers。
```

触发信号的核心逻辑：**Confirmed = 2+ 个独立 task 验证了同一事实**，这才是"可以进 wiki"的信号。

**机制 C：定时整理（兜底）**

用 `CronCreate` 设置周期性 consolidation（如每周），防止 notes 和 wiki 长期分叉。

```
三种机制的关系：

日常任务结束
    ↓
B: Memory Agent 检测 Confirmed 升级 → 提示用户
    ↓
用户决定立刻整理？
  是 → A: 手动触发 consolidation
  否 → notes 继续积累，等下次
    ↓
（如果长期没整理）
C: 每周定时 consolidation 兜底触发
```

#### Consolidation 的执行逻辑

Memory Agent 在 consolidation 模式下：

```
对每个 Confirmed 条目：
  wiki 里已有这个事实？
    是 → 确认一致性，confidence 升为 high
    否 → 写入 wiki（新建页面或追加章节）
    矛盾 → contradiction 处理（降 confidence，写 Superseded 段）

对每个 Uncertain 条目：
  保留在 notes，标注"等待更多证据"
  不写入 wiki

Confirmed 写入 wiki 后：
  notes 里将其移到 ## Consolidated 区块（或删除）
  保留原始 task_id 引用，便于溯源
```

---

### 四、扩展后的完整记忆架构

```
Layer 1   preferences.md          用户偏好，缓慢积累
Layer 2+3 wiki/                   权威知识，只在 consolidation 时更新
Layer 4   skills/                 从 notes/learning 晋升，deliberate
Layer 5a  learning/               per-task 结构化日志，immutable，证据层
Layer 5b  notes/                  主题式工作笔记，flexible，wiki 的前厅
```

**信息流向**：

```
task cycle
  │
  ├─→ learning/{task_id}.md      （always，immutable）
  │
  └─→ notes/{topic}.md           （有新发现时，mutable）
             │
             │ consolidation（manual / threshold / scheduled）
             ▼
        wiki/{category}/{page}.md  （deliberate，stable）
             │
             │ 2+ confirmed occurrences
             ▼
        skills/{skill-slug}.md     （promoted，authoritative）
```

**已落地改动**：

1. `agents/memory/CLAUDE.md` — Step 4 改为 notes 写入，并加入 consolidation 模式。
2. `agents/memory/store/notes/README.md` — 已建立 notes 目录和格式约定。
3. Coder/Verifier 的 `CLAUDE.md` — 读取顺序已加入 notes，并要求低置信度标注。

---

## 2026-05-29 演进：Evidence-backed Learning 与 Task Artifact Protocol

本轮在原有 `learning -> notes -> wiki -> skills` 记忆流之上，补了一条任务证据链。

### 一、为什么需要任务证据链

早期 `.learning` 记录的是 task cycle 发生了什么，已经能支持经验回看和 skill promotion 候选识别。但它还缺少一个关键能力：说明这条经验凭什么可信。

因此新的目标是：

- `.learning` 不再只是 event log
- `.learning` 必须引用 task contract、candidate、evidence、promotion decision
- Memory Agent 写回时不只记录结论，还记录结论的证据来源

### 二、新增 runtime artifacts

```
workspace/task_contract.md          本次任务的目标、约束、验证命令、晋升标准
workspace/plan.json                 subtasks / dependencies / context_refs
workspace/candidates.jsonl          候选实现与验证状态账本
workspace/patch/{task_id}/          Coder 输出 patch
workspace/evidence/{task_id}/       Verifier 保存日志、测试、人工检查、benchmark/profile 证据
workspace/verify_result.json        Verifier 结构化判定
workspace/promotion_decision.md     Verifier 对 learning / notes / wiki / skills 的晋升建议
```

这些 artifact 仍属于 `workspace/`，是 task-cycle runtime 产物，安全删除。Memory Agent 必须在 workspace 清理前，把有价值的证据引用写进 `learning/`。

### 三、`.learning` 新格式

新 learning entry 必须包含：

```
Summary
Task contract
Candidate evidence
Outcome
Promotion decision
Domain facts
Potential skill
```

也就是说，`.learning` 是证据索引和经验摘要，不复制所有日志。

### 四、sample cycle

`custom-callback-norm-lr-01` 已被升级为 sample task cycle：

- `workspace/task_contract.md`
- `workspace/plan.json`
- `workspace/candidates.jsonl`
- `workspace/evidence/custom-callback-norm-lr-01/`
- `workspace/verify_result.json`
- `workspace/promotion_decision.md`
- `agents/memory/store/learning/custom-callback-norm-lr-01.md`
- `agents/memory/store/notes/mf-train-wrappers.md`

当前验证：

- `python3 -m py_compile workspace/patch/custom-callback-norm-lr-01/norm_lr_logger.py`
- `python3 -m json.tool workspace/verify_result.json`
- `candidates.jsonl` line-by-line JSON parse
- `python3 agents/memory/store/wiki/scripts/validate_wiki.py`

### 五、与 skill promotion 的关系

Skill promotion 现在必须同时满足：

1. 2+ successful learning entries
2. domain-specific pattern
3. clear trigger
4. evidence refs exist
5. `promotion_decision.md` accepts or explicitly recommends skill consideration

这使 skill promotion 从“看起来有用”升级为“由证据支持的程序性记忆晋升”。
