import asyncio
import os
import aiohttp
from mcp.server.fastmcp import FastMCP
import uvicorn

mcp = FastMCP("CS:GO 估价工具")

# 缓存全部饰品行情（用于第三方 API）
_exchange_cache = None
_exchange_cache_time = 0
CACHE_TTL = 120  # 秒

# 获取第三方 API 全量数据（带缓存）
async def _get_all_exchange_data(session: aiohttp.ClientSession) -> list:
    global _exchange_cache, _exchange_cache_time
    now = asyncio.get_event_loop().time()
    if _exchange_cache and (now - _exchange_cache_time) < CACHE_TTL:
        return _exchange_cache

    url = "https://api.csqaq.com/api/v1/info/exchange_detail"
    token = os.getenv("CSQAQ_API_TOKEN", "")
    if not token:
        return [{"error": "环境变量 CSQAQ_API_TOKEN 未设置"}]

    async with session.post(url, json={"ApiToken": token}) as resp:
        if resp.status != 200:
            return [{"error": f"第三方 API 返回状态码 {resp.status}"}]
        raw = await resp.json()
        if raw.get("code") != 200:
            return [{"error": raw.get("msg", "第三方接口异常")}]
        data = raw.get("data", [])
    _exchange_cache = data
    _exchange_cache_time = now
    return data

@mcp.tool()
async def all_platform_price(market_hash_name: str) -> dict:
    """
    查询指定饰品在 Buff、悠悠有品、Steam 的真实价格（人民币）。
    参数 market_hash_name 为官方英文哈希名，例如 'MP9 | Deadly Poison (Minimal Wear)'。
    """
    async with aiohttp.ClientSession() as session:
        all_data = await _get_all_exchange_data(session)
        if isinstance(all_data, list) and len(all_data) > 0 and "error" in all_data[0]:
            return {"error": all_data[0]["error"]}
        # 精确匹配
        for item in all_data:
            if item.get("market_hash_name") == market_hash_name:
                return {
                    "market_hash_name": market_hash_name,
                    "buff_sell_price": item.get("buff_sell_price"),
                    "buff_sell_num": item.get("buff_sell_num"),
                    "buff_buy_price": item.get("buff_buy_price"),
                    "buff_buy_num": item.get("buff_buy_num"),
                    "steam_sell_price": item.get("steam_sell_price"),
                    "steam_sell_num": item.get("steam_sell_num"),
                    "steam_buy_price": item.get("steam_buy_price"),
                    "steam_buy_num": item.get("steam_buy_num"),
                    "yyyp_sell_price": item.get("yyyp_sell_price"),
                    "yyyp_sell_num": item.get("yyyp_sell_num"),
                    "yyyp_buy_price": item.get("yyyp_buy_price"),
                    "yyyp_buy_num": item.get("yyyp_buy_num"),
                    "img": item.get("img"),
                    "name": item.get("name"),
                }
        return {"error": f"未找到饰品 '{market_hash_name}' 的数据"}

# 原有的 Steam 直接查询（备用）
price_cache = {}

async def fetch_steam_price(session: aiohttp.ClientSession, market_hash_name: str) -> dict:
    import urllib.parse
    encoded = urllib.parse.quote(market_hash_name)
    url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=23&market_hash_name={encoded}"
    async with session.get(url) as resp:
        if resp.status != 200:
            return {"error": f"Steam API 返回 {resp.status}"}
        data = await resp.json()
        if not data.get("success"):
            return {"error": "Steam 无此物品"}
        return {
            "lowest_price": data.get("lowest_price", "N/A"),
            "median_price": data.get("median_price", "N/A"),
            "volume": data.get("volume", "0")
        }

@mcp.tool()
async def steam_price(market_hash_name: str) -> dict:
    """
    直接查询 Steam 市场最低价（人民币），可作为备用验证。
    """
    if market_hash_name in price_cache:
        return price_cache[market_hash_name]
    async with aiohttp.ClientSession() as session:
        result = await fetch_steam_price(session, market_hash_name)
    price_cache[market_hash_name] = result
    asyncio.get_event_loop().call_later(120, lambda: price_cache.pop(market_hash_name, None))
    return result

@mcp.tool()
async def adjust_price(float_value: float = 0.05, stickers: list[str] = None) -> dict:
    """根据磨损值和贴纸计算额外溢价。"""
    stickers = stickers or []
    float_extra = 0
    if float_value <= 0.001:
        float_extra = 15.0
    elif float_value >= 0.99:
        float_extra = 20.0
    sticker_extra = len(stickers) * 2.0
    return {"float_premium": float_extra, "sticker_premium": sticker_extra}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    try:
        app = mcp.sse_app()
    except AttributeError:
        app = mcp.app
    uvicorn.run(app, host="0.0.0.0", port=port)
