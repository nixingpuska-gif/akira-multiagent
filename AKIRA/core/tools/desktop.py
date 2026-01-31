try:
    import pyautogui
except Exception:  # pragma: no cover
    pyautogui = None


def screenshot(path: str, mode: str = "safe") -> str:
    if mode != "full":
        return "ERROR: Desktop tools disabled in safe mode. Set AKIRA_MODE=full."
    if pyautogui is None:
        return "ERROR: pyautogui is not installed."
    img = pyautogui.screenshot()
    img.save(path)
    return path


def click(x: int, y: int, mode: str = "safe") -> str:
    if mode != "full":
        return "ERROR: Desktop tools disabled in safe mode. Set AKIRA_MODE=full."
    if pyautogui is None:
        return "ERROR: pyautogui is not installed."
    pyautogui.click(x, y)
    return "OK"


def type_text(text: str, mode: str = "safe") -> str:
    if mode != "full":
        return "ERROR: Desktop tools disabled in safe mode. Set AKIRA_MODE=full."
    if pyautogui is None:
        return "ERROR: pyautogui is not installed."
    pyautogui.write(text, interval=0.02)
    return "OK"


def hotkey(keys: list[str], mode: str = "safe") -> str:
    if mode != "full":
        return "ERROR: Desktop tools disabled in safe mode. Set AKIRA_MODE=full."
    if pyautogui is None:
        return "ERROR: pyautogui is not installed."
    pyautogui.hotkey(*keys)
    return "OK"
