"""Tool creator (ASCII only)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .library import ToolSpec


class ToolCreator:
    def __init__(self) -> None:
        pass

    @staticmethod
    def build_spec(
        name: str,
        description: str,
        args_schema: Dict[str, Any],
        tags: Optional[List[str]] = None,
    ) -> ToolSpec:
        return ToolSpec(
            name=name,
            description=description,
            args_schema=args_schema,
            code="",
            tags=tags or [],
        )

    @staticmethod
    def create_stub(spec: ToolSpec) -> str:
        args_json = json.dumps(spec.args_schema, ensure_ascii=True, sort_keys=True)
        doc = spec.description.replace('"', "'")
        return (
            "# Auto-generated tool stub (ASCII only)\n"
            f"def {spec.name}(**kwargs):\n"
            f'    """{doc}"""\n'
            f"    # args_schema: {args_json}\n"
            '    raise NotImplementedError("Tool not implemented.")\n'
        )

    def create(self, spec: ToolSpec) -> ToolSpec:
        if not spec.code.strip():
            spec.code = self.create_stub(spec)
        return spec
