import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo Mcp", stateless_http=True, json_response=True)

@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m**2)

@mcp.tool()
async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city"""
    async with httpx.AsyncClient() as client:
        return "天晴，25度"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    # mcp.run(transport="sse")
    # mcp.run(transport="stdio")

