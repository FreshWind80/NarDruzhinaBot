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
from dotenv import load_dotenv

# Поддержка .env при локальном запуске
load_dotenv()

# Переменные окружения
TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")

# Проверка обязательных переменных
if not TOKEN or not TARGET_CHAT_ID:
    raise RuntimeError("Переменные BOT_TOKEN и TARGET_CHAT_ID обязательны!")

# Состояния диалога
MESSAGE, ADDRESS, MEDIA = range(3)

# Обработчики
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
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return MEDIA

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_response = update.message.text
    media = None

    # Проверяем, хочет ли пользователь прикрепить медиа
    if user_response == "Продолжить без медиа":
        pass
    elif update.message.photo:
        media = update.message.photo[-1].file_id
        await context.bot.send_photo(chat_id=TARGET_CHAT_ID, photo=media)
    elif update.message.video:
        media = update.message.video.file_id
        await context.bot.send_video(chat_id=TARGET_CHAT_ID, video=media)

    message = context.user_data.get("message", "Нет сообщения")
    address = context.user_data.get("address", "Нет адреса")
    final_text = f"📝 Сообщение:\n{message}\n\n📍 Адрес:\n{address}"

    await context.bot.send_message(chat_id=TARGET_CHAT_ID, text=final_text)
    await update.message.reply_text("Сообщение отправлено!", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Главная функция
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

