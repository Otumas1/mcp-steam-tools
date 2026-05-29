import asyncio
import os
from mcp.server.fastmcp import FastMCP
import uvicorn

# 创建 MCP 服务器
mcp = FastMCP("CS:GO 估价工具")

# ---------- 工具1：查 Steam 价格 ----------
@mcp.tool()
async def steam_price(market_hash_name: str) -> dict:
    """
    查询指定饰品在 Steam 市场上的最低价、中位数价和求购价（演示用假数据）。
    参数 market_hash_name：饰品的市场哈希名称，例如 'M4A1-S | 请擦擦 (崭新出厂)'
    """
    fake_prices = {
        "M4A1-S | 请擦擦 (崭新出厂)": {"lowest": "145.63", "median": "152.00", "hand": "123.78"},
        "AK-47 | 红线 (久经考验)": {"lowest": "623.10", "median": "635.50", "hand": "529.63"},
    }
    result = fake_prices.get(market_hash_name, {"lowest": "10.00", "median": "12.00", "hand": "8.50"})
    return result

# ---------- 工具2：查 Buff 在售数量 ----------
@mcp.tool()
async def buff_supply(market_hash_name: str) -> dict:
    """
    查询指定饰品在 Buff 上的在售数量和流动性评估（演
