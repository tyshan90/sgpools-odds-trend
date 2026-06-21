from __future__ import annotations

import argparse
import os
from pathlib import Path

from .cli import DEFAULT_DB
from .formatting import format_changes, format_latest
from .store import OddsStore


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Telegram bot for stored Singapore Pools odds trends")
    parser.add_argument("--db", default=DEFAULT_DB, type=Path)
    parser.add_argument("--token", default=os.environ.get("TELEGRAM_BOT_TOKEN"))
    args = parser.parse_args(argv)

    if not args.token:
        raise SystemExit("Missing Telegram token. Set TELEGRAM_BOT_TOKEN or pass --token.")

    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes
    except ImportError as exc:
        raise SystemExit("python-telegram-bot is not installed. Run: python -m pip install -r requirements.txt") from exc

    store = OddsStore(args.db)

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Singapore Pools odds tracker\n\n"
            "Commands:\n"
            "/odds <match words>\n"
            "/change <match words>\n\n"
            "Example: /change spain saudi"
        )

    async def odds(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        match = " ".join(context.args).strip()
        if not match:
            await update.message.reply_text('Usage: /odds <match words>, e.g. /odds spain saudi')
            return
        await update.message.reply_text(format_latest(store.latest_for_match(match)))

    async def change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        match = " ".join(context.args).strip()
        if not match:
            await update.message.reply_text('Usage: /change <match words>, e.g. /change spain saudi')
            return
        await update.message.reply_text(format_changes(store.change_for_match(match)))

    app = Application.builder().token(args.token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("odds", odds))
    app.add_handler(CommandHandler("change", change))
    app.run_polling()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

