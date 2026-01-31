"""System Diagnostics - Complete system analysis and health check."""

import os
import sys
import platform
import subprocess
import socket
from typing import Dict, List, Any
from dataclasses import dataclass, field

from .schema import Tool, ToolResult


@dataclass
class DiagnosticReport:
    """Complete diagnostic report."""
    system_info: Dict[str, str] = field(default_factory=dict)
    tools_available: Dict[str, bool] = field(default_factory=dict)
    network_status: Dict[str, Any] = field(default_factory=dict)
    filesystem_access: Dict[str, bool] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "system": self.system_info,
            "tools": self.tools_available,
            "network": self.network_status,
            "filesystem": self.filesystem_access,
            "warnings": self.warnings
        }


class SystemDiagnosticsTool(Tool):
    """
    Complete system diagnostics and health check.

    Checks:
    - System information
    - Available tools (bash, python, git, curl, etc.)
    - Network connectivity
    - Filesystem access
    """

    def __init__(self):
        super().__init__(
            name="system_diagnostics",
            description="Run complete system diagnostics",
            parameters={
                "check_network": {
                    "type": "boolean",
                    "description": "Check network connectivity",
                    "default": True
                },
                "check_tools": {
                    "type": "boolean",
                    "description": "Check available tools",
                    "default": True
                }
            }
        )

    async def execute(self, args: Dict[str, Any], context: Any) -> ToolResult:
        """Run diagnostics."""
        check_network = args.get("check_network", True)
        check_tools = args.get("check_tools", True)

        report = DiagnosticReport()

        # System info
        report.system_info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": sys.version.split()[0],
            "hostname": socket.gethostname(),
            "user": os.path.expanduser("~").split(os.sep)[-1]
        }

        # Check tools
        if check_tools:
            tools_to_check = [
                "bash", "python3", "pip3", "git", "curl", "wget",
                "node", "npm", "npx", "docker", "rg"
            ]

            for tool in tools_to_check:
                report.tools_available[tool] = self._check_tool(tool)

        # Network check
        if check_network:
            report.network_status = self._check_network()

        # Filesystem check
        report.filesystem_access = self._check_filesystem()

        # Generate warnings
        if not report.tools_available.get("git", False):
            report.warnings.append("Git not available - version control limited")
        if not report.tools_available.get("curl", False) and not report.tools_available.get("wget", False):
            report.warnings.append("No HTTP tools (curl/wget) - network operations limited")

        return ToolResult(
            success=True,
            output=self._format_report(report),
            metadata=report.to_dict()
        )

    def _check_tool(self, tool: str) -> bool:
        """Check if tool is available."""
        try:
            result = subprocess.run(
                ["which", tool] if os.name != "nt" else ["where", tool],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False

    def _check_network(self) -> Dict[str, Any]:
        """Check network connectivity."""
        status = {
            "internet": False,
            "dns": False,
            "latency": None
        }

        try:
            # Check DNS
            socket.gethostbyname("google.com")
            status["dns"] = True

            # Check internet
            sock = socket.create_connection(("8.8.8.8", 53), timeout=3)
            sock.close()
            status["internet"] = True
        except:
            pass

        return status

    def _check_filesystem(self) -> Dict[str, bool]:
        """Check filesystem access."""
        access = {}

        # Check temp directory
        temp_dir = os.path.join(os.path.expanduser("~"), "temp")
        try:
            os.makedirs(temp_dir, exist_ok=True)
            test_file = os.path.join(temp_dir, ".test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            access["temp_write"] = True
        except:
            access["temp_write"] = False

        # Check current directory
        try:
            test_file = ".test_write"
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            access["cwd_write"] = True
        except:
            access["cwd_write"] = False

        return access

    def _format_report(self, report: DiagnosticReport) -> str:
        """Format report as readable text."""
        lines = ["=== SYSTEM DIAGNOSTICS ===\n"]

        lines.append("SYSTEM INFO:")
        for key, value in report.system_info.items():
            lines.append(f"  {key}: {value}")

        lines.append("\nTOOLS AVAILABLE:")
        for tool, available in report.tools_available.items():
            status = "[OK]" if available else "[--]"
            lines.append(f"  {status} {tool}")

        lines.append("\nNETWORK STATUS:")
        for key, value in report.network_status.items():
            lines.append(f"  {key}: {value}")

        lines.append("\nFILESYSTEM ACCESS:")
        for key, value in report.filesystem_access.items():
            status = "[OK]" if value else "[--]"
            lines.append(f"  {status} {key}")

        if report.warnings:
            lines.append("\nWARNINGS:")
            for warning in report.warnings:
                lines.append(f"  [!] {warning}")

        return "\n".join(lines)
