# 终局提交清单（私有备忘，截止前最后一次 Issue）

截止：**2026-08-25 12:00 UTC+8**。公开 fork 平时尽量少动；终局一次覆盖。

## 生效策略

- 资格件：已受理 Issue #9（仅 L1）— 先保留。  
- 终局件：约 8/22–8/24 推公开 `submission` → 新建最终提交 Issue。  
- 只认最后一次 `submission:accepted`。

## 建议终局申报

| 项 | 条件 |
|---|---|
| L1 | 三后端本地 + Docker 自检绿（已有私有验证记录） |
| L3 | `compile_hybrid` 已接；测试 7/7 |
| L2 | 仅当 DeepSeek/兼容 Key **真调用过公开样例** 后再勾 |
| 真机 | 每平台：**有门 + measure 的 Bell**，可溯源 job_id + 原始结果 JSON |

## `submission.yaml`（勾 L2 时必须改）

```yaml
levels:
  l1: true
  l2: true   # 未实测前保持 false
  l3: true
network:
  required_for_l1: false
  required_for_l2: true   # 勾 L2 时必为 true（否则官方 L2 case 会全挂）
  allowed_hosts: []       # 正式评测由组委会注入模型；本地调试用环境变量
```

路径必须是 **`starter_kit/`**（不要再用旧 `starter-kit/`）。

## 终局前自检命令

```bash
# 契约（按声明 Level）
PYTHONPATH=starter_kit python starter_kit/evaluator.py --level declared --target spinq,braket,originq

# L3
PYTHONPATH=starter_kit python starter_kit/tests/test_hybrid.py

# L2 单测（无 Key）
PYTHONPATH=starter_kit python starter_kit/tests/test_agent_unit.py

# L2 真调用（需 .env）
PYTHONPATH=starter_kit python starter_kit/tools/l2_chat_cli.py '生成一个 3 比特 GHZ 态并全测量'

# 预检
python3 starter_kit/prepare_submission.py --team-id jessicaruan6688-byte
```

## 真机证据（重要）

操作卡：[`SPINQ_HARDWARE.md`](SPINQ_HARDWARE.md)（网页 Bell / SSH 云后端）。

### 无效例（勿再交这类）

量旋 `G-260802-0004` / 页面 `taskResult/61136`：只有 `qreg`，**无门、无 measure** → 只证明账号连通，**不计 LoomQ 真机分**。

### 有效最低标准

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q -> c;
```

- 任务成功结束  
- 保存：电路 QASM、平台原始结果、job_id、时间（含时区）、shots  
- 截图可作辅证，不能代替 job_id + 原始结果  

助手脚本（云模式可用时）：

```bash
PYTHONPATH=starter_kit python starter_kit/tools/run_bell_evidence.py --platform originq
# 或 spinq（待 SDK 真机路径打通后）
```

### 关于华为云机时

赛题真机分锚定 **量旋 / 本源（及相关竞赛后端）可溯源 job**。华为机时可用于练手，**一般不能替代** LoomQ 证据里的平台 job_id。本源「郑州+悟空」仍应继续跟申请。

## 证据包勾选前核对

- [ ] `evidence/README.md` 对应项改成 `[x]` 且字段填满  
- [ ] `evidence/files/` 内路径真实存在且进了终局 commit  
- [ ] 无 API Key / Cookie  
- [ ] 工程叙事指向 `docs/ARCHITECTURE.md` + README 复现命令  
- [ ] L2 体验写明 CLI 启动命令与 3 个现场任务  

## 泄露控制

终局前：不把完整 L2/L3 推到公开默认分支展示进度。  
终局时：一次打包推送 + 一个 Issue。
