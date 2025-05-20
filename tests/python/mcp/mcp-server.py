import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MCP Server", stateless_http=True, json_response=True)

@mcp.tool()
async def fetch_weather(city: str) -> str:
    """根据城市名称查询指定城市的天气"""
    async with httpx.AsyncClient() as client:
        return "天晴，25度"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    # mcp.run(transport="sse")
    # mcp.run(transport="stdio")

