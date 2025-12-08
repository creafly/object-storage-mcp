from fastmcp import FastMCP

from src.core.settings import get_settings

settings = get_settings()

mcp = FastMCP(
    settings.APP_NAME,
)
