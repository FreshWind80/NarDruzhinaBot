import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Получаем токен и ID из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")

# Проверка переменных
if not TOKEN or not TARGET_CHAT_ID:
    raise RuntimeError("Переменные BOT_TOKEN и TARGET_CHAT_ID обязательны!")

# Этапы разговора
MESSAGE, ADDRESS, MEDIA = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши сообщение о происшествии:")
    return MESSAGE

async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["message"] = update.message.text
    await update.message.reply_text("Укажи адрес происшествия:")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    keyboard = [["Прикрепить фото/видео", "Продолжить без медиа"]]
    await update.message.reply_text(
        "Хочешь прикрепить медиа?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return MEDIA

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    media = None
    if update.message.text == "Продолжить без медиа":
        media = None
    else:
        media = update.message.photo or update.message.video

    message = context.user_data["message"]
    address = context.user_data["address"]
    final_text = f"📝 Сообщение:\n{message}\n\n📍 Адрес:\n{address}"

    await update.message.reply_text("Сообщение отправлено!", reply_markup=ReplyKeyboardRemove())

    await context.bot.send_message(chat_id=TARGET_CHAT_ID, text=final_text)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_message)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            MEDIA: [MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO, handle_media)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()

async def debug_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")

app.add_handler(CommandHandler("debug", debug_chat))
