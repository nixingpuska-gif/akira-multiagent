import os
import re
import string
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None


def _load_env():
    if load_dotenv:
        if os.getenv("AKIRA_SKIP_DOTENV", "").lower() in ("1", "true", "yes", "on"):
            return
        override = os.getenv("AKIRA_DOTENV_OVERRIDE", "1").lower() in ("1", "true", "yes", "on")
        root_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
        load_dotenv(root_env, override=override)
        load_dotenv(override=override)


def _get_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


def _detect_drive_roots() -> list[str]:
    roots = []
    for letter in string.ascii_uppercase:
        root = f"{letter}:\\"
        if os.path.exists(root):
            roots.append(root)
    return roots


def _expand_mcp_roots(raw: str) -> list[str]:
    value = raw.strip()
    if not value:
        return []
    if value.upper() in ("ALL", "*", "FULL"):
        return _detect_drive_roots()
    if value.upper() in ("HOME", "USER"):
        return [os.path.expanduser("~")]
    return [p.strip() for p in value.split(";") if p.strip()]


def _parse_allowlist(raw: str | None) -> list[str]:
    if not raw:
        return []
    value = raw.strip()
    if not value:
        return []
    if value.upper() in ("ALL", "*"):
        return ["*"]
    parts = re.split(r"[,\s;]+", value)
    return [p for p in parts if p]


def is_allowed(allowlist: list[str], subject: str, allowlist_required: bool) -> bool:
    if not allowlist:
        return not allowlist_required
    if "*" in allowlist:
        return True
    return subject in allowlist


@dataclass
class AkiraConfig:
    telegram_token: str
    telegram_allowlist: list[str]
    ui_allowlist: list[str]
    allowlist_required: bool
    primary_api_base: str
    primary_api_key: str
    openrouter_api_key: str | None
    openrouter_base: str
    model: str
    fallback_model: str | None
    wire_api: str
    fallback_wire_api: str
    disable_safe_mode: bool
    mode: str
    data_dir: str
    ui_enabled: bool
    ui_host: str
    ui_port: int
    timeout_s: float
    mcp_roots: list[str]
    n8n_api_base: str | None
    n8n_api_key: str | None
    chatdev_path: str
    browser_proxy: str | None


def load_config() -> AkiraConfig:
    _load_env()

    telegram_token = _get_env("AKIRA_TELEGRAM_TOKEN") or _get_env("TELEGRAM_TOKEN")
    telegram_allowlist = _parse_allowlist(_get_env("AKIRA_TELEGRAM_ALLOWLIST"))
    ui_allowlist = _parse_allowlist(_get_env("AKIRA_UI_ALLOWLIST"))
    allowlist_required = (_get_env("AKIRA_ALLOWLIST_REQUIRED") or "true").lower() in ("1", "true", "yes", "on")
    primary_api_base = _get_env("AKIRA_PRIMARY_API_BASE") or _get_env("OPENAI_BASE_URL")
    primary_api_key = _get_env("AKIRA_PRIMARY_API_KEY") or _get_env("OPENAI_API_KEY")
    openrouter_api_key = _get_env("OPENROUTER_API_KEY")
    openrouter_base = _get_env("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1/chat/completions"
    model = _get_env("AKIRA_MODEL") or "gpt-4o"
    fallback_model = _get_env("AKIRA_FALLBACK_MODEL")
    wire_api = (_get_env("AKIRA_WIRE_API") or "chat").lower()
    fallback_wire_api = (_get_env("AKIRA_FALLBACK_WIRE_API") or "chat").lower()
    disable_safe_mode = (_get_env("AKIRA_DISABLE_SAFE_MODE") or "false").lower() in ("1", "true", "yes", "on")
    mode = (_get_env("AKIRA_MODE") or "safe").lower()
    data_dir = _get_env("AKIRA_DATA_DIR") or os.path.join(os.getcwd(), "data")
    ui_enabled = (_get_env("AKIRA_UI_ENABLED") or "true").lower() in ("1", "true", "yes", "on")
    ui_host = _get_env("AKIRA_UI_HOST") or "127.0.0.1"
    ui_port = int(_get_env("AKIRA_UI_PORT") or "8000")
    timeout_s = float(_get_env("AKIRA_TIMEOUT_S") or "60")
    mcp_roots_raw = _get_env("AKIRA_MCP_ROOTS") or ""
    mcp_roots = _expand_mcp_roots(mcp_roots_raw)
    if not mcp_roots:
        mcp_roots = [os.getcwd()]

    n8n_api_base = _get_env("N8N_API_BASE") or _get_env("AKIRA_N8N_API_BASE")
    n8n_api_key = _get_env("N8N_API_KEY") or _get_env("AKIRA_N8N_API_KEY")
    chatdev_path = _get_env("AKIRA_CHATDEV_PATH") or r"C:\Users\Nicita\ChatDev"
    browser_proxy = _get_env("AKIRA_BROWSER_PROXY") or _get_env("AKIRA_TOR_PROXY")

    if not telegram_token:
        raise ValueError("Missing AKIRA_TELEGRAM_TOKEN (or TELEGRAM_TOKEN).")
    if not primary_api_base:
        raise ValueError("Missing AKIRA_PRIMARY_API_BASE (or OPENAI_BASE_URL).")
    if not primary_api_key:
        raise ValueError("Missing AKIRA_PRIMARY_API_KEY (or OPENAI_API_KEY).")

    os.makedirs(data_dir, exist_ok=True)

    # Provide OpenAI-compatible envs for mem0/embedding backends
    os.environ.setdefault("OPENAI_API_KEY", primary_api_key)
    os.environ.setdefault("OPENAI_BASE_URL", primary_api_base)

    return AkiraConfig(
        telegram_token=telegram_token,
        telegram_allowlist=telegram_allowlist,
        ui_allowlist=ui_allowlist,
        allowlist_required=allowlist_required,
        primary_api_base=primary_api_base,
        primary_api_key=primary_api_key,
        openrouter_api_key=openrouter_api_key,
        openrouter_base=openrouter_base,
        model=model,
        fallback_model=fallback_model,
        wire_api=wire_api,
        fallback_wire_api=fallback_wire_api,
        disable_safe_mode=disable_safe_mode,
        mode=mode,
        data_dir=data_dir,
        ui_enabled=ui_enabled,
        ui_host=ui_host,
        ui_port=ui_port,
        timeout_s=timeout_s,
        mcp_roots=mcp_roots,
        n8n_api_base=n8n_api_base,
        n8n_api_key=n8n_api_key,
        chatdev_path=chatdev_path,
        browser_proxy=browser_proxy,
    )
