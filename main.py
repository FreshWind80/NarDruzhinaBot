
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    ConversationHandler, filters
)

STAGE_MESSAGE, STAGE_ADDRESS, STAGE_MEDIA, STAGE_CONFIRM = range(4)
TARGET_GROUP_CHAT_ID = -1001234567890  # Замените на реальный chat_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Что произошло?")
    return STAGE_MESSAGE

async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['message'] = update.message.text
    await update.message.reply_text("📍 Где это произошло? Укажите точный адрес.")
    return STAGE_ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    keyboard = [["📎 Прикрепить медиа", "⏭ Продолжить без медиа"]]
    await update.message.reply_text(
        "📷 Можете прикрепить фото или видео, или нажмите «Продолжить без медиа».",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return STAGE_MEDIA

async def get_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    media = update.message.photo or update.message.video

    if text == "⏭ Продолжить без медиа":
        context.user_data['media'] = None
        return await confirm(update, context)

    if media:
        context.user_data['media'] = update.message
        return await confirm(update, context)

    if text == "📎 Прикрепить медиа":
        await update.message.reply_text("Пожалуйста, отправьте фото или видео, или нажмите «Продолжить без медиа».")
        return STAGE_MEDIA

    await update.message.reply_text("Пожалуйста, прикрепите медиа или нажмите «Продолжить без медиа».")
    return STAGE_MEDIA

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = context.user_data['message']
    address = context.user_data['address']
    has_media = "✅ Да" if context.user_data['media'] else "❌ Нет"

    summary = f"""Проверьте данные перед отправкой:
🚨 Происшествие: {message}
📍 Адрес: {address}
📷 Мультимедиа: {has_media}

Отправить сообщение? (да / нет)
"""
    await update.message.reply_text(summary, reply_markup=ReplyKeyboardRemove())
    return STAGE_CONFIRM

async def send_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg_text = f"""⚠️ Новое сообщение от {user.full_name or '@' + user.username}:

🚨 Происшествие: {context.user_data['message']}
📍 Адрес: {context.user_data['address']}
"""
    media = context.user_data.get('media')
    if media:
        if media.photo:
            file = await media.photo[-1].get_file()
            await context.bot.send_photo(chat_id=TARGET_GROUP_CHAT_ID, photo=file.file_id, caption=msg_text)
        elif media.video:
            file = await media.video.get_file()
            await context.bot.send_video(chat_id=TARGET_GROUP_CHAT_ID, video=file.file_id, caption=msg_text)
    else:
        await context.bot.send_message(chat_id=TARGET_GROUP_CHAT_ID, text=msg_text)

    await update.message.reply_text("✅ Ваше сообщение отправлено. Спасибо!")
    return ConversationHandler.END

async def cancel_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отправка отменена.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Диалог прерван.")
    return ConversationHandler.END

if __name__ == '__main__':
    import os
    TOKEN = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STAGE_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_message)],
            STAGE_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            STAGE_MEDIA: [
                MessageHandler(filters.PHOTO | filters.VIDEO | filters.TEXT, get_media)
            ],
            STAGE_CONFIRM: [
                MessageHandler(filters.Regex('^(да|Да|yes|Yes)$'), send_report),
                MessageHandler(filters.Regex('^(нет|Нет|no|No)$'), cancel_report),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    print("🤖 Бот запущен...")

    app.run_polling()

async def debug_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")

app.add_handler(CommandHandler("debug", debug_chat))

