import os
import array
from telegram import (
    Update
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)


copyfecha = 2024

start_text = (
        "Analisis grafico de colmenas\n"
        "(c) UCO " + str(copyfecha)
        )


BOT_TOKEN = os.getenv("TELEGRAM_BOTTOKEN")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global start_text
    await update.message.reply_text(start_text)

async def usuario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    quienes = update.message.from_user
    n = quienes.find(":")
    await update.message.reply_text(quienes)

async def moto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Aca viene la moto\n"
        )

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("moto", moto))
    application.add_handler(CommandHandler("usuario", usuario))
    application.run_polling()

if __name__ == "__main__":
    main()
