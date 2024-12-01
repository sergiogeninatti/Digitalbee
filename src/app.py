import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


BOT_TOKEN = os.getenv("TELEGRAM_BOTTOKEN")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! I'm your Telegram bot.")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == "__main__":
    main()
