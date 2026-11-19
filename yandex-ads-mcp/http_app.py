"""Streamable HTTP entry (stateless) for avadge-mcp proxy; token/read-only per request headers."""

from contextlib import asynccontextmanager

from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount

import server

mgr = StreamableHTTPSessionManager(app=server.server, stateless=True, json_response=True)


@asynccontextmanager
async def lifespan(_app):
    async with mgr.run():
        yield


app = Starlette(routes=[Mount("/mcp", app=mgr.handle_request)], lifespan=lifespan)
