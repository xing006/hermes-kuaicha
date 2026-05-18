# 同花顺快查 × Hermes Agent 集成计划

## 目标

将同花顺快查（Kuaicha Search）企业数据引擎接入 Hermes Agent，使其 100+ 企业数据查询工具以原生 MCP 工具的形式直接在对话中可用。

## 方案

**MCP 桥接方案** — 写一个轻量 Python MCP Server，将 `kuaicha_tool.mjs` 的 `discover`/`call` CLI 包装为标准 MCP 工具，由 Hermes 原生 MCP Client 自动发现并注册。

## 架构

```
Hermes Agent
  └─ native-mcp client (自动发现)
       └─ mcp_kuaicha (python 桥接)
            └─ node kuaicha_tool.mjs  (CLI)
                 └─ 快查 API Gateway
                      └─ 3.7亿+企业数据
```

所有 MCP 工具以 `mcp_kuaicha_*` 前缀注册，Hermes 可直接调用。

---

## 步骤分解

### P0 — 核心链路（必须完成）

| # | 任务 | 说明 | 交付物 |
|---|------|------|--------|
| 1 | 注册获取 API Key | 访问 https://open.kuaicha365.com/skills/ 注册，获取 `KUAICHA_API_KEY` | API Key |
| 2 | 下载快查工具包 | 下载 `kuaicha_tool.mjs` + `kuaicha_client.mjs` + `kuaicha_env.mjs` | Node.js CLI 可用 |
| 3 | 验证 Node.js CLI 可用 | 运行 `node kuaicha_tool.mjs discover "企业基本信息" --limit 3` | CLI 正常 |
| 4 | 编写 MCP 桥接 Server | `src/kuaicha_mcp_server.py`，暴露两个 MCP 工具 | 桥接器 |
| 5 | 配置 Hermes config.yaml | 在 `mcp_servers` 下注册 kuaicha server | 配置生效 |
| 6 | 验证工具注入 | 重启 Hermes，确认工具列表中出现 `mcp_kuaicha_*` | 注册成功 |

### P1 — 可用性完善

| # | 任务 | 说明 |
|---|------|------|
| 7 | 编写 Hermes Skill | `skill/SKILL.md`，封装 discover→call 最佳实践、参数规范、来源标注 |
| 8 | 端到端测试 | 真实场景测试：查企业、查股东、筛选 |
| 9 | 错误处理 | 测试空结果、密钥无效、网络超时，桥接器加友好错误信息 |
| 10 | 修复/完善 | 根据测试反馈调整 |

### P2 — 增强（后续）

| # | 任务 | 说明 |
|---|------|------|
| 11 | 批量查询支持 | 企业名单批量补全 |
| 12 | 高频场景独立工具 | 产业链筛选、资质筛选等 |

---

## 项目结构

```
e:/projects/hermes-kuaicha/
├── src/
│   ├── kuaicha_mcp_server.py     (新建 — MCP 桥接)
│   └── requirements.txt          (新建 — 依赖)
├── scripts/
│   ├── kuaicha_tool.mjs          (下载)
│   ├── kuaicha_client.mjs        (下载)
│   └── kuaicha_env.mjs           (下载)
├── docs/
│   ├── SETUP.md                  (安装指南)
│   └── USAGE.md                  (使用说明)
├── skill/
│   └── SKILL.md                  (Hermes Skill)
├── plans/
│   └── 01-integration-plan.md    (本计划)
├── README.md                     (项目概览 + "装回"指南)
├── config.txt                    (API 密钥，不提交)
└── .gitignore
```

**关键原则**：
- ✅ 不碰 Hermes 核心代码 — MCP 桥接是独立子进程，通过 stdio 通信
- ✅ 配置只改用户级 `~/.hermes/config.yaml`
- ✅ Skill 放用户级 `~/.hermes/skills/`
- ✅ 所有代码和文档在项目目录内，README 包含"装回"指南

## 风险 & 权衡

| 风险 | 缓解 |
|------|------|
| Node.js 未安装 | 前置检查，提示安装 |
| API Key 内测限 1000 次 | 测试够用，生产需付费 |
| Python→JS 进程开销 | ~50ms，可忽略 |
| 工具包远程更新 | MCP bridge 的 discover 动态查询，自动生效 |
| 仅限大陆 IP | 本机无问题 |

## 记录：已踩过的坑

- `config.txt` 必须放**项目根目录**，不是 `scripts/` 下。`kuaicha_env.mjs` 的 `getLocalConfigPath()` 从 `scripts/` 往一级 `..` 找 `config.txt`，即 `scripts/../config.txt` = 项目根目录
- MCP 桥接的 `_run_node()` 需显式 `env["KUAICHA_API_KEY"] = key`，不能只靠 `os.environ.copy()`，因为 Hermes MCP client 的 env 传递可能有过滤
- `README.md`、`docs/SETUP.md`、`src/kuaicha_mcp_server.py` 三个位置的 config.txt 路径需同步

## 验证标准

1. 对话输入："查一下深圳市腾讯计算机系统有限公司的股东信息"
2. 助手自动 discover→call 流程
3. 返回结构化股东数据，标注来源
4. 结果准确
