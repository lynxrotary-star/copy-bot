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

async def handle_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Берем текст из подписи к фото или из обычного сообщения
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

    # Форматируем текст: описание + промт в блоке <code>
    final_text = f"{description}\n\n<b>Промт:</b>\n<code>{prompt}</code>"

    # Если пользователь прислал фото — отправляем фото с подписью
    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        await update.message.reply_photo(
            photo=photo_file_id, 
            caption=final_text, 
            parse_mode='HTML'
        )
    else:
        # Если просто текст
        await update.message.reply_text(final_text, parse_mode='HTML')

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    # Обрабатываем и текст, и фото с подписями
    bot_app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, handle_post))
    bot_app.run_polling()
