"""
AKIRA Terminal Executor
Executes commands through terminal (claude, codex, etc.)
"""

import subprocess
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    """Result of terminal command execution."""
    success: bool
    output: str
    error: Optional[str] = None
    exit_code: int = 0
    command: str = ""


class TerminalExecutor:
    """
    Executes commands through terminal.
    Main interface for running claude and codex.
    """

    def __init__(self, timeout: int = 600):
        self.timeout = timeout  # Default 10 minutes
        self.execution_history: List[ExecutionResult] = []

    async def execute_claude(
        self,
        task_description: str,
        working_dir: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute task using Claude Code through terminal.

        Args:
            task_description: Description of task for Claude
            working_dir: Working directory for execution

        Returns:
            ExecutionResult with output
        """
        command = ["claude", task_description]

        return await self._execute_command(
            command,
            working_dir=working_dir,
            description="Claude Code execution"
        )

    async def execute_codex(
        self,
        prompt: str,
        working_dir: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute code generation using Codex through terminal.

        Args:
            prompt: Prompt for Codex
            working_dir: Working directory

        Returns:
            ExecutionResult with generated code
        """
        # Assuming openai CLI or similar tool
        command = ["openai", "api", "completions.create", "-m", "code-davinci-002", "-p", prompt]

        return await self._execute_command(
            command,
            working_dir=working_dir,
            description="Codex execution"
        )

    async def _execute_command(
        self,
        command: List[str],
        working_dir: Optional[str] = None,
        description: str = ""
    ) -> ExecutionResult:
        """
        Execute shell command.

        Args:
            command: Command as list of strings
            working_dir: Working directory
            description: Human-readable description

        Returns:
            ExecutionResult
        """
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )

            result = ExecutionResult(
                success=process.returncode == 0,
                output=stdout.decode('utf-8', errors='ignore'),
                error=stderr.decode('utf-8', errors='ignore') if stderr else None,
                exit_code=process.returncode,
                command=" ".join(command)
            )

            self.execution_history.append(result)
            return result

        except asyncio.TimeoutError:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Command timed out after {self.timeout} seconds",
                exit_code=-1,
                command=" ".join(command)
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Execution error: {str(e)}",
                exit_code=-1,
                command=" ".join(command)
            )
