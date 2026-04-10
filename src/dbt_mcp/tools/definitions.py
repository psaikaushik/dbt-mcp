from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from functools import cached_property, partial
from typing import Any

from mcp.server.fastmcp.tools.base import Tool
from mcp.types import ToolAnnotations

from dbt_mcp.tools.injection import adapt_with_mapper
from dbt_mcp.tools.tool_names import ToolName

# class DynamicToolAdapter(ABC):
#     @abstractmethod
#     def adapt_arguments(self, arguments: dict[str, Any]) -> dict[str, Any]: ...
#     # @abstractmethod
#     # def adapt_context(self, context: Any) -> Any: ...
#     @abstractmethod
#     def adapt_input_schema(self, input_schema: dict[str, Any]) -> dict[str, Any]: ...


@dataclass
class GenericToolDefinition[NameEnum: Enum]:
    fn: Callable[..., Any]
    description: str
    name_enum: type[NameEnum]
    name: str | None = None
    title: str | None = None
    annotations: ToolAnnotations | None = None
    # We haven't strictly defined our tool contracts yet.
    # So we're setting this to False by default for now.
    structured_output: bool | None = False
    meta: dict[str, Any] | None = None

    def get_name(self) -> NameEnum:
        return self.name_enum((self.name or self.fn.__name__).lower())

    # def input_schema(self) -> dict[str, Any]:
    #     if self.dynamic_adapter:
    #         return self.dynamic_adapter.adapt_input_schema(
    #             self.to_fastmcp_internal_tool.parameters
    #         )
    #     return self.to_fastmcp_internal_tool.parameters

    # def output_schema(self) -> dict[str, Any] | None:
    #     return self.to_fastmcp_internal_tool.output_schema

    # def adapt_arguments(self, arguments: dict[str, Any]) -> dict[str, Any]:
    #     if self.dynamic_adapter:
    #         return self.dynamic_adapter.adapt_arguments(arguments)
    #     return arguments

    @cached_property
    def to_fastmcp_internal_tool(self) -> Tool:
        return Tool.from_function(
            fn=self.fn,
            name=self.name,
            title=self.title,
            description=self.description,
            annotations=self.annotations,
            structured_output=self.structured_output,
            meta=self.meta,
        )

    def adapt_context(
        self, context_mapper: Callable[..., Any]
    ) -> "GenericToolDefinition[NameEnum]":
        """
        Adapt the tool definition to accept a different context object.
        """
        return type(self)(
            fn=adapt_with_mapper(self.fn, context_mapper),
            description=self.description,
            name_enum=self.name_enum,
            name=self.name,
            title=self.title,
            annotations=self.annotations,
            structured_output=self.structured_output,
            meta=self.meta,
        )


# @dataclass
# class AdaptedGenericToolDefinition[NameEnum: Enum]:
#     fn: Callable[..., Any]
#     description: str
#     name_enum: type[NameEnum]
#     name: str | None = None
#     title: str | None = None
#     annotations: ToolAnnotations | None = None
#     # We haven't strictly defined our tool contracts yet.
#     # So we're setting this to False by default for now.
#     structured_output: bool | None = False
#     meta: dict[str, Any] | None = None
#     dynamic_adapter: DynamicToolAdapter

#     def get_name(self) -> NameEnum:
#         return self.name_enum((self.name or self.fn.__name__).lower())

#     def input_schema(self) -> dict[str, Any]:
#         if self.dynamic_adapter:
#             return self.dynamic_adapter.adapt_input_schema(
#                 self.to_fastmcp_internal_tool.parameters
#             )
#         return self.to_fastmcp_internal_tool.parameters

#     def output_schema(self) -> dict[str, Any] | None:
#         return self.to_fastmcp_internal_tool.output_schema

#     def adapt_arguments(self, arguments: dict[str, Any]) -> dict[str, Any]:
#         if self.dynamic_adapter:
#             return self.dynamic_adapter.adapt_arguments(arguments)
#         return arguments

#     @cached_property
#     def to_fastmcp_internal_tool(self) -> Tool:
#         return Tool.from_function(
#             fn=self.fn,
#             name=self.name,
#             title=self.title,
#             description=self.description,
#             annotations=self.annotations,
#             structured_output=self.structured_output,
#             meta=self.meta,
#         )

#     def adapt_context(
#         self, context_mapper: Callable[..., Any]
#     ) -> "AdaptedGenericToolDefinition[NameEnum]":
#         """
#         Adapt the tool definition to accept a different context object.
#         """
#         return type(self)(
#             fn=adapt_with_mapper(self.fn, context_mapper),
#             description=self.description,
#             name_enum=self.name_enum,
#             name=self.name,
#             title=self.title,
#             annotations=self.annotations,
#             structured_output=self.structured_output,
#             meta=self.meta,
#             dynamic_adapter=self.dynamic_adapter,
#         )


@dataclass
class ToolDefinition(GenericToolDefinition[ToolName]):
    name_enum: type[ToolName] = ToolName


# def adapted_dbt_mcp_tool[NameEnum: Enum](
#     description: str,
#     name_enum: type[NameEnum],
#     dynamic_adapter: DynamicToolAdapter,
#     name: str | None = None,
#     title: str | None = None,
#     read_only_hint: bool = False,
#     destructive_hint: bool = True,
#     idempotent_hint: bool = False,
#     open_world_hint: bool = True,
#     structured_output: bool | None = False,
#     meta: dict[str, Any] | None = None,
# ) -> Callable[[Callable], AdaptedGenericToolDefinition[NameEnum]]:
#     """Decorator to define a tool definition for dbt MCP"""

#     def decorator(fn: Callable) -> AdaptedGenericToolDefinition[NameEnum]:
#         return AdaptedGenericToolDefinition(
#             fn=fn,
#             description=description,
#             name_enum=name_enum,
#             name=name,
#             title=title,
#             annotations=ToolAnnotations(
#                 title=title,
#                 readOnlyHint=read_only_hint,
#                 destructiveHint=destructive_hint,
#                 idempotentHint=idempotent_hint,
#                 openWorldHint=open_world_hint,
#             ),
#             structured_output=structured_output,
#             meta=meta,
#             dynamic_adapter=dynamic_adapter,
#         )

#     return decorator


def generic_dbt_mcp_tool[NameEnum: Enum](
    description: str,
    name_enum: type[NameEnum],
    name: str | None = None,
    title: str | None = None,
    read_only_hint: bool = False,
    destructive_hint: bool = True,
    idempotent_hint: bool = False,
    open_world_hint: bool = True,
    structured_output: bool | None = False,
    meta: dict[str, Any] | None = None,
) -> Callable[[Callable], GenericToolDefinition[NameEnum]]:
    """Decorator to define a tool definition for dbt MCP"""

    def decorator(fn: Callable) -> GenericToolDefinition[NameEnum]:
        return GenericToolDefinition(
            fn=fn,
            description=description,
            name_enum=name_enum,
            name=name,
            title=title,
            annotations=ToolAnnotations(
                title=title,
                readOnlyHint=read_only_hint,
                destructiveHint=destructive_hint,
                idempotentHint=idempotent_hint,
                openWorldHint=open_world_hint,
            ),
            structured_output=structured_output,
            meta=meta,
        )

    return decorator


# Wrapper with ToolName pre-supplied for the common case
dbt_mcp_tool = partial(generic_dbt_mcp_tool, name_enum=ToolName)
