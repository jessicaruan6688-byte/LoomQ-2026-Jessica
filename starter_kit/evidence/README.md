# LoomQ 人工评分证据

这份文件是人工评分材料的统一入口。请直接编辑它，只填写要申报的项目。截图、原始结果或图表统一放在 `starter_kit/evidence/files/`，也可以引用 `starter_kit/` 中已有的代码和文档。

证据包是可选的。没有申报某项人工分时，留空即可，不影响自动评分。

## 提交前填写

把要申报项目的方框改成 `[x]`，并填写对应内容：

- [x] L1 真机（量旋 Bell 已跑通；本源仍待补第二平台）
- [ ] L2 交互体验（**等 LOOMQ_LLM_* 实测后再勾**）
- [x] 工程与产品化（材料已备；终局随 commit）
- [ ] 自定义量子 RISC-V Bonus
- [ ] 新手引导与视觉叙事 Bonus

## L1 真机

每个有效真机平台计 5 分，最多两个平台。模拟器不计真机分。每个平台复制并填写一次下面的信息：

### 量旋（有效 — Bell）

```text
平台名称：量旋云 · 2比特核磁量子计算机
平台 job ID：G-260809-0018
运行时间：创建 2026-08-09 11:13:59 → started 11:14:30 → ended 11:15:32（UTC+8）
shots：结果页以投影概率为主展示（未在页头标明整数 shots；见 result JSON）
实际执行的 QASM：evidence/files/spinq-bell.qasm
平台返回的原始结果：evidence/files/spinq-bell-result.json
任务页截图：evidence/files/spinq-bell-hardware-result.png
模拟对照截图：evidence/files/spinq-bell-sim-preview.png
判定：有效（含 H、CNOT；实验柱主峰在 00/11）
```

### 草稿：量旋空电路（无效对照，勿计分）

```text
平台 job ID：G-260802-0004
实际执行的 QASM：evidence/files/spinq-G-260802-0004-empty.qasm
任务页截图：evidence/files/spinq-G-260802-0004-empty-circuit-NOT-valid-hw.png
判定：无效（无门）
```

### 待补：本源悟空（申请中）

```text
平台名称：本源悟空
平台 job ID：[待填写]
运行时间：[待填写]
shots：[待填写]
实际执行的 QASM：evidence/files/originq-bell.qasm
平台返回的原始结果：evidence/files/originq-bell-result.json
任务页截图：[选填]
```

申请进度：混合计算 / 悟空额度跟进中。华为机时可用于练习，**不替代**本源/量旋可溯源 job。

## L2 交互体验

材料草稿（有 Key 实测前不要勾总开关）：

```text
启动界面或 CLI 的命令：
  cd starter_kit && python tools/l2_chat_cli.py
  # 或一次性：PYTHONPATH=starter_kit python starter_kit/tools/l2_chat_cli.py '生成一个 3 比特 GHZ 态并全测量'
测试入口或页面地址：无（CLI）
适合现场体验的 3 个用户任务：
1. 生成 3 比特 GHZ 并全测量，确认回复含 OpenQASM 2.0
2. 粘贴一段错误的贝尔代码（大写门名/缺寄存器）请 Agent 修好
3. 问：15 比特、零排队，应选哪个后端（应出现能力表中的 simulator id）
截图或演示视频：[选填]
```

## 工程与产品化

```text
干净环境中的构建和启动命令：
  docker build -t loomq-submission starter_kit
  docker run --rm loomq-submission
  # 或本地：
  PYTHONPATH=starter_kit python starter_kit/evaluator.py --level declared --target spinq,braket,originq
架构说明：starter_kit/docs/ARCHITECTURE.md
目标用户和使用场景：不会三家 SDK 的开发者/产品同学；一份 QASM 或多后端 Agent，先模拟后真机
完整使用流程：README「一分钟上手」+ docs/FINAL_CHECKLIST.md
```

## 自定义量子 RISC-V Bonus

```text
指令编码规格：[未申报]
模拟器扩展实现：[未申报]
端到端测试命令：[未申报]
```

## 新手引导与视觉叙事 Bonus

```text
零基础首次运行指南：README「一分钟上手」+ QUANTUM_101.md
量子概念解释：QUANTUM_101.md
结果可视化：[待补]
错误恢复或无障碍引导：L2 CLI 错误回显 + agent 校验重试
```

## 提交规则

- 所有材料都要在截止前进入最终提交的 commit，工作人员不接受截止后补交。
- 外部视频可以用稳定只读链接，源码、原始结果和复现命令应保存在仓库中。
- 整个 fork commit 的归档包不得超过 100 MiB。
- 不要提交 API Key、Token、Cookie、个人身份信息或平台账户隐私。
- 如申报 L1 真机分，在最终提交 Issue 的 `Hardware evidence` 中填写 `starter_kit/evidence/README.md`。
