import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

TOKEN = os.environ.get('TOKEN')
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я помогу оформить посты с артами и промтами.\n\n"
        "Отправь мне картинку с подписью (или просто текст) в формате:\n"
        "<b>Описание арта | Промт</b>\n\n"
        "Я верну красивое сообщение с промтом в блоке для копирования.",
        parse_mode='HTML'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 <b>Инструкция:</b>\n\n"
        "1. Отправьте фото с подписью (или просто текст).\n"
        "2. Разделите описание и промт символом <b>|</b> (прямая черта).\n"
        "3. Слева — текст для канала, справа — сам промт.\n\n"
        "<b>Пример:</b>\n"
        "Девушка в стиле киберпанк | cyberpunk girl, neon lights, 8k, detailed",
        parse_mode='HTML'
    )

async def handle_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.caption if update.message.caption else update.message.text
    
    if not text:
        return

    if "|" in text:
        description, prompt = text.split("|", 1)
        description = description.strip()
        prompt = prompt.strip()
    else:
        await update.message.reply_text("❌ Не найден разделитель |. Пожалуйста, используй формат: Описание | Промт")
        return

    # Промт теперь без ограничения в 256 символов
    final_text = f"{description}\n\n<b>Промт:</b>\n<code>{prompt}</code>"

    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        await update.message.reply_photo(
            photo=photo_file_id, 
            caption=final_text, 
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(final_text, parse_mode='HTML')

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, handle_post))
    bot_app.run_polling()
