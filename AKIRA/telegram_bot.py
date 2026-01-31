"""
AKIRA Telegram Bot
Main entry point for Telegram interaction
"""

import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from core.akira.akira_core import AKIRACore
from core.akira.model_presets import ModelPresets
from core.telegram.commands import TelegramCommands


async def start(update: Update, context):
    """Handle /start command."""
    await update.message.reply_text(
        "AKIRA-9 Online!\n\n"
        "Commands:\n"
        "/m 1-4 - Quick model switch\n"
        "/model - Current model\n"
        "/models - List models\n"
        "/status - System status"
    )




def main():
    """Start the Telegram bot."""
    print("=" * 60)
    print("AKIRA-9 TELEGRAM BOT")
    print("=" * 60)

    # Load config
    presets = ModelPresets()
    token = presets.get_telegram_token()

    if not token:
        print("[ERROR] Telegram token not found in config!")
        return

    print(f"[OK] Token loaded: {token[:20]}...")

    # Initialize AKIRA
    print("[OK] Initializing AKIRA Core...")
    akira = AKIRACore()

    # Initialize commands
    commands = TelegramCommands(akira)

    # Create application
    print("[OK] Creating Telegram application...")
    app = Application.builder().token(token).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("m", commands.cmd_m))
    app.add_handler(CommandHandler("model", commands.cmd_model))
    app.add_handler(CommandHandler("models", commands.cmd_models))
    app.add_handler(CommandHandler("status", commands.cmd_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, commands.handle_message))

    print("[OK] Bot ready!")
    print("=" * 60)
    print("Starting polling...")

    # Start bot
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
