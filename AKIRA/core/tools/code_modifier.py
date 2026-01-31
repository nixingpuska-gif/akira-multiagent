"""Code modification tools for self-improvement."""

from __future__ import annotations

import os
import ast
import difflib
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from .schema import Tool, ToolResult


@dataclass
class CodeAnalysis:
    """Result of code analysis."""
    file_path: str
    classes: List[Dict[str, Any]]
    functions: List[Dict[str, Any]]
    imports: List[str]
    lines_of_code: int
    complexity: int


class CodeModifierTool(Tool):
    """
    Tool for modifying code files.

    Provides full access to read, analyze, and modify any code file.
    NO RESTRICTIONS - complete autonomy.
    """

    def __init__(self):
        super().__init__(
            name="code_modify",
            description="Modify code files with full access",
            parameters={
                "action": {
                    "type": "string",
                    "enum": ["read", "write", "analyze", "diff"],
                    "description": "Action to perform"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to file"
                },
                "content": {
                    "type": "string",
                    "description": "New content (for write action)",
                    "required": False
                },
                "backup": {
                    "type": "boolean",
                    "description": "Create backup before modifying",
                    "default": True
                }
            }
        )

    async def execute(self, args: Dict[str, Any], context: Any) -> ToolResult:
        """Execute code modification."""
        action = args.get("action")
        file_path = args.get("file_path")

        if not file_path:
            return ToolResult(
                success=False,
                output="",
                error="file_path is required"
            )

        try:
            if action == "read":
                return await self._read_file(file_path)
            elif action == "write":
                content = args.get("content", "")
                backup = args.get("backup", True)
                return await self._write_file(file_path, content, backup)
            elif action == "analyze":
                return await self._analyze_file(file_path)
            elif action == "diff":
                content = args.get("content", "")
                return await self._show_diff(file_path, content)
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Unknown action: {action}"
                )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error: {str(e)}"
            )

    async def _read_file(self, file_path: str) -> ToolResult:
        """Read file content."""
        if not os.path.exists(file_path):
            return ToolResult(
                success=False,
                output="",
                error=f"File not found: {file_path}"
            )

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return ToolResult(
            success=True,
            output=content,
            metadata={"file_path": file_path, "size": len(content)}
        )

    async def _write_file(self, file_path: str, content: str, backup: bool) -> ToolResult:
        """Write content to file."""
        # Create backup if requested and file exists
        if backup and os.path.exists(file_path):
            backup_path = f"{file_path}.backup"
            with open(file_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)

        # Write new content
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return ToolResult(
            success=True,
            output=f"File written: {file_path}",
            metadata={
                "file_path": file_path,
                "size": len(content),
                "backup_created": backup
            }
        )

    async def _analyze_file(self, file_path: str) -> ToolResult:
        """Analyze Python file structure."""
        if not os.path.exists(file_path):
            return ToolResult(
                success=False,
                output="",
                error=f"File not found: {file_path}"
            )

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content)

            classes = []
            functions = []
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    })
                elif isinstance(node, ast.FunctionDef):
                    # Only top-level functions
                    if node.col_offset == 0:
                        functions.append({
                            "name": node.name,
                            "line": node.lineno,
                            "args": [arg.arg for arg in node.args.args]
                        })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    else:
                        module = node.module or ""
                        imports.append(module)

            analysis = {
                "file_path": file_path,
                "classes": classes,
                "functions": functions,
                "imports": list(set(imports)),
                "lines_of_code": len(content.splitlines())
            }

            return ToolResult(
                success=True,
                output=str(analysis),
                metadata=analysis
            )
        except SyntaxError as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Syntax error in file: {str(e)}"
            )

    async def _show_diff(self, file_path: str, new_content: str) -> ToolResult:
        """Show diff between current and new content."""
        if not os.path.exists(file_path):
            return ToolResult(
                success=True,
                output="New file (no diff)",
                metadata={"is_new_file": True}
            )

        with open(file_path, 'r', encoding='utf-8') as f:
            old_content = f.read()

        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"{file_path} (current)",
            tofile=f"{file_path} (new)",
            lineterm=''
        )

        diff_text = ''.join(diff)

        return ToolResult(
            success=True,
            output=diff_text,
            metadata={
                "file_path": file_path,
                "changes": len(diff_text)
            }
        )
