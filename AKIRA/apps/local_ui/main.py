from fastapi import FastAPI, Request
import os
import sys
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.config import load_config, is_allowed
from core.runtime import AgentRuntime

app = FastAPI()
config = load_config()
runtime = AgentRuntime(config)
ACCESS_DENIED = "Access denied. Set AKIRA_UI_ALLOWLIST or set AKIRA_ALLOWLIST_REQUIRED=false."


class ChatRequest(BaseModel):
    text: str


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if not _is_local_request(request):
        return HTMLResponse(ACCESS_DENIED)
    if not is_allowed(config.ui_allowlist, "local", config.allowlist_required):
        return HTMLResponse(ACCESS_DENIED)
    safe_option = "" if getattr(config, "disable_safe_mode", False) else '<option value="safe">safe</option>'
    html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>AKIRA Local UI</title>
  <style>
    body { font-family: Arial, sans-serif; background:#0f1115; color:#e5e7eb; margin:0; }
    .wrap { max-width: 900px; margin: 40px auto; padding: 0 16px; }
    .card { background:#161a22; border:1px solid #2a3140; border-radius:12px; padding:16px; }
    .row { display:flex; gap:12px; align-items:center; margin-bottom:12px; }
    select { background:#0f1115; color:#e5e7eb; border:1px solid #2a3140; border-radius:8px; padding:6px; }
    textarea { width:100%; min-height:120px; background:#0f1115; color:#e5e7eb; border:1px solid #2a3140; border-radius:8px; padding:10px; }
    button { margin-top:12px; background:#22c55e; color:#0b0f14; border:none; padding:10px 16px; border-radius:8px; cursor:pointer; font-weight:600; }
    pre { white-space: pre-wrap; background:#0b0f14; padding:12px; border-radius:8px; border:1px solid #2a3140; }
  </style>
</head>
<body>
  <div class="wrap">
    <h2>AKIRA Local UI</h2>
    <div class="card">
      <div class="row">
        <label>Mode:</label>
        <select id="mode">
          __SAFE_OPTION__
          <option value="full">full</option>
        </select>
        <button onclick="setMode()">Set mode</button>
      </div>
      <textarea id="input" placeholder="Type your task..."></textarea>
      <button onclick="send()">Send</button>
      <h4>Reply</h4>
      <pre id="output"></pre>
    </div>
  </div>
  <script>
    async function setMode() {
      const mode = document.getElementById('mode').value;
      await fetch('/mode', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({mode})
      });
    }
    async function send() {
      const text = document.getElementById('input').value;
      const res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text})
      });
      const data = await res.json();
      document.getElementById('output').textContent = data.reply || JSON.stringify(data);
    }
  </script>
</body>
</html>
"""
    return html.replace("__SAFE_OPTION__", safe_option)


def _is_local_request(request: Request) -> bool:
    host = request.client.host if request.client else ""
    return host in ("127.0.0.1", "::1")


@app.post("/chat")
async def chat(req: ChatRequest, request: Request):
    if not _is_local_request(request):
        return {"reply": ACCESS_DENIED}
    if not is_allowed(config.ui_allowlist, "local", config.allowlist_required):
        return {"reply": ACCESS_DENIED}
    try:
        reply = await runtime.handle_message("local", req.text)
    except Exception as exc:
        err = " ".join(str(exc).split())
        if len(err) > 400:
            err = err[:400] + "..."
        return {"reply": f"LLM error. Check model/base. Details: {err}"}
    return {"reply": reply}


class ModeRequest(BaseModel):
    mode: str


@app.post("/mode")
async def set_mode(req: ModeRequest, request: Request):
    if not _is_local_request(request):
        return {"mode": "denied"}
    if not is_allowed(config.ui_allowlist, "local", config.allowlist_required):
        return {"mode": "denied"}
    runtime.tools.set_mode(req.mode.lower())
    return {"mode": runtime.tools.mode}
