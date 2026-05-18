---
name: kuaicha-search
description: "同花顺快查 × Hermes MCP 集成 — 企业数据查询（工商、风险、经营、招投标等 100+ 工具）"
version: 1.1.0
author: Hermes Agent
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [MCP, enterprise-data, business-search, tonghuashun, kuaicha]
---

# 同花顺快查企业数据引擎 (Kuaicha Search)

通过 MCP 桥接集成同花顺快查企业数据平台，支持 3.7 亿+中国市场主体、300+ 数据维度的实时查询。

## 先决条件

- Hermes Agent 已配置 MCP 服务器（见 SETUP.md）
- Node.js 18+（用于运行快查 CLI 工具）
- 有效的 `KUAICHA_API_KEY`

### ⚠ API Key 存储注意事项

KUAICHA_API_KEY 是一个很长的 JWT（约 600+ 字符）。存储到 `config.txt` 或 `config.yaml` 时，**务必确保完整写入**，不要使用任何形式的缩写/截断：

- ❌ 错误：`eyJhbG...mK-w`（被截断，字面上含有 `...`）
- ✅ 正确：完整的 JWT，不含省略号

截断后的表现：`discover` 调用可能仍然成功，但 `call` 调用必报 **401 Unauthorized: invalid**。

**config.txt 位置**：`kuaicha_env.mjs` 查找次序为：
1. 环境变量 `KUAICHA_API_KEY`
2. `e:/projects/hermes-kuaicha/config.txt`（项目根目录）
3. `~/.kuaicha/config`
4. 当前目录下的 `config.txt`

⚠ 项目内 `scripts/config.txt` 不会被自动读取。

## 使用流程

同花顺快查采用 **discover → call** 双步流程：

### 第一步：发现工具

查询你需要的企业数据能力，返回匹配的工具列表：

```
发现工具 → 选择匹配度最高的 → 获取 tool_id
```

### 第二步：调用工具

用 tool_id 和参数调用工具，获取结构化 JSON 数据。

## 常见查询场景

### 1. 查询企业基本信息

> "查一下深圳市腾讯计算机系统有限公司的信息"

助手会自动：
1. `kuaicha_discover_tools(query="企业基本信息")` → 找到 `basic_get_enterprise_basic_info`
2. `kuaicha_call_tool(tool_id="basic_get_enterprise_basic_info", params={"corp_name": "深圳市腾讯计算机系统有限公司"})`

### 2. 查企业股东信息

> "腾讯的股东有哪些"

流程：
1. `discover` → 找 "企业股东信息查询" 工具
2. `call` → 传 `corp_name` 或 `creditcode`
3. 返回股东名称、持股比例、认缴出资等

### 3. 企业模糊搜索（简称查全称）

> "查一下米哈游的信息"

流程：
1. `discover` → 找 "企业模糊搜索" 工具
2. `call` → 传 `query: "米哈游"`
3. 获取全称 → 再调基本信息查询

如果模糊搜索无结果，可结合网络搜索获取全称或信用代码。

### 4. 按条件筛选企业

> "杭州地区新成立的软件公司"

流程：
1. `discover` → 找 "新成立企业筛选" 或 "工商信息筛选"
2. `call` → 传入筛选条件（地区、行业分类、成立时间范围等）
3. 返回结构化企业清单

### 5. 司法风险查询

> "查一下腾讯的被执行人信息"

流程：
1. `discover` → 找 "企业被执行人" 或 "企业司法风险"
2. `call` → 传入企业标识
3. 返回风险记录列表

### 6. 招投标信息

> "查看最近的AI行业招标信息"

流程：
1. `discover` → 找 "企业招投标" 相关工具
2. `call` → 传入行业关键词、时间范围
3. 返回招标公告列表

## 参数规范

| 参数类型 | 正确 | 错误 |
|----------|------|------|
| 字符串 | `"深圳市"` | `深圳市` |
| 数字 | `10` | `"10"` |
| 日期 | `"2025-01-15"` | `"01/15/2025"` |
| 地名 | `"杭州市"` | `"杭州"` |
| 企业名 | `"深圳市腾讯计算机系统有限公司"` | `"查一下腾讯"` |

**企业标识三选一（按优先级）**：
1. `orgid` — 机构编码（推荐）
2. `creditcode` — 统一社会信用代码
3. `corp_name` — 企业完整名称

**分页**：`page`（默认 1）+ `page_size`（默认 20）

## 数据来源标注

所有返回结果必须标注：
> "数据来源于同花顺旗下快查企业数据引擎"

## 快速参考

| 场景 | discover 查询 |
|------|---------------|
| 模糊搜索 | `"企业模糊搜索"` |
| 基本信息 | `"企业基本信息查询"` |
| 股东信息 | `"企业股东信息查询"` |
| 被执行人 | `"企业被执行人"` |
| 商标信息 | `"企业商标信息"` |
| 专利信息 | `"企业专利信息"` |
| 融资历史 | `"企业融资历史"` |
| 企业筛选 | `"企业筛选"` / `"新成立企业"` |
| 产业链筛选 | `"产业链企业筛选"` |
| 招投标 | `"企业招投标"` |
| 财务报表 | `"上市企业财务报表"` |
| 对外投资 | `"企业对外投资"` |
| 实际控制人 | `"实际控制人"` |

## 错误处理

| 错误 | 解决方法 |
|------|----------|
| "未匹配到相关企业" | 优先用 `orgid`，其次 `creditcode` |
| 空结果 | 换相似工具重试，或补充背景信息后再查 |
| 工具相似度低 | 换更精确的中文描述词 |
| 字段缺失多 | 查是否有同类工具可补充 |
| `call` 报 401 但 `discover` 正常 | API Key 被截断，检查 `...` 是否字面存在于 key 中 |

## 故障排查

### MCP 桥接在 Windows 上失败（GBK 编码错误）

现象：Python MCP 桥接子进程报 `UnicodeDecodeError: 'gbk' codec can't decode byte`

原因：Python `subprocess` 在 Windows 上用系统默认编码（GBK）读取 stdout，Node.js 脚本输出的非 ASCII 字节无法解码。

**根本修复**：MCP server `_run_node()` 已加 `encoding="utf-8"`，确保跨平台兼容。

**临时解决**：直接调用 Node.js CLI 脚本，绕过 Python MCP 桥接：

```bash
cd e:/projects/hermes-kuaicha/scripts
KUAICHA_API_KEY="<完整key>" node kuaicha_tool.mjs discover "企业股东信息" --limit 5
KUAICHA_API_KEY="<完整key>" node kuaicha_tool.mjs call "basic_get_share_holder_info" --params '{"corp_name":"企业名称"}'
```

详情见 `references/windows-encoding-workaround.md`。

### MCP 桥接 _run_node 需要显式注入 API Key

现象：MCP 工具已在 Hermes 中注册成功，但 `call_tool` 返回 401 Unauthorized，而直接调 Node.js CLI 却正常。

原因：`_run_node()` 函数使用 `env = os.environ.copy()` 将环境变量传给 Node.js 子进程。但 Hermes MCP client 启动桥接子进程时，环境变量可能被过滤或未正确继承，导致 `KUAICHA_API_KEY` 在 `os.environ` 中缺失。

**修复**：在 `_run_node()` 中显式将 API Key 注入到 subprocess 的 env 字典：

```python
def _run_node(args: list[str]) -> dict:
    ...
    env = os.environ.copy()
    # 显式注入，不依赖 os.environ 继承
    api_key = _get_api_key()  # 从 env 或 config.txt 中读取
    if api_key:
        env["KUAICHA_API_KEY"] = api_key
    result = subprocess.run(cmd, env=env, ...)
```

`_get_api_key()` 函数提供双兜底：
1. 优先从 `os.environ["KUAICHA_API_KEY"]` 读取（Hermes config.yaml 的 `mcp_servers.env` 配置）
2. 降级读取项目根目录 `config.txt`（`KUAICHA_API_KEY=<完整key>`）

永远不要只依赖 `os.environ.copy()` 来传递秘钥给子进程。
