# LoomQ 人工评分证据

这份文件是人工评分材料的统一入口。请直接编辑它，只填写要申报的项目。截图、原始结果或图表统一放在 `starter_kit/evidence/files/`，也可以引用 `starter_kit/` 中已有的代码和文档。

证据包是可选的。没有申报某项人工分时，留空即可，不影响自动评分。

## 评委现场（30 秒）

```bash
# fork 根目录
./start_demo.sh
# → http://127.0.0.1:8765/
```

1. 第一屏：量旋真机 Bell `G-260809-0018`，柱状图主峰 **00/11**（归档回放，不排队）。  
   任务页：https://cloud.spinq.cn/circuitDesign/taskResult/61210  
2. 点「再看三枚硬币」或 `?demo=ghz3` / `?exp=ghz3`：GHZ `S-260810-0001`，主峰 **000/111**。  
   任务页：https://cloud.spinq.cn/circuitDesign/taskResult/61216  
3. L2 三项：`?demo=repair` 语法说明 · `?demo=backend` 15 比特零排队能力表 · 任务 1 GHZ 需 `LOOMQ_LLM_*` 调 Agent。  

**目标用户**：已有 OpenQASM/多 SDK 经验的产品与开发——一份中间层 + 可溯源真机 job，而不是再学三家方言。

## 公开态势对照（2026-08-20 傍晚，仅 Issue 回执 + evidence 头）

| 队 | 最后 Issue | L1–L3 | 真机叙事 | L2/产品公开面 |
|---|---|---|---|---|
| WilderNoTrack | #31 | 全勾 | **量旋+本源**，各 2 job | `python3 -m loomq web` :8787 |
| AphrixZjr | #32 | 全勾 | Origin+SpinQ 脚本化 | Docker compose + web 单测 |
| tale03 | #39 | 全勾 | 量旋+本源材料 | Flask `app.py` :5000 |
| AzureWynn | #45 | 全勾 | 量旋 2q+3q（G/S-260817） | CLI 为主，无 Web |
| **本队** | **#62** | **全勾** | **量旋 2q+3q 满 10 分**；本源维护中 | **`./start_demo.sh` 真机回放 Web** |
| hongwei-2026 | #50 | 全勾 | 量旋 1 job（G-260820-0003） | `loomq_web.py` :8765 |
| HpIahtcthocw | #27 | 全勾 | 量旋 2q+3q（同构） | 文档为主 |
| WayneYu1212 | #52 | 全勾 | evidence 空 | 待现场 |
| yiyuanrvk77 | #36 | 全勾 | 量旋 1 台 | `web_demo.py` 柱状图 |
| Jimmy658 | #38 | 全勾 | Issue 真机空 | L2 Agent |
| lyl2222 | #37 | 无 L3 | 量旋 1 job | `web_app.py` |

> 非官方排名。自动分取决于隐藏测例；人工分看真机 job、L2 现场、工程复现。**对照表对齐 #62（`71fc6ae`）；本 commit 含本源 chip 映射与维护重试记录，以截止前最后一次 `submission:accepted` Issue 为准。**

## 本包相对前 Issue (#42) 新增（须进 commit）

| 路径 | 作用 |
|---|---|
| `start_demo.sh` | fork 根目录一键启动 |
| `starter_kit/web/index.html` `style.css` `app.js` | 真机回放第一屏 + 三项任务 + 能力表 |
| `starter_kit/web/server.py` | `/api/experiments` 归档回放、`/api/simulate` 本地验算 |
| `starter_kit/tools/start_l2_web.sh` | 端口占用检测、自动开浏览器 |
| `starter_kit/evidence/files/l2-web-*.png` | L2 四项截图 |
| `starter_kit/evidence/README.md` | 本文件（评委入口 + 对照） |

## 提交前填写

把要申报项目的方框改成 `[x]`，并填写对应内容：

- [x] L1 真机（量旋双平台已齐：2q Bell + 3q GHZ；本源过审可加但不阻塞 10 分上限）
- [x] L2 交互体验（第一屏真机回放 + DeepSeek 三项任务：GHZ / 修 Bell / 15q 后端推荐）
- [x] 工程与产品化（材料已备；终局随 commit）
- [x] 自定义量子 RISC-V Bonus
- [x] 新手引导与视觉叙事 Bonus（README + QUANTUM_101 + 真机截图/投影图；无独立 RISC-V）

## L1 真机

每个有效真机平台计 5 分，最多两个平台。模拟器不计真机分。每个平台复制并填写一次下面的信息：

### 量旋（有效 — Bell）

```text
平台名称：量旋云 · 2比特核磁量子计算机
平台 job ID：G-260809-0018
任务页：https://cloud.spinq.cn/circuitDesign/taskResult/61210
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

### 量旋（有效 — GHZ-3 · 第二平台）

```text
平台名称：量旋云 · 3比特核磁量子计算机
平台 job ID：S-260810-0001
任务页：https://cloud.spinq.cn/circuitDesign/taskResult/61216
运行时间：created/ended 2026-08-10 11:30:16 → 11:32:42（UTC+8）
shots：结果页以投影概率为主展示（未在页头标明整数 shots；见 result JSON）
实际执行的 QASM：evidence/files/spinq-ghz3.qasm
平台返回的原始结果：evidence/files/spinq-ghz3-result.json
任务页截图：evidence/files/spinq-ghz3-hardware-result.png
模拟对照截图：evidence/files/spinq-ghz3-sim-preview.png
判定：有效（H + 两级 CNOT；实验主峰在 000/111，有 NISQ 泄漏）
```

### 待补：本源悟空（120s 机时窗口；云侧多次维护，尚未产生可溯源 job）

```text
平台名称：本源悟空（超导）
平台 job ID：[维护结束后填写]
运行时间：[维护结束后填写]
shots：256（计划）
实际执行的 QASM：evidence/files/originq-bell.qasm（与量旋 Bell 同语义）
平台返回的原始结果：evidence/files/originq-bell-result.json（维护失败记录，非有效真机分）
任务页截图：[维护成功后选填]
```

维护重试记录（均无 job_id，不申报真机分）：
- 2026-08-19、2026-08-20 17:30 (UTC+8)
- 2026-08-23 12:36 / 13:17 (UTC+8)：`LOOMQ_ORIGINQ_MODE=wukong`，`LOOMQ_ORIGINQ_CHIP=WK_C180`（pyqpanda 映射为 `chip_id=72` / `origin_72`），`TIMEOUT_SEC=120`，shots=256 → 仍返回 `Quantum computer under maintenance`

量旋双平台已满足人工真机 10 分上限；本源用于「两家中国云」答辩叙事，非第 11 分。
重试命令：`./starter_kit/tools/try_originq_bell.sh`（成功后更新本段 job ID，并开新 Final Issue）。

## L2 交互体验

```text
启动界面或 CLI 的命令：
  ./start_demo.sh
  # 或 cd starter_kit && ./tools/start_l2_web.sh
  # 浏览器 http://127.0.0.1:8765/
  # 真机回放无需 LOOMQ_LLM_*；Agent 三项需 starter_kit/.env
  cd starter_kit && python tools/l2_chat_cli.py
测试入口或页面地址：http://127.0.0.1:8765/
适合现场体验的 3 个用户任务：
1. 第一屏 Bell 归档（G-260809-0018）或 ?demo=ghz / 任务 1：GHZ 000/111 + Agent OpenQASM
2. ?demo=repair / 任务 2：三处 OpenQASM 语法坑 + Bell 真机对照
3. ?demo=backend / 任务 3：15 比特零排队 → 能力表高亮本地模拟器
本地实测（2026-08-20，DeepSeek deepseek-v4-flash）：
1. 通过 — GHZ 返回含 qreg q[3] 的 OpenQASM；页面可对照真机 S-260810-0001
2. 通过 — 修 Bell 补全头/寄存器/h/cx
3. 通过 — 回复含 braket_local_simulator 或 originq_local_simulator
截图或演示视频：
  - 启动 + Bell 真机回放：evidence/files/l2-web-ui-home.png
  - 任务 1 GHZ：evidence/files/l2-web-ghz3-demo.png
  - 任务 2 修 Bell：evidence/files/l2-web-bell-repair-demo.png
  - 任务 3 15q 后端：evidence/files/l2-web-backend-15q-demo.png
```

## 工程与产品化

```text
干净环境中的构建和启动命令：
  ./start_demo.sh
  cd starter_kit && docker build -t loomq-submission . && docker run --rm loomq-submission
  PYTHONPATH=starter_kit python starter_kit/evaluator.py --level declared --target spinq,braket,originq
架构说明：starter_kit/docs/ARCHITECTURE.md
目标用户和使用场景：跨平台开发/产品——统一 OpenQASM 中间层，先归档真机主峰再调 Agent；见上文「评委现场」
完整使用流程：starter_kit/README.md「一分钟上手」
```

## 自定义量子 RISC-V Bonus

```text
指令编码规格：starter_kit/docs/LOOMQ_QISA_V1.md
模拟器扩展实现：starter_kit/riscv_emulator.py（qinit/qh/qx/qcx/qmeas；assemble/decode；**load_machine_words 机器码闭环**，对齐主办方 Q3 方向 1；CUSTOM-0 opcode=0b0001011）
端到端测试命令：PYTHONPATH=starter_kit python starter_kit/tests/test_quantum_riscv_e2e.py（含 test_bell_via_machine_words_closed_loop）
```

## 新手引导与视觉叙事 Bonus

```text
零基础首次运行指南：README「一分钟上手」+ QUANTUM_101.md
量子概念解释：QUANTUM_101.md（Bell / 测量 / 多后端动机）
结果可视化：http://127.0.0.1:8765/ 第一屏真机/理想柱状图（Bell 00/11、GHZ 000/111）+ evidence/files 真机 JSON
错误恢复或无障碍引导：Web 白话报错（缺模型钥匙时仍可看真机）；agent 本地校验失败后最多重试 3 次；CLI 见 tools/l2_chat_cli.py
```

## 提交规则

- 所有材料都要在截止前进入最终提交的 commit，工作人员不接受截止后补交。
- 外部视频可以用稳定只读链接，源码、原始结果和复现命令应保存在仓库中。
- 整个 fork commit 的归档包不得超过 100 MiB。
- 不要提交 API Key、Token、Cookie、个人身份信息或平台账户隐私。
- 如申报 L1 真机分，在最终提交 Issue 的 `Hardware evidence` 中填写 `starter_kit/evidence/README.md`。
