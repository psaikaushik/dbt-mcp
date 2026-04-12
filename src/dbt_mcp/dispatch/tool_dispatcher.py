from collections.abc import Sequence
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ContentBlock
from mcp.types import Tool as MCPTool

from dbt_mcp.config.credentials import CredentialsProvider


class MultiprojectToolDispatchMCPServer(FastMCP):
    def __init__(
        self,
        *,
        name: str,
        credentials_provider: CredentialsProvider,
        multi_project_mcp: FastMCP,
        single_project_mcp: FastMCP,
    ):
        super().__init__(
            name=name,
        )
        self.credentials_provider = credentials_provider
        self.multi_project_mcp = multi_project_mcp
        self.single_project_mcp = single_project_mcp

    async def _is_multi_project(self) -> bool:
        settings, _ = await self.credentials_provider.get_credentials()
        return bool(
            settings.dbt_project_ids is not None and len(settings.dbt_project_ids) > 0
        )

    async def call_tool(
        self, name: str, arguments: dict[str, Any]
    ) -> Sequence[ContentBlock] | dict[str, Any]:
        if await self._is_multi_project():
            return await self.multi_project_mcp.call_tool(name, arguments)
        return await self.single_project_mcp.call_tool(name, arguments)

    async def list_tools(self) -> list[MCPTool]:
        if await self._is_multi_project():
            return await self.multi_project_mcp.list_tools()
        return await self.single_project_mcp.list_tools()
