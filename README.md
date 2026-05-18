# 同花顺快查 × Hermes Agent MCP 桥接
# Kuaicha Search MCP Bridge for Hermes Agent

将同花顺快查企业数据引擎集成到 Hermes Agent，提供 100+ 企业数据查询工具的 MCP 原生访问能力。
*Integrate Kuaicha (同花顺) enterprise data engine into Hermes Agent via MCP bridge — 100+ business data tools as native MCP tools.*

[中文] | [English]

---

## 能力 / Capabilities

| 中文 | English |
|------|---------|
| **3.7 亿+ 中国市场主体**覆盖 | **370M+** Chinese business entities |
| **300+ 数据维度**（工商、司法、经营、招投标等） | **300+** data dimensions (registration, legal, risk, bidding, IP, etc.) |
| **毫秒级响应** | **Sub-200ms** average response |
| **自然语言查询**：discover → call 双步流程 | **Natural language query**: discover → call two-step workflow |

## 架构 / Architecture

```
Hermes Agent
  └─ native-mcp client
       └─ run_mcp_server.bat (self-locating)
            └─ venv/Scripts/python.exe
                 └─ src/kuaicha_mcp_server.py (MCP bridge)
                      └─ subprocess: node scripts/kuaicha_tool.mjs
                           └─ Kuaicha API Gateway
                                └─ 370M+ business entities
```

**Two MCP tools registered:**
- `kuaicha_discover_tools` — Discover available query tools by natural language
- `kuaicha_call_tool` — Call a discovered tool with structured params

---

## 快速开始 / Quick Start

### Prerequisites

- **Hermes Agent** — with MCP support enabled
- **Node.js 18+** — for the kuaicha CLI tools
- **Python 3.10+** — for the MCP bridge
- **Kuaicha API Key** — register at [open.kuaicha365.com/skills/](https://open.kuaicha365.com/skills/)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/xing006/hermes-kuaicha.git
cd hermes-kuaicha

# 2. Install Python dependencies
pip install mcp>=1.0.0

# 3. Configure API key
echo "KUAICHA_API_KEY=your-key-here" > config.txt

# 4. Configure Hermes — edit ~/.hermes/config.yaml:
#
# mcp_servers:
#   kuaicha:
#     command: "/path/to/hermes-kuaicha/run_mcp_server.bat"
#     args: []
#     env:
#       KUAICHA_API_KEY: "your-key-here"
#     timeout: 30
#     connect_timeout: 15

# 5. Restart Hermes and open a new session
```

### Deploy (for production use)

This project follows a **dev → deploy** separation:

| Environment | Path | Purpose |
|-------------|------|---------|
| Development | `hermes-kuaicha/` (cloned directory) | Code, test, docs |
| Deployment | `~/AppData/Local/hermes/tools/kuaicha/` | Hermes runtime reference |

```bash
# Deploy to Hermes tools directory
cp -r src/ ~/AppData/Local/hermes/tools/kuaicha/src/
cp -r scripts/ ~/AppData/Local/hermes/tools/kuaicha/scripts/
cp config.txt ~/AppData/Local/hermes/tools/kuaicha/
cp run_mcp_server.bat ~/AppData/Local/hermes/tools/kuaicha/

# Deploy skill
mkdir -p ~/AppData/Local/hermes/skills/kuaicha-search
cp skill/SKILL.md ~/AppData/Local/hermes/skills/kuaicha-search/

# Create venv (first time only)
python -m venv ~/AppData/Local/hermes/tools/kuaicha/venv
~/AppData/Local/hermes/tools/kuaicha/venv/Scripts/pip install mcp
```

Then point `~/.hermes/config.yaml` to the deployed path:
```yaml
command: "C:/Users/<you>/AppData/Local/hermes/tools/kuaicha/run_mcp_server.bat"
```

---

## 使用 / Usage

### Query Examples

**"查一下腾讯的股东信息"** (Find Tencent's shareholders)

The assistant automatically:
1. `discover(query="企业股东信息查询")` → finds `basic_get_share_holder_info`
2. `call(tool_id="basic_get_share_holder_info", params={"corp_name": "深圳市腾讯计算机系统有限公司"})`
3. Returns structured shareholder data (name, share ratio, capital contribution)

**"杭州新成立的软件公司有哪些"** (New software companies in Hangzhou)

1. `discover(query="按工商信息筛选企业")` → finds `filter_get_enterprise_search_by_commercial`
2. `call(tool_id="...", params={"city": "杭州市", "industry_classi_name": "软件和信息技术服务业", "established_date_start": "2025-01-01"})`

**"查一下阿里的被执行人信息"** (Check Alibaba's enforcement records)

1. `discover(query="企业被执行人")` → finds judicial risk tool
2. Call with company identifier → returns risk records

### Data Source Attribution

All query results **must** include this attribution:
> "数据来源于同花顺旗下快查企业数据引擎"
> *Data provided by Kuaicha (同花顺) enterprise data engine*

---

## 项目结构 / Project Structure

```
hermes-kuaicha/
├── run_mcp_server.bat        # Self-locating startup script (Windows)
├── src/
│   ├── kuaicha_mcp_server.py # MCP bridge server (Python)
│   └── requirements.txt      # Python dependencies
├── scripts/
│   ├── kuaicha_tool.mjs      # Kuaicha CLI entry point (Node.js)
│   ├── kuaicha_client.mjs    # HTTP client
│   └── kuaicha_env.mjs       # Environment config (API key resolution)
├── docs/
│   ├── SETUP.md              # Installation guide (CN)
│   └── USAGE.md              # Usage guide (CN)
├── skill/
│   └── SKILL.md              # Hermes Agent skill definition
├── plans/
│   └── 01-integration-plan.md # Integration plan & pitfalls
├── .gitignore
└── README.md                 # This file
```

---

## 已知坑点 / Known Pitfalls

### 1. config.txt location
`kuaicha_env.mjs` looks for `config.txt` one directory up from `scripts/` (project root). Do NOT put it in `scripts/`.

### 2. API Key must be complete
The key is a ~600-char JWT. Truncation (even `...`) causes `call` to fail with 401.

### 3. Windows GBK encoding
On Windows, Python subprocess may use GBK to decode Node.js output. Fixed by `encoding="utf-8"` in `_run_node()`.

### 4. API Key injection
MCP bridge explicitly injects `KUAICHA_API_KEY` into subprocess env — don't rely on `os.environ.copy()` alone.

---

## 设计原则 / Design Principles

- ✅ **No Hermes core modification** — MCP bridge runs as an independent subprocess
- ✅ **Standard MCP protocol** — Compatible with any MCP-supporting AI agent
- ✅ **Zero-intrusion config** — Only modifies user-level `~/.hermes/config.yaml`
- ✅ **Dev/Deploy separation** — Development workspace independent from runtime

## 许可证 / License

MIT
