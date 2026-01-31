import asyncio
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram import F

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.config import load_config, is_allowed
from core.runtime import AgentRuntime

config = load_config()
runtime = AgentRuntime(config)
settings_store = runtime.settings

bot = Bot(token=config.telegram_token)
dp = Dispatcher()
ACCESS_DENIED = "Access denied. Set AKIRA_TELEGRAM_ALLOWLIST or set AKIRA_ALLOWLIST_REQUIRED=false."
_pending_inputs: dict[str, str] = {}

def _mode_keyboard() -> types.ReplyKeyboardMarkup:
    if getattr(config, "disable_safe_mode", False):
        keyboard = [[types.KeyboardButton(text="Mode: full")]]
    else:
        keyboard = [
            [
                types.KeyboardButton(text="Mode: safe"),
                types.KeyboardButton(text="Mode: full"),
            ],
        ]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def _menu_keyboard() -> types.ReplyKeyboardMarkup:
    rows = []
    if getattr(config, "disable_safe_mode", False):
        rows.append([types.KeyboardButton(text="Mode: full")])
    else:
        rows.append(
            [
                types.KeyboardButton(text="Mode: safe"),
                types.KeyboardButton(text="Mode: full"),
            ]
        )
    rows.append([types.KeyboardButton(text="LLM: provider"), types.KeyboardButton(text="LLM: model")])
    rows.append([types.KeyboardButton(text="LLM: key"), types.KeyboardButton(text="LLM: base")])
    rows.append([types.KeyboardButton(text="LLM: status"), types.KeyboardButton(text="LLM: reset")])
    return types.ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def _provider_keyboard() -> types.ReplyKeyboardMarkup:
    rows = [
        [types.KeyboardButton(text="LLM: primary"), types.KeyboardButton(text="LLM: openrouter")],
        [types.KeyboardButton(text="LLM: custom"), types.KeyboardButton(text="/menu")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def _extract_mode(text: str) -> str | None:
    t = text.strip().lower()
    if t.startswith("/mode"):
        parts = t.split(maxsplit=1)
        if len(parts) > 1:
            return parts[1].strip()
        return "full" if getattr(config, "disable_safe_mode", False) else "safe"
    if t in ("mode: safe", "safe", "safe mode", "режим safe", "режим: safe"):
        if getattr(config, "disable_safe_mode", False):
            return None
        return "safe"
    if t in ("mode: full", "full", "full mode", "режим full", "режим: full"):
        return "full"
    return None

def _get_provider(user_id: str) -> str:
    settings = settings_store.load_settings(user_id)
    return settings.get("provider") or "primary"

def _status_text(user_id: str) -> str:
    settings = settings_store.load_settings(user_id)
    provider = settings.get("provider") or "primary"
    model = settings.get("model") or config.model
    primary_key = settings.get("primary_key")
    openrouter_key = settings.get("openrouter_key")
    custom_key = settings.get("custom_key")
    custom_base = settings.get("custom_base")

    if provider == "openrouter":
        key_display = settings_store.mask_key(openrouter_key) if openrouter_key else ("set (env)" if config.openrouter_api_key else "not set")
        base_display = config.openrouter_base
    elif provider == "custom":
        key_display = settings_store.mask_key(custom_key) if custom_key else "not set"
        base_display = custom_base or "not set"
    else:
        key_display = settings_store.mask_key(primary_key) if primary_key else "set (env)"
        base_display = config.primary_api_base

    return (
        "LLM status:\n"
        f"provider: {provider}\n"
        f"model: {model}\n"
        f"base: {base_display}\n"
        f"key: {key_display}"
    )

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id if message.from_user else message.chat.id)
    if not is_allowed(config.telegram_allowlist, user_id, config.allowlist_required):
        await message.reply(ACCESS_DENIED)
        return
    await message.reply(
        "AKIRA is online. Memory and tools are ready. Send a task.",
        reply_markup=_mode_keyboard(),
    )


@dp.message(Command("id"))
async def cmd_id(message: types.Message):
    user_id = message.from_user.id if message.from_user else message.chat.id
    if not is_allowed(config.telegram_allowlist, str(user_id), config.allowlist_required):
        await message.reply(ACCESS_DENIED)
        return
    await message.reply(f"Your Telegram ID: {user_id}")


@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    user_id = str(message.from_user.id if message.from_user else message.chat.id)
    if not is_allowed(config.telegram_allowlist, user_id, config.allowlist_required):
        await message.reply(ACCESS_DENIED)
        return
    _pending_inputs.pop(user_id, None)
    await message.reply("Menu:", reply_markup=_menu_keyboard())

@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message):
    user_id = str(message.from_user.id if message.from_user else message.chat.id)
    _pending_inputs.pop(user_id, None)
    await message.reply("Canceled.", reply_markup=_menu_keyboard())

@dp.message(F.text)
async def handle_message(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    text = message.text.strip()
    user_id = str(message.from_user.id if message.from_user else message.chat.id)
    if not is_allowed(config.telegram_allowlist, user_id, config.allowlist_required):
        await message.answer(ACCESS_DENIED)
        return

    pending = _pending_inputs.get(user_id)
    if pending:
        if text.startswith("/"):
            _pending_inputs.pop(user_id, None)
            await message.answer("Canceled.", reply_markup=_menu_keyboard())
            return
        elif pending == "provider":
            provider = text.strip().lower().replace("llm:", "").strip()
            if provider not in ("primary", "openrouter", "custom"):
                await message.answer("Invalid provider. Use primary, openrouter, or custom.")
                return
            settings_store.set_provider(user_id, provider)
            _pending_inputs.pop(user_id, None)
            err = await runtime.apply_llm_settings(user_id)
            if err:
                await message.answer(err, reply_markup=_menu_keyboard())
            else:
                await message.answer(f"Provider set: {provider}", reply_markup=_menu_keyboard())
            return
        elif pending == "model":
            settings_store.set_model(user_id, text)
            _pending_inputs.pop(user_id, None)
            err = await runtime.apply_llm_settings(user_id)
            if err:
                await message.answer(err)
            else:
                await message.answer("Model updated.")
            return
        elif pending == "openrouter_key":
            settings_store.set_openrouter_key(user_id, text)
            _pending_inputs.pop(user_id, None)
            err = await runtime.apply_llm_settings(user_id)
            if err:
                await message.answer(err)
            else:
                await message.answer("OpenRouter key saved.")
            return
        elif pending == "custom_key":
            settings_store.set_custom_key(user_id, text)
            _pending_inputs.pop(user_id, None)
            err = await runtime.apply_llm_settings(user_id)
            if err:
                await message.answer(err)
            else:
                await message.answer("Custom key saved.")
            return
        elif pending == "custom_base":
            settings_store.set_custom_base(user_id, text)
            _pending_inputs.pop(user_id, None)
            err = await runtime.apply_llm_settings(user_id)
            if err:
                await message.answer(err)
            else:
                await message.answer("Custom base saved.")
            return
        elif pending == "primary_key":
            settings_store.set_primary_key(user_id, text)
            _pending_inputs.pop(user_id, None)
            err = await runtime.apply_llm_settings(user_id)
            if err:
                await message.answer(err)
            else:
                await message.answer("Primary key saved.")
            return

    if text in ("LLM: primary", "LLM: openrouter", "LLM: custom"):
        provider = text.split(":", 1)[1].strip().lower()
        settings_store.set_provider(user_id, provider)
        err = await runtime.apply_llm_settings(user_id)
        if err:
            await message.answer(err, reply_markup=_menu_keyboard())
        else:
            await message.answer(f"Provider set: {provider}", reply_markup=_menu_keyboard())
        return

    if text == "LLM: provider":
        _pending_inputs[user_id] = "provider"
        await message.answer("Pick provider (or /menu to cancel).", reply_markup=_provider_keyboard())
        return

    if text == "LLM: model":
        _pending_inputs[user_id] = "model"
        await message.answer("Send model name (or /menu to cancel).")
        return

    if text == "LLM: key":
        provider = _get_provider(user_id)
        if provider == "openrouter":
            _pending_inputs[user_id] = "openrouter_key"
            await message.answer("Send OpenRouter key (or /menu to cancel).")
            return
        if provider == "custom":
            _pending_inputs[user_id] = "custom_key"
            await message.answer("Send custom key (or /menu to cancel).")
            return
        _pending_inputs[user_id] = "primary_key"
        await message.answer("Send primary key override (or /menu to cancel).")
        return

    if text == "LLM: base":
        provider = _get_provider(user_id)
        if provider != "custom":
            await message.answer("LLM base is used only for custom provider.")
            return
        _pending_inputs[user_id] = "custom_base"
        await message.answer("Send custom base URL (or /menu to cancel).")
        return

    if text == "LLM: status":
        await message.answer(_status_text(user_id))
        return

    if text == "LLM: reset":
        settings_store.reset(user_id)
        err = await runtime.apply_llm_settings(user_id)
        if err:
            await message.answer(err)
        else:
            await message.answer("LLM settings reset to env.", reply_markup=_menu_keyboard())
        return

    mode = _extract_mode(text)
    if mode:
        runtime.tools.set_mode(mode)
        await message.answer(f"Mode set: {mode}", reply_markup=_menu_keyboard())
        return

    try:
        ai_text = await runtime.handle_message(user_id, text)
    except Exception as exc:
        err = " ".join(str(exc).split())
        if len(err) > 400:
            err = err[:400] + "..."
        print(f"LLM error: {exc}", file=sys.stderr)
        await message.answer(f"LLM error. Check model/base. Details: {err}")
        return
    await message.answer(ai_text)


async def start_everything():
    print("--- AKIRA STARTED ---")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_everything())
