from collections.abc import Sequence
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ContentBlock
from mcp.types import Tool as MCPTool

from dbt_mcp.config.credentials import CredentialsProvider


# TODO: consolidate this with DbtMCP class
class ToolDispatcher(FastMCP):
    def __init__(
        self,
        credentials_provider: CredentialsProvider,
        multi_project_mcp: FastMCP,
        single_project_mcp: FastMCP,
    ):
        # TODO: clean this up
        super().__init__(
            name="ToolDispatcher",
            instructions="This is a tool dispatcher for the dbt MCP server.",
            website_url="https://www.dbt.com",
        )
        self.credentials_provider = credentials_provider
        self.multi_project_mcp = multi_project_mcp
        self.single_project_mcp = single_project_mcp

    def _is_multi_project(self, settings: Any) -> bool:
        return bool(
            settings.dbt_project_ids is not None and len(settings.dbt_project_ids) > 0
        )

    async def call_tool(
        self, name: str, arguments: dict[str, Any]
    ) -> Sequence[ContentBlock] | dict[str, Any]:
        settings, _ = await self.credentials_provider.get_credentials()
        if self._is_multi_project(settings):
            return await self.multi_project_mcp.call_tool(name, arguments)
        return await self.single_project_mcp.call_tool(name, arguments)

    async def list_tools(self) -> list[MCPTool]:
        settings, _ = await self.credentials_provider.get_credentials()
        if self._is_multi_project(settings):
            return await self.multi_project_mcp.list_tools()
        return await self.single_project_mcp.list_tools()
