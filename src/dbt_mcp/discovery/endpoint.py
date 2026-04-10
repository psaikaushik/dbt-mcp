from dataclasses import dataclass

from dbt_mcp.config.headers import HeadersProvider


@dataclass
class Endpoint[T: HeadersProvider]:
    url: str
    headers_provider: T
