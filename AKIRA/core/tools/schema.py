"""Tool definition schema (ASCII only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ToolDefinition:
    name: str
    description: str
    args_schema: Dict[str, Any]
    output_schema: Optional[Dict[str, Any]] = None

    def validate_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        errors: List[str] = []
        schema = self.args_schema or {}
        props = schema.get("properties") if isinstance(schema, dict) else None
        required = schema.get("required") if isinstance(schema, dict) else None
        if not isinstance(props, dict):
            # Fallback: treat schema as flat param->type map
            props = schema if isinstance(schema, dict) else {}
            required = list(props.keys())
        if not isinstance(required, list):
            required = []

        for key in required:
            if key not in args:
                errors.append(f"Missing required arg: {key}")

        for key, value in args.items():
            expected = props.get(key)
            if expected is None:
                continue
            if isinstance(expected, dict):
                expected = expected.get("type")
            if expected:
                if not self._type_ok(value, str(expected)):
                    errors.append(f"Invalid type for {key}: expected {expected}")
        return {"ok": not errors, "errors": errors}

    def serialize(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "args_schema": self.args_schema,
            "output_schema": self.output_schema or {},
        }

    @staticmethod
    def _type_ok(value: Any, expected: str) -> bool:
        if expected == "string":
            return isinstance(value, str)
        if expected == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if expected == "boolean":
            return isinstance(value, bool)
        if expected == "object":
            return isinstance(value, dict)
        if expected == "array":
            return isinstance(value, list)
        return True


@dataclass
class ToolResult:
    """Result from tool execution."""
    success: bool
    output: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Tool:
    """Base class for tools."""

    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters

    async def execute(self, args: Dict[str, Any], context: Any) -> ToolResult:
        """Execute tool with given arguments."""
        raise NotImplementedError("Tool must implement execute method")
