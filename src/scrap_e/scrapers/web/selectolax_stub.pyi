"""Type stubs for selectolax (not actually used but satisfies mypy)."""

from typing import Any

class HTMLParser:
    """Stub class for selectolax HTMLParser."""

    def __init__(self, html: str) -> None: ...
    def css(self, selector: str) -> list[Any]: ...
    def css_first(self, selector: str) -> Any | None: ...
