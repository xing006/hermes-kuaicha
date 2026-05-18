# 安装指南

## 前置条件

- **Node.js 18+** — 快查 CLI 工具依赖
- **Python 3.10+** — MCP 桥接运行环境
- **Hermes Agent** — 已安装并可正常使用

## 安装步骤

### 1. 确认 Node.js 可用

```bash
node --version
# >= v18.0.0
```

### 2. 创建项目虚拟环境（可选，推荐）

```bash
cd e:/projects/hermes-kuaicha
python -m venv venv
source venv/Scripts/activate   # Windows (Git Bash)
# 或 venv\Scripts\activate     # Windows (PowerShell)
pip install mcp>=1.0.0
```

### 3. 配置 API Key

快查 CLI 按以下优先级读取 API Key：
1. 环境变量 `KUAICHA_API_KEY`
2. 脚本目录内 `config.txt`（格式: `KUAICHA_API_KEY=你的密钥`）
3. `~/.kuaicha/config` 文件

推荐方式——写入项目根目录 `config.txt`（Node.js CLI 原生读取位置）：

```bash
echo "KUAICHA_API_KEY=你的密钥" > e:/projects/hermes-kuaicha/config.txt
```

或导出为环境变量：

```bash
export KUAICHA_API_KEY="你的密钥"
```

### 4. 验证 CLI 可用

```bash
cd e:/projects/hermes-kuaicha/scripts
export KUAICHA_API_KEY="你的密钥"
node kuaicha_tool.mjs discover "企业基本信息" --limit 3
```

应返回工具列表。

### 5. 配置 Hermes MCP 服务器

编辑 `~/.hermes/config.yaml`，在 `mcp_servers` 下添加：

```yaml
mcp_servers:
  kuaicha:
    command: "e:/projects/hermes-kuaicha/run_mcp_server.bat"
    args: []
    env:
      KUAICHA_API_KEY: "你的密钥"
    timeout: 30
    connect_timeout: 15
```

> **关于路径**：`run_mcp_server.bat` 会自动定位自身所在目录，内部的 Python 路径和脚本路径都是相对路径。**如果移动项目目录**，只需改这一行中的路径。
>
> 内部原理：`.bat` 文件使用 `%~dp0` 获取自身所在目录，然后 `.\venv\Scripts\python.exe .\src\kuaicha_mcp_server.py` 自动解析到项目内路径。

### 6. 重启 Hermes

```bash
hermes restart
```

### 7. 验证 MCP 工具已注册

启动后检查日志或直接问：

> "有哪些 MCP 工具可用？"

应该能看到 `kuaicha_discover_tools` 和 `kuaicha_call_tool`。

## 验证安装

提问验证：

> "查一下深圳市腾讯计算机系统有限公司的基本信息"

助手应能自动走 discover → call 流程并返回结构化数据。

## 故障排查

| 问题 | 检查 |
|------|------|
| MCP 工具未出现 | 检查 `~/.hermes/config.yaml` 的 `mcp_servers` 缩进和路径 |
| 401 认证错误 | 检查 `KUAICHA_API_KEY` 是否正确，是否有拼写错误 |
| 连接超时 | 检查网络是否能访问快查 API（需大陆 IP） |
| Python 找不到模块 | 确认 `pip install mcp` 已在对应 Python 环境中执行 |
| Node.js 未找到 | 确认 node 在 PATH 中 |
