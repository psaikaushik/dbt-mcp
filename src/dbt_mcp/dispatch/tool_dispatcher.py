# from collections.abc import Sequence
# from dataclasses import dataclass
# from enum import Enum
# from typing import Any

# from mcp.server.fastmcp import FastMCP
# from mcp.types import ContentBlock
# from mcp.types import Tool as MCPTool

# from dbt_mcp.config.config_providers import (
#     ConfigProvider,
#     DiscoveryConfig,
#     MultiProjectDiscoveryConfigProvider,
# )
# from dbt_mcp.config.settings import DbtMcpSettings
# from dbt_mcp.discovery.client import AppliedResourceType, ResourceDetailsFetcher
# from dbt_mcp.discovery.tools import DiscoveryToolContext
# from dbt_mcp.prompts.prompts import get_prompt
# from dbt_mcp.tools.definitions import (
#     AdaptedGenericToolDefinition,
#     DynamicToolAdapter,
#     GenericToolDefinition,
#     adapted_dbt_mcp_tool,
# )
# from dbt_mcp.tools.fields import NAME_FIELD, UNIQUE_ID_FIELD
# from dbt_mcp.tools.tool_names import ToolName


# @dataclass
# class TestToolContext:
#     resource_details_fetcher: ResourceDetailsFetcher

#     def __init__(
#         self,
#         settings: DbtMcpSettings,
#         config_provider: ConfigProvider[DiscoveryConfig],
#         multi_project_config_provider: MultiProjectDiscoveryConfigProvider,
#     ):
#         self.settings = settings
#         self.resource_details_fetcher = ResourceDetailsFetcher()
#         self.config_provider = config_provider
#         self.multi_project_config_provider = multi_project_config_provider

#     async def get_config(self) -> DiscoveryConfig:
#         if self.settings.actual_prod_environment_id is not None:
#             return await self.config_provider.get_config()
#         return await self.multi_project_config_provider.get_config(project_id="1")


# class DiscoveryDynamicToolAdapter(DynamicToolAdapter):
#     def adapt_arguments(self, arguments: dict[str, Any]) -> dict[str, Any]:
#         if "project_id" in arguments:
#             project_id = arguments["project_id"]
#             config = await self.config_provider.get_config(project_id=project_id)
#         else:
#             config = await self.config_provider.get_config()
#         return {**arguments, "config": config}

#     def adapt_input_schema(self, input_schema: dict[str, Any]) -> dict[str, Any]:
#         # TODO: If multi-project -> add project_id parameter
#         return input_schema


# @adapted_dbt_mcp_tool(
#     name_enum=ToolName,
#     description=get_prompt("discovery/get_model_details"),
#     title="Get Model Details",
#     read_only_hint=True,
#     destructive_hint=False,
#     idempotent_hint=True,
#     dynamic_adapter=DiscoveryDynamicToolAdapter(),
# )
# async def get_model_details(
#     context: TestToolContext,
#     name: str | None = NAME_FIELD,
#     unique_id: str | None = UNIQUE_ID_FIELD,
# ) -> list[dict]:
#     return await context.resource_details_fetcher.fetch_details(
#         resource_type=AppliedResourceType.MODEL,
#         config=await context.get_config(),
#         unique_id=unique_id,
#         name=name,
#     )


# tools: list[AdaptedGenericToolDefinition[ToolName]] = [
#     get_model_details,
# ]


# class ToolDispatcher[NameEnum: Enum]:
#     def __init__(
#         self, mcp_server: FastMCP, tools: list[GenericToolDefinition[NameEnum]]
#     ):
#         self.index = {tool.name: tool for tool in tools}
#         self.mcp_server = mcp_server

#         def bind_context() -> DiscoveryToolContext:
#             return TestToolContext()

#         for tool in tools:
#             self.mcp_server.add_tool(
#                 fn=tool.adapt_context(bind_context).fn,
#                 name=tool.get_name().value,
#                 title=tool.title,
#                 description=tool.description,
#                 annotations=tool.annotations,
#                 structured_output=tool.structured_output,
#                 meta=tool.meta,
#             )

#     async def call_tool(
#         self, name: str, arguments: dict[str, Any]
#     ) -> Sequence[ContentBlock] | dict[str, Any]:
#         tool = self.index.get(name)
#         if not tool:
#             raise ValueError("TODO")
#         return await self.mcp_server.call_tool(name, tool.adapt_arguments(arguments))

#     async def list_tools(self) -> list[MCPTool]:
#         return [
#             MCPTool(
#                 name=t.get_name().value,
#                 title=t.title,
#                 description=t.description,
#                 inputSchema=t.input_schema(),
#                 outputSchema=t.output_schema(),
#                 annotations=t.annotations,
#                 icons=None,  # None of our tools have icons
#                 _meta=t.meta,
#             )
#             for t in tools
#         ]
