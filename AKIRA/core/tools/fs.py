import os


def list_dir(path: str) -> list[str]:
    return os.listdir(path)


def read_file(path: str, max_bytes: int = 200_000) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read(max_bytes)


def write_file(path: str, content: str, mode: str = "safe") -> str:
    if mode != "full":
        return "ERROR: File writes disabled in safe mode. Set AKIRA_MODE=full."
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return "OK"
