from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("TARGET_CHAT_ID")

MESSAGE, ADDRESS, MEDIA = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши сообщение:")
    return MESSAGE

async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["message"] = update.message.text
    await update.message.reply_text("Теперь укажи адрес:")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    keyboard = [["Прикрепить медиа", "Продолжить без медиа"]]
    await update.message.reply_text(
        "Хочешь прикрепить медиа?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return MEDIA

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = context.user_data.get("message", "")
    address = context.user_data.get("address", "")
    full_message = f"📝 Сообщение:\n{message}\n📍 Адрес:\n{address}"

    await context.bot.send_message(chat_id=CHAT_ID, text=full_message)
    await update.message.reply_text("Готово! Спасибо.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_message)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            MEDIA: [MessageHandler(filters.ALL, handle_media)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    print("✅ Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()

async def debug_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")

app.add_handler(CommandHandler("debug", debug_chat))

