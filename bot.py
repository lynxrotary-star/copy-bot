import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

TOKEN = os.environ.get('TOKEN')

# ТУТ АВТОМАТИЧЕСКИ ВПИСАН ВАШ КАНАЛ
CHANNEL_ID = "@g_to4ka" 

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли мне картинку с подписью (или текст) в формате:\n"
        "<b>Описание арта | Промт</b>\n\n"
        "Я сразу опубликую это в канале без всяких надписей!",
        parse_mode='HTML'
    )

async def handle_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.caption if update.message.caption else update.message.text
    if not text: return

    if "|" in text:
        description, prompt = text.split("|", 1)
        description = description.strip()
        prompt = prompt.strip()
    else:
        await update.message.reply_text("❌ Не найден разделитель |. Формат: Описание | Промт")
        return

    final_text = f"{description}\n\n<b>Промт:</b>\n<code>{prompt}</code>"

    try:
        if update.message.photo:
            photo_file_id = update.message.photo[-1].file_id
            # Отправляем фото в канал
            await context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo_file_id, caption=final_text, parse_mode='HTML')
        else:
            # Отправляем текст в канал
            await context.bot.send_message(chat_id=CHANNEL_ID, text=final_text, parse_mode='HTML')
            
        await update.message.reply_text("✅ Пост успешно опубликован в канале ТочкаG!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка публикации. Убедитесь, что бот админ в канале. Детали: {e}")

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, handle_post))
    bot_app.run_polling()
