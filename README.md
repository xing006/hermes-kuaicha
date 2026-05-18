<p align="center">
  <img src="assets/banner.png" alt="Kuaicha MCP Bridge" width="100%">
</p>

# Kuaicha MCP Bridge for Hermes Agent

<p align="center">
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文"></a>
  <a href="https://github.com/xing006/hermes-kuaicha/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"></a>
  <a href="https://github.com/xing006/hermes-kuaicha"><img src="https://img.shields.io/badge/GitHub-hermes--kuaicha-181717?style=for-the-badge&logo=github" alt="GitHub"></a>
</p>

**MCP bridge that connects Kuaicha (同花顺) enterprise data engine to Hermes Agent.** Provides 100+ business data query tools as native MCP tools — query 370M+ Chinese business entities across 300+ data dimensions.

---

## Features

| Capability | Description |
|------------|-------------|
| **370M+ entities** | Covers Chinese companies, self-employed businesses, social organizations, government agencies |
| **300+ data dimensions** | Registration, legal, risk, operations, bidding, IP, finance, news |
| **Sub-200ms response** | Real-time queries via optimized API gateway |
| **Natural language query** | `discover` → `call` two-step workflow |
| **Zero Hermes core modification** | Runs as independent MCP subprocess |

## Architecture

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
- `kuaicha_discover_tools` — Discover available query tools by natural language description
- `kuaicha_call_tool` — Call a discovered tool with structured parameters

---

## Quick Start

### Prerequisites

- [Hermes Agent](https://hermes-agent.nousresearch.com) installed
- **Node.js 18+** — for the kuaicha CLI tools
- **Python 3.10+** — for the MCP bridge
- **Kuaicha API Key** — register at [open.kuaicha365.com/skills/](https://open.kuaicha365.com/skills/)

### Install

```bash
# Clone the repo
git clone https://github.com/xing006/hermes-kuaicha.git
cd hermes-kuaicha

# Install Python dependencies
pip install mcp>=1.0.0

# Configure API key
echo "KUAICHA_API_KEY=your-key-here" > config.txt

# Deploy to Hermes tools directory
cp -r src/ ~/AppData/Local/hermes/tools/kuaicha/src/
cp -r scripts/ ~/AppData/Local/hermes/tools/kuaicha/scripts/
cp config.txt ~/AppData/Local/hermes/tools/kuaicha/
cp run_mcp_server.bat ~/AppData/Local/hermes/tools/kuaicha/

# Create venv (first time only)
python -m venv ~/AppData/Local/hermes/tools/kuaicha/venv
~/AppData/Local/hermes/tools/kuaicha/venv/Scripts/pip install mcp

# Deploy skill
mkdir -p ~/AppData/Local/hermes/skills/kuaicha-search
cp skill/SKILL.md ~/AppData/Local/hermes/skills/kuaicha-search/
```

### Configure Hermes

Edit `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  kuaicha:
    command: "C:/Users/<you>/AppData/Local/hermes/tools/kuaicha/run_mcp_server.bat"
    args: []
    env:
      KUAICHA_API_KEY: "your-key-here"
    timeout: 30
    connect_timeout: 15
```

Restart Hermes and open a new session — the MCP tools will be auto-discovered.

---

## Usage

The data engine uses a **discover → call** two-step workflow:

### 1. Discover tools

Ask for the capability you need:

> "Find shareholder information for Tencent"

The assistant will call `kuaicha_discover_tools(query="企业股东信息查询")` to find matching tools.

### 2. Call the tool

With the `tool_id` from discovery, structured data is returned:

> `kuaicha_call_tool(tool_id="basic_get_share_holder_info", params={"corp_name": "深圳市腾讯计算机系统有限公司"})`

### Supported Query Types

| Category | Examples |
|----------|----------|
| **Company search** | Fuzzy name search, basic info, shareholders, investments |
| **Registration data** | Legal person, registered capital, establishment date, industry classification |
| **Risk & legal** | Enforcement records, dishonest persons, court announcements, administrative penalties |
| **Operations** | Bidding history, financing rounds, recruitment, supply chain |
| **IP & credentials** | Trademarks, patents, software copyrights, certifications |
| **Financial** | Balance sheet, income statement, cash flow (listed companies) |
| **Filtering** | By region, industry chain, qualification, establishment date |
| **News & announcements** | Enterprise news, public notices |

### Data Source Attribution

All query results **must** include:
> Data provided by Kuaicha (同花顺) enterprise data engine

---

## Project Structure

```
hermes-kuaicha/
├── run_mcp_server.bat        # Self-locating startup script (Windows)
├── src/
│   ├── kuaicha_mcp_server.py # MCP bridge server (Python)
│   └── requirements.txt      # Python dependencies
├── scripts/
│   ├── kuaicha_tool.mjs      # Kuaicha CLI entry point (Node.js)
│   ├── kuaicha_client.mjs    # HTTP client
│   └── kuaicha_env.mjs       # Environment config
├── docs/
│   ├── SETUP.md              # Installation guide (Chinese)
│   └── USAGE.md              # Usage guide (Chinese)
├── skill/
│   └── SKILL.md              # Hermes Agent skill definition
├── plans/
│   └── 01-integration-plan.md # Integration plan & pitfalls
├── .gitignore
└── README.md                 # This file (English)
└── README.zh-CN.md           # Chinese version
```

---

## Known Pitfalls

| Pitfall | Solution |
|---------|----------|
| **config.txt location** | Must be in project **root** (not `scripts/`). `kuaicha_env.mjs` resolves one directory up from its own location. |
| **Truncated API key** | The ~600-char JWT must be complete. Literal `...` in the key causes `call` to return 401. |
| **Windows GBK encoding** | Python subprocess on Windows may decode Node.js stdout as GBK. Fixed by `encoding="utf-8"` in `_run_node()`. |
| **Env var filtering** | MCP bridge explicitly injects `KUAICHA_API_KEY` into subprocess env — `os.environ.copy()` alone may miss it. |

---

## License

MIT
