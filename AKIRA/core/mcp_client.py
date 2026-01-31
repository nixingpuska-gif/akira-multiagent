from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import anyio
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client
    from mcp import types
except Exception:  # pragma: no cover
    ClientSession = None
    StdioServerParameters = None
    stdio_client = None
    types = None
    anyio = None


@dataclass
class MCPServerConfig:
    name: str
    command: str
    args: List[str]
    cwd: Optional[str] = None
    env: Optional[Dict[str, str]] = None


class MCPServerHandle:
    def __init__(self, cfg: MCPServerConfig, roots: List[str]):
        self.cfg = cfg
        self.roots = roots
        self._ctx = None
        self._session: ClientSession | None = None
        self._read = None
        self._write = None
        self._session_entered = False

    async def connect(self):
        if ClientSession is None or stdio_client is None or StdioServerParameters is None:
            raise RuntimeError("mcp client not installed")
        if self._session:
            return

        params = StdioServerParameters(
            command=self.cfg.command,
            args=self.cfg.args,
            cwd=self.cfg.cwd,
            env=self.cfg.env,
        )

        async def list_roots_callback(context):
            root_objs = [
                types.Root(uri=Path(p).resolve().as_uri(), name=Path(p).name)
                for p in self.roots
            ]
            return types.ListRootsResult(roots=root_objs)

        self._ctx = stdio_client(params)
        self._read, self._write = await self._ctx.__aenter__()
        self._session = ClientSession(
            self._read,
            self._write,
            list_roots_callback=list_roots_callback,
        )
        await self._session.__aenter__()
        self._session_entered = True
        await self._session.initialize()

    async def list_tools(self):
        await self.connect()
        assert self._session
        return await self._session.list_tools()

    async def call_tool(self, name: str, arguments: dict | None = None):
        await self.connect()
        assert self._session
        return await self._session.call_tool(name, arguments or {})

    async def close(self):
        if self._session and self._session_entered:
            await self._session.__aexit__(None, None, None)
            self._session_entered = False
        if self._ctx:
            await self._ctx.__aexit__(None, None, None)
        self._ctx = None
        self._session = None
        self._read = None
        self._write = None


class MCPManager:
    def __init__(self, roots: List[str] | None = None):
        self.roots = roots or [os.getcwd()]
        self.servers: Dict[str, MCPServerHandle] = {}

        # Defaults: can be overridden later by explicit registration.
        self.register(
            MCPServerConfig(
                name="time",
                command=sys.executable,
                args=["-m", "mcp_server_time"],
            )
        )
        self.register(
            MCPServerConfig(
                name="fetch",
                command=sys.executable,
                args=["-m", "mcp_server_fetch"],
            )
        )
        self.register(
            MCPServerConfig(
                name="git",
                command=sys.executable,
                args=["-m", "mcp_server_git"],
            )
        )
        # Filesystem uses Node by default (npx). Requires Node installed.
        self.register(
            MCPServerConfig(
                name="filesystem",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", *self.roots],
            )
        )

    def register(self, cfg: MCPServerConfig):
        self.servers[cfg.name] = MCPServerHandle(cfg, self.roots)

    async def close_all(self):
        for handle in self.servers.values():
            try:
                await handle.close()
            except Exception:
                pass

    async def set_roots(self, roots: List[str]):
        self.roots = roots
        for handle in self.servers.values():
            handle.roots = roots
        fs_handle = self.servers.get("filesystem")
        if fs_handle:
            try:
                await fs_handle.close()
            except Exception:
                pass
        self.register(
            MCPServerConfig(
                name="filesystem",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", *self.roots],
            )
        )

    async def list_tools(self, server: str):
        if server not in self.servers:
            raise ValueError(f"Unknown MCP server: {server}")
        return await self.servers[server].list_tools()

    async def call(self, server: str, tool: str, args: dict | None = None):
        if server not in self.servers:
            raise ValueError(f"Unknown MCP server: {server}")
        return await self.servers[server].call_tool(tool, args or {})
