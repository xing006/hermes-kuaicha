<p align="center">
  <img src="assets/banner.png" alt="Kuaicha MCP Bridge" width="100%">
</p>

# Kuaicha MCP Bridge × Hermes Agent

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/Lang-English-lightgrey?style=for-the-badge" alt="English"></a>
  <a href="https://github.com/xing006/hermes-kuaicha/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"></a>
  <a href="https://github.com/xing006/hermes-kuaicha"><img src="https://img.shields.io/badge/GitHub-hermes--kuaicha-181717?style=for-the-badge&logo=github" alt="GitHub"></a>
</p>

**将同花顺快查企业数据引擎通过 MCP 桥接集成到 Hermes Agent。** 提供 100+ 企业数据查询工具作为原生 MCP 工具——覆盖 3.7 亿+中国市场主体，300+ 数据维度。

---

## 能力

| 能力 | 说明 |
|------|------|
| **3.7 亿+ 市场主体** | 企业、个体工商户、社会组织、事业单位等 |
| **300+ 数据维度** | 工商、司法、经营、招投标、知识产权、财务、舆情 |
| **毫秒级响应** | 高性能 API 网关，平均响应 <200ms |
| **自然语言查询** | discover → call 双步流程，无需记 API |
| **不碰 Hermes 核心** | 独立 MCP 子进程运行，零侵入 |

## 架构

```
Hermes Agent
  └─ native-mcp client（自动发现工具）
       └─ run_mcp_server.bat（自定位启动脚本）
            └─ venv/Scripts/python.exe
                 └─ src/kuaicha_mcp_server.py（MCP 桥接）
                      └─ 子进程: node scripts/kuaicha_tool.mjs
                           └─ 快查 API 网关
                                └─ 3.7 亿+ 企业数据
```

**注册两个 MCP 工具：**
- `kuaicha_discover_tools` — 通过自然语言发现可用查询工具
- `kuaicha_call_tool` — 调用已发现的工具获取结构化数据

---

## 快速开始

### 前置条件

- 已安装 [Hermes Agent](https://hermes-agent.nousresearch.com)
- **Node.js 18+** — 运行快查 CLI 工具
- **Python 3.10+** — 运行 MCP 桥接
- **快查 API Key** — 在 [open.kuaicha365.com/skills/](https://open.kuaicha365.com/skills/) 注册获取（内测送 1000 次）

### 安装

```bash
# 克隆仓库
git clone https://github.com/xing006/hermes-kuaicha.git
cd hermes-kuaicha

# 安装 Python 依赖
pip install mcp>=1.0.0

# 配置 API Key（放项目根目录！kuaicha_env.mjs 查找的是 scripts/../config.txt）
echo "KUAICHA_API_KEY=你的密钥" > config.txt

# 部署到 Hermes 工具目录
cp -r src/ ~/AppData/Local/hermes/tools/kuaicha/src/
cp -r scripts/ ~/AppData/Local/hermes/tools/kuaicha/scripts/
cp config.txt ~/AppData/Local/hermes/tools/kuaicha/
cp run_mcp_server.bat ~/AppData/Local/hermes/tools/kuaicha/

# 创建虚拟环境（首次）
python -m venv ~/AppData/Local/hermes/tools/kuaicha/venv
~/AppData/Local/hermes/tools/kuaicha/venv/Scripts/pip install mcp

# 部署 Skill
mkdir -p ~/AppData/Local/hermes/skills/kuaicha-search
cp skill/SKILL.md ~/AppData/Local/hermes/skills/kuaicha-search/
```

### 配置 Hermes

编辑 `~/.hermes/config.yaml`：

```yaml
mcp_servers:
  kuaicha:
    command: "C:/Users/<你的用户名>/AppData/Local/hermes/tools/kuaicha/run_mcp_server.bat"
    args: []
    env:
      KUAICHA_API_KEY: "你的密钥"
    timeout: 30
    connect_timeout: 15
```

重启 Hermes，新会话中 MCP 工具自动注册。

---

## 使用示例

### 1. 查企业基本信息

> "查一下深圳市腾讯计算机系统有限公司的信息"

助手自动：
1. `kuaicha_discover_tools(query="企业基本信息")` → 找到 `basic_get_enterprise_basic_info`
2. `kuaicha_call_tool(tool_id="...", params={"corp_name": "深圳市腾讯计算机系统有限公司"})`
3. 返回法人、注册资本、经营范围等

### 2. 查股东信息

> "腾讯的股东有哪些"

返回：马化腾 54.29%、张志东 22.86%、陈一丹 11.43%、许晨晔 11.43%

### 3. 按条件筛选企业

> "杭州新成立的软件公司"

需要精确行业分类名 `"软件和信息技术服务业"`（非模糊搜索），组合 `city=杭州市` + `established_date_start=2025-01-01`。

### 4. 简称查全称（模糊搜索）

> "查一下米哈游的信息"

先 `discover("企业模糊搜索")` 获取全称或信用代码，再调基本信息查询。

### 5. 司法风险

> "查一下阿里的被执行人信息"

### 数据来源标注

所有查询结果**必须**标注：
> 数据来源于同花顺旗下快查企业数据引擎

---

## 项目结构

```
hermes-kuaicha/
├── run_mcp_server.bat        # 自定位启动脚本（Windows）
├── src/
│   ├── kuaicha_mcp_server.py # MCP 桥接服务（Python）
│   └── requirements.txt      # Python 依赖
├── scripts/
│   ├── kuaicha_tool.mjs      # 快查 CLI 入口（Node.js）
│   ├── kuaicha_client.mjs    # HTTP 客户端
│   └── kuaicha_env.mjs       # 环境配置
├── docs/
│   ├── SETUP.md              # 安装指南
│   └── USAGE.md              # 使用说明
├── skill/
│   └── SKILL.md              # Hermes Skill 定义
├── plans/
│   └── 01-integration-plan.md # 集成计划 & 踩坑记录
├── .gitignore
├── README.md                 # 英文版
└── README.zh-CN.md           # 本文件（中文版）
```

---

## 已知坑点

| 坑点 | 解决方法 |
|------|----------|
| **config.txt 位置** | 必须放**项目根目录**，不是 `scripts/`。`kuaicha_env.mjs` 从自身目录往上一级找 `../config.txt`。 |
| **API Key 被截断** | 密钥是 ~600 字符的 JWT。字面出现 `...` 会导致 `call` 报 401，`discover` 可能正常。 |
| **Windows GBK 编码** | Python `subprocess` 在 Windows 上会用 GBK 解码 Node.js 输出。已在 `_run_node()` 中加 `encoding="utf-8"` 修复。 |
| **环境变量过滤** | MCP 桥接已显式注入 `KUAICHA_API_KEY` 到子进程 env——不能只依赖 `os.environ.copy()`。 |

---

## 许可证

MIT
