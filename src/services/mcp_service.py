from typing import Any, Dict, List, Optional, Tuple
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.sse import sse_client
import logging

logger = logging.getLogger(__name__)


class MCPService:
    async def _connect_to_mcp_server(
        self, config_json: Dict[str, Any]
    ) -> Tuple[List[Any], Optional[AsyncExitStack]]:
        exit_stack = AsyncExitStack()
        try:
            url = config_json.get("url", "")
            headers = config_json.get("headers", {})
            sse_transport = await exit_stack.enter_async_context(
                sse_client(url, headers=headers)
            )
            read, write = sse_transport
            session = await exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            result = await session.list_tools()
            return result.tools, exit_stack
        except Exception as e:
            logger.error(f"Error connecting to MCP server: {e}")
            await exit_stack.aclose()
            return [], None
