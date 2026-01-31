"""OSINT Tools - Advanced intelligence gathering integration."""

import subprocess
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .schema import Tool, ToolResult


@dataclass
class OSINTResult:
    """OSINT gathering result."""
    tool: str
    target: str
    data: Dict[str, Any] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)
    timestamp: str = ""


class TheHarvesterTool(Tool):
    """
    theHarvester integration for email/subdomain/IP gathering.

    Collects information from public sources.
    """

    def __init__(self):
        super().__init__(
            name="osint_harvester",
            description="Gather emails, subdomains, IPs from public sources",
            parameters={
                "domain": {
                    "type": "string",
                    "description": "Target domain to investigate"
                },
                "sources": {
                    "type": "string",
                    "description": "Data sources (google, bing, linkedin, etc.)",
                    "default": "google,bing"
                },
                "limit": {
                    "type": "integer",
                    "description": "Result limit",
                    "default": 500
                }
            }
        )

    async def execute(self, args: Dict[str, Any], context: Any) -> ToolResult:
        """Run theHarvester."""
        domain = args.get("domain")
        sources = args.get("sources", "google,bing")
        limit = args.get("limit", 500)

        if not domain:
            return ToolResult(
                success=False,
                output="",
                error="Domain is required"
            )

        try:
            # Check if theHarvester is installed
            check = subprocess.run(
                ["which", "theHarvester"],
                capture_output=True,
                timeout=5
            )

            if check.returncode != 0:
                return ToolResult(
                    success=False,
                    output="",
                    error="theHarvester not installed. Install: pip install theHarvester"
                )

            # Run theHarvester
            cmd = [
                "theHarvester",
                "-d", domain,
                "-b", sources,
                "-l", str(limit),
                "-f", f"/tmp/harvest_{domain}"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            # Parse results
            data = self._parse_output(result.stdout)

            return ToolResult(
                success=True,
                output=json.dumps(data, indent=2),
                metadata={
                    "domain": domain,
                    "sources": sources,
                    "emails_found": len(data.get("emails", [])),
                    "hosts_found": len(data.get("hosts", []))
                }
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                output="",
                error="Operation timed out"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error: {str(e)}"
            )

    def _parse_output(self, output: str) -> Dict[str, List[str]]:
        """Parse theHarvester output."""
        data = {
            "emails": [],
            "hosts": [],
            "ips": []
        }

        for line in output.split('\n'):
            if '@' in line and '.' in line:
                # Potential email
                parts = line.split()
                for part in parts:
                    if '@' in part and '.' in part:
                        data["emails"].append(part.strip())
            elif line.strip().startswith(('http://', 'https://', 'www.')):
                # Potential host
                data["hosts"].append(line.strip())

        return data


class SherlockTool(Tool):
    """
    Sherlock integration for username search across social networks.

    Finds user accounts by username.
    """

    def __init__(self):
        super().__init__(
            name="osint_sherlock",
            description="Find user accounts across social networks",
            parameters={
                "username": {
                    "type": "string",
                    "description": "Username to search"
                },
                "sites": {
                    "type": "string",
                    "description": "Specific sites to check (comma-separated)",
                    "required": False
                }
            }
        )

    async def execute(self, args: Dict[str, Any], context: Any) -> ToolResult:
        """Run Sherlock."""
        username = args.get("username")
        sites = args.get("sites")

        if not username:
            return ToolResult(
                success=False,
                output="",
                error="Username is required"
            )

        try:
            # Check if Sherlock is installed
            check = subprocess.run(
                ["which", "sherlock"],
                capture_output=True,
                timeout=5
            )

            if check.returncode != 0:
                return ToolResult(
                    success=False,
                    output="",
                    error="Sherlock not installed. Install: pip install sherlock-project"
                )

            # Build command
            cmd = ["sherlock", username, "--json", "--timeout", "10"]

            if sites:
                cmd.extend(["--site", sites])

            # Run Sherlock
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            # Parse JSON output
            try:
                data = json.loads(result.stdout)
            except:
                data = {"raw_output": result.stdout}

            found_accounts = len([k for k, v in data.items() if isinstance(v, dict) and v.get("url_user")])

            return ToolResult(
                success=True,
                output=json.dumps(data, indent=2),
                metadata={
                    "username": username,
                    "accounts_found": found_accounts,
                    "sites_checked": len(data)
                }
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                output="",
                error="Operation timed out"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error: {str(e)}"
            )
