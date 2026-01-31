"""Tool validator (ASCII only)."""

from __future__ import annotations

import re
from typing import List

from .library import ToolSpec


class ToolValidator:
    NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def validate(self, spec: ToolSpec) -> List[str]:
        errors: List[str] = []
        if not spec.name or not self.NAME_RE.match(spec.name):
            errors.append("Invalid name.")
        if not isinstance(spec.args_schema, dict):
            errors.append("args_schema must be a dict.")
        if not isinstance(spec.code, str) or not spec.code.strip():
            errors.append("Code is empty.")
        if not isinstance(spec.description, str):
            errors.append("description must be a string.")
        if not self._is_ascii(spec.name):
            errors.append("name must be ASCII.")
        if not self._is_ascii(spec.description):
            errors.append("description must be ASCII.")
        if not self._is_ascii(spec.code):
            errors.append("code must be ASCII.")
        return errors

    def is_valid(self, spec: ToolSpec) -> bool:
        return not self.validate(spec)

    @staticmethod
    def _is_ascii(text: str) -> bool:
        try:
            text.encode("ascii")
            return True
        except Exception:
            return False
