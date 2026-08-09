# 量旋真机：下次 10 分钟操作卡

空电路 `G-260802-0004` **不计分**。下面两条路任选其一拿到 **带 measure 的 Bell**。

## 路 A：网页（你上次用的界面）

1. 打开 https://cloud.spinq.cn → 新建线路（2 比特核磁即可）  
2. 网页编辑器粘贴下面全文（**不要写 `creg` / `measure`**：量旋网页常标红且不同步；全测量由平台在运行时做）：

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
h q[0];
cx q[0],q[1];
```

通过标准：左侧线路图出现 **H + CNOT**；下方模拟投影约 `00` / `11` 各一半。  
（赛题证据仍须保留任务页结果；有门的 Bell 即有效，不要交空 `qreg`。）

模板：`evidence/files/spinq-bell.TODO.qasm`  
3. 提交运行，等到「运行成功」  
4. 记录：任务号（如 `G-……`）、结束时间、shots、任务页 URL  
5. 导出/复制投影概率或 counts；截图任务页  
6. 保存到仓库：

```text
evidence/files/spinq-bell.qasm          # 实际提交的电路
evidence/files/spinq-bell-result.json   # 原始结果（可手填 schema，见下）
evidence/files/spinq-bell-screenshot.png
```

手填 `spinq-bell-result.json` 最小字段：

```json
{
  "backend": "spinq_cloud_qpu",
  "job_id": "G-xxxxxxxx",
  "shots": 1024,
  "counts": {"00": 480, "11": 520},
  "bit_order": "little",
  "timestamp": "2026-08-09T12:00:00Z",
  "meta": {"source": "spinq-web-ui", "task_url": "https://cloud.spinq.cn/circuitDesign/taskResult/xxxxx"}
}
```

7. 在 `evidence/README.md` 勾选 L1 真机并填平台段。

## 路 B：SpinQit 云后端（SSH 密钥）

文档：https://doc.spinq.cn/doc/spinqit/programming/backend/backend.html  

1. 在量旋云绑定 **SSH 公钥**  
2. `starter_kit/.env`：

```bash
LOOMQ_SPINQ_MODE=cloud
LOOMQ_SPINQ_USERNAME=你的用户名
LOOMQ_SPINQ_KEYFILE=/绝对路径/到/私钥
LOOMQ_SPINQ_PLATFORM=gemini_vp
```

3. 运行：

```bash
PYTHONPATH=starter_kit python starter_kit/tools/run_bell_evidence.py --platform spinq --shots 1024
```

脚本会拒绝本地 simulator 冒充真机（除非 `--allow-simulator` 干跑布局）。

## 无效自检

提交前打开任务页看线路图：必须能看到 H、CNOT 和测量，不能是空白两条线。
