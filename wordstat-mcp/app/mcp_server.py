"""Streamable HTTP MCP server for the Wordstat website."""
import asyncio

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers
from mcp_service import WordstatError, resolve_cookie, top_requests, monthly_dynamics, suggestions

mcp = FastMCP("wordstat")


async def call_wordstat(fn, *args):
    try:
        cookie = resolve_cookie(get_http_headers(include_all=True))
        return await asyncio.to_thread(fn, cookie, *args)
    except WordstatError as exc:
        raise ToolError(str(exc)) from None


@mcp.tool
async def wordstat_top_requests(phrase: str, region: str = "all") -> dict:
    """Популярные запросы и их частотность за окно по умолчанию сайта Wordstat."""
    return await call_wordstat(top_requests, phrase, region)


@mcp.tool
async def wordstat_monthly_dynamics(phrase: str, start_date: str, end_date: str, region: str = "all") -> dict:
    """Помесячная динамика. Даты YYYY-MM-DD, не менее трёх полных месяцев; публикация может запаздывать."""
    return await call_wordstat(monthly_dynamics, phrase, start_date, end_date, region)


@mcp.tool
async def wordstat_suggest(phrase: str) -> dict:
    """Поисковые подсказки Яндекса для заданной фразы; cookie не требуется."""
    try:
        return await asyncio.to_thread(suggestions, phrase)
    except WordstatError as exc:
        raise ToolError(str(exc)) from None


app = mcp.http_app(path="/mcp", stateless_http=True)
