"""Shared status model for optional provider adapters."""

from dataclasses import asdict, dataclass


@dataclass
class ConnectorStatus:
    provider: str
    configured: bool
    capabilities: list[str]
    note: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)
