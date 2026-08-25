# 线上评委核验清单

正式提交以截止前最后一次 `submission:accepted` Issue 为准。  
评委核验只依赖：**公开 fork 归档 commit + 本仓 evidence + 云平台可点链接**。参赛队无需额外线下演示。

## 提交入口

- Fork：https://github.com/jessicaruan6688-byte/LoomQ-2026-Jessica
- 证据总入口：`starter_kit/evidence/README.md`
- 权威 Issue：以 GitHub 上该队最后一次 `submission:accepted` 为准

## 零启动核验（纯线上点开即可）

| 项 | 线上怎么核 |
|---|---|
| 量旋 Bell | https://cloud.spinq.cn/circuitDesign/taskResult/61210 · 仓内 `evidence/files/spinq-bell-*` |
| 量旋 GHZ | https://cloud.spinq.cn/circuitDesign/taskResult/61216 · 仓内 `evidence/files/spinq-ghz3-*` |
| 本源 Bell | job `724E511297B861472AA2441F90F3D5E6` · 打开 `originq-bell-result.json`（counts 00/11）与 `originq-bell-rest-detail.json`（`taskState=3`，chipId=180，物理比特 `[157,166]`） |
| L2 截图 | 仓内 `evidence/files/l2-web-*.png`（首页 / GHZ / 修 Bell / 15q 后端） |
| 产品为谁 | 见 `evidence/README.md` 入口第一段 |

## L2 Demo（评委从归档 commit 复现时）

官方线上评测会拉取归档包；若需交互体验，在归档根目录：

```bash
./start_demo.sh
# http://127.0.0.1:8765/
# http://127.0.0.1:8765/?demo=ghz3
# http://127.0.0.1:8765/?demo=repair
# http://127.0.0.1:8765/?demo=backend
```

| 步骤 | URL | 期望现象 |
|---|---|---|
| 首页 | `/` | Bell 归档柱状图主峰 **00/11**；job `G-260809-0018`；lede 提及本源双云 |
| GHZ | `?demo=ghz3` | 主峰 **000/111**；job `S-260810-0001` |
| 修电路 | `?demo=repair` | OpenQASM 语法说明 + Bell 对照 |
| 选后端 | `?demo=backend` | 15 比特零排队能力表，不排队、不烧机时 |

真机回放不扣机时；Agent 三项需评测环境注入的 `LOOMQ_LLM_*`。

## 本源适配三点（工程）

1. **chipId=180**：`WK_C180` 必须映射到 180；误用退役 72 会假性「维护中」。
2. **不要 `set_configure(72,72)`**：会清掉 `init_qvm` 状态。
3. **SDK 轮询失败 ≠ 任务失败**：先存 job id，用 REST `getTaskDetail` / 控制台取结果；禁止因超时重交。

## 产品一句话

给会写软件、但不想同时学 SpinQ / OriginIR / Braket 三套方言的人——先看可溯源真机主峰，再用自然语言改电路。
