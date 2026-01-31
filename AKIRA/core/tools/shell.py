import subprocess


def run_command(command: str, mode: str = "safe") -> str:
    if mode != "full":
        return "ERROR: Shell disabled in safe mode. Set AKIRA_MODE=full."
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return output.strip()
    except subprocess.CalledProcessError as exc:
        return f"ERROR: Command failed: {exc}"
