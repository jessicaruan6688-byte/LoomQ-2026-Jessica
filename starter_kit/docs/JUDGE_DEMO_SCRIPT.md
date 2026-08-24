# 截止前口述与 Demo（私有备忘）

截止：**2026-08-25 12:00 UTC+8**。正式提交以最后一次 `submission:accepted` Issue 为准。

## 当前正式版

- Issue：https://github.com/QAIDAO/LoomQ-2026/issues/109 （若后续又开新 Issue，以更新者为准）
- Fork：https://github.com/jessicaruan6688-byte/LoomQ-2026-Jessica
- 证据：`starter_kit/evidence/README.md`

## Demo（不烧真机）

```bash
cd "/Users/jessica/Documents/2026projects/0825量子赛道/LoomQ-2026-Jessica 0820版"
./start_demo.sh
# http://127.0.0.1:8765/
```

30 秒路径见 `evidence/README.md`「评委现场」。

## 3 分钟走查口述

1. **产品**：给会写代码、但不想学三家量子方言的人；一键看真机主峰，再说人话改电路。  
2. **L1**：OpenQASM → 统一 IR → SpinQ / OriginIR / Braket；不是三套复制粘贴。  
3. **真机**：量旋 Bell + GHZ 两个 job；本源 Bell `724E511297B861472AA2441F90F3D5E6`，**chipId=180**（72 是退役资源，会假维护）。  
4. **L2**：`agent_chat` + Web；生成 / 修复 / 选后端；正式评测用组委会模型。  
5. **L3 / Bonus**：Hybrid-QASM → RISC-V；QISA 机器码闭环可测。  

## 真机已停

- `.env`：`LOOMQ_ORIGINQ_MODE=local`、`LOOMQ_SPINQ_MODE=local`
- 不要再跑 `try_originq_bell.sh`
