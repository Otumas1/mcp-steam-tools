import asyncio
import os
from mcp.server.fastmcp import FastMCP

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
    查询指定饰品在 Buff 上的在售数量和流动性评估（演示用假数据）。
    参数 market_hash_name：饰品的市场哈希名称
    """
    return {"total_count": 12, "liquidity": "低"}

# ---------- 工具3：浮点 & 贴纸溢价 ----------
@mcp.tool()
async def adjust_price(float_value: float = 0.05, stickers: list[str] = None) -> dict:
    """
    根据皮肤的磨损值和贴纸计算额外溢价。
    参数 float_value：皮肤的磨损值，0~1，越小越新
    参数 stickers：贴纸列表，空列表表示无贴纸
    """
    stickers = stickers or []
    float_extra = 0
    if float_value <= 0.001:
        float_extra = 15.0
    elif float_value >= 0.99:
        float_extra = 20.0
    sticker_extra = len(stickers) * 2.0
    return {"float_premium": float_extra, "sticker_premium": sticker_extra}

# ---------- 启动 SSE 服务 ----------
if __name__ == "__main__":
    mcp.run(transport="sse", port=int(os.environ.get("PORT", 8080)))
