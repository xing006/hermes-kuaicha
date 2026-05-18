"""
Kuaicha Search MCP Server — MCP bridge for 同花顺快查企业数据引擎

Wraps the kuaicha_tool.mjs CLI (discover/call) as standard MCP tools,
auto-discovered by Hermes Agent's native MCP client.

Usage:
    python kuaicha_mcp_server.py

Requires:
    - Node.js 18+ (for kuaicha_tool.mjs)
    - KUAICHA_API_KEY env var, or config.txt in project root
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# ── paths ──────────────────────────────────────────────────────────────────

PROJECT_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_DIR / "scripts"
TOOL_MJS = SCRIPTS_DIR / "kuaicha_tool.mjs"
CONFIG_TXT = PROJECT_DIR / "config.txt"

# ── auth helpers ───────────────────────────────────────────────────────────

def _get_api_key() -> str | None:
    """Read KUAICHA_API_KEY from env or config.txt fallback."""
    # 1. Environment variable (passed via Hermes config.yaml mcp_servers.env)
    key = os.environ.get("KUAICHA_API_KEY")
    if key:
        return key.strip()

    # 2. config.txt at project root (CLI's native fallback location)
    if CONFIG_TXT.exists():
        m = re.search(r"^KUAICHA_API_KEY=(.+)$", CONFIG_TXT.read_text("utf-8"), re.M)
        if m:
            return m.group(1).strip()

    return None


def _run_node(args: list[str]) -> dict:
    """Run kuaicha_tool.mjs with given args, return parsed JSON result."""
    cmd = ["node", str(TOOL_MJS)] + args
    env = os.environ.copy()

    # Explicitly inject the API key so subprocess always has it
    api_key = _get_api_key()
    if api_key:
        env["KUAICHA_API_KEY"] = api_key

    cwd = str(SCRIPTS_DIR)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            cwd=cwd,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return {"_error": "请求超时（30s），请重试"}

    if result.returncode != 0:
        stderr = result.stderr.strip()
        return {"_error": f"CLI 错误 (exit={result.returncode}): {stderr or '无错误信息'}"}

    raw = result.stdout.strip()
    if not raw:
        return {"_error": "CLI 返回空结果"}

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        return {"_error": f"解析 JSON 失败: {e}"}


def _format_tool_param(param: dict) -> str:
    """Format a tool parameter for display in the MCP tool definition."""
    required = " (必填)" if param.get("required") else ""
    default = param.get("default", "")
    default_str = f" [默认: {default}]" if default else ""
    return f"{param.get('name')} ({param.get('type')}{required}{default_str}): {param.get('description', '')}"


# ── server ─────────────────────────────────────────────────────────────────

server = Server("kuaicha")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Register two MCP tools: discover and call."""
    return [
        types.Tool(
            name="kuaicha_discover_tools",
            description=(
                "发现快查企业数据平台的可用工具。通过自然语言描述你需要的企业数据能力，"
                "返回匹配的工具列表（含 tool_id、相似度、参数描述）。"
                "示例查询：'企业基本信息'、'企业股东信息'、'企业被执行人'、'企业商标信息'、'产业链企业筛选'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "能力描述（中文），如'企业基本信息查询'、'企业股东信息'、'企业经营异常'"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量上限，默认 10，最大 50",
                        "default": 10
                    },
                    "category_id": {
                        "type": "integer",
                        "description": "按分类筛选（可选），不传则搜索所有分类"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="kuaicha_call_tool",
            description=(
                "调用快查企业数据平台中已发现的工具，获取结构化企业数据。"
                "先通过 kuaicha_discover_tools 获取 tool_id，再用此工具调用。"
                "注意：企业查询参数优先使用 orgid > creditcode > corp_name；"
                "企业简称需先用模糊搜索工具获取全称或信用代码"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "tool_id": {
                        "type": "string",
                        "description": "工具 ID（从 kuaicha_discover_tools 返回的 tool_id 或 id 字段）"
                    },
                    "params": {
                        "type": "object",
                        "description": (
                            "工具参数（JSON 对象），根据 discover 返回的参数定义传入。"
                            "企业标识三选一优先顺序：orgid > creditcode > corp_name。"
                            "示例：{\"corp_name\": \"深圳市腾讯计算机系统有限公司\"} 或 "
                            "{\"creditcode\": \"91440300708461136T\"}"
                        )
                    }
                },
                "required": ["tool_id", "params"]
            }
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    """Handle tool execution."""
    if name == "kuaicha_discover_tools":
        query = arguments.get("query", "")
        if not query:
            return [types.TextContent(type="text", text="错误：query 参数不能为空")]

        args = ["discover", query]
        if arguments.get("limit"):
            args.extend(["--limit", str(arguments["limit"])])
        if arguments.get("category_id"):
            args.extend(["--category-id", str(arguments["category_id"])])

        data = _run_node(args)

        if "_error" in data:
            return [types.TextContent(type="text", text=data["_error"])]

        # Format the result nicely
        tools = data.get("tools", [])
        if not tools:
            return [types.TextContent(
                type="text",
                text=f"未找到匹配 '{query}' 的工具。请尝试换一种描述方式。"
            )]

        lines = [f"找到 {len(tools)} 个匹配工具（查询: '{query}'）：\n"]
        for i, tool in enumerate(tools, 1):
            name_t = tool.get("name", tool.get("tool_id", "未知"))
            tid = tool.get("tool_id", tool.get("id", ""))
            sim = tool.get("similarity", 0)
            desc = tool.get("description", "")
            params = tool.get("params", [])

            lines.append(f"  [{i}] {name_t}")
            lines.append(f"      tool_id: {tid}")
            lines.append(f"      相似度:   {sim}")
            lines.append(f"      描述:     {desc}")
            if params:
                lines.append(f"      参数:")
                for p in params:
                    lines.append(f"        - {_format_tool_param(p)}")
            lines.append("")

        return [types.TextContent(type="text", text="\n".join(lines))]

    elif name == "kuaicha_call_tool":
        tool_id = arguments.get("tool_id", "")
        params = arguments.get("params", {})

        if not tool_id:
            return [types.TextContent(type="text", text="错误：tool_id 参数不能为空")]

        # Build the CLI args
        args = ["call", tool_id, "--params", json.dumps(params, ensure_ascii=False)]
        data = _run_node(args)

        if "_error" in data:
            return [types.TextContent(type="text", text=data["_error"])]

        # Format result
        output = json.dumps(data, ensure_ascii=False, indent=2)
        return [types.TextContent(
            type="text",
            text=output + "\n\n数据来源于同花顺旗下快查企业数据引擎"
        )]

    else:
        return [types.TextContent(type="text", text=f"未知工具: {name}")]


# ── entrypoint ─────────────────────────────────────────────────────────────

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="kuaicha",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
