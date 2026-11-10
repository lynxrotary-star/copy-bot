import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

TOKEN = os.environ.get('TOKEN')
CHANNEL_ID = "@g_to4ka" 

# ВАШИ ХЭШТЕГИ И ССЫЛКА НА КАНАЛ
# \n\n делает два отступа вниз, чтобы отделить от промта
HASHTAGS = "\n\n🔗 <a href='https://t.me/g_to4ka'><b>ТочкаG</b></a> | Подписаться\n#ТочкаG #нейросети #ИИарт #промты #Midjourney"

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли мне картинку с подписью (или текст) в формате:\n"
        "<b>Описание арта | Промт</b>\n\n"
        "Я сразу опубликую это в канале с хэштегами!",
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

    # Собираем пост: Описание -> Промт в блоке -> Хэштеги внизу
    final_text = f"{description}\n\n<b>Промт:</b>\n<code>{prompt}</code>{HASHTAGS}"

    try:
        if update.message.photo:
            photo_file_id = update.message.photo[-1].file_id
            await context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo_file_id, caption=final_text, parse_mode='HTML')
        else:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=final_text, parse_mode='HTML')
            
        await update.message.reply_text("✅ Пост с хэштегами успешно опубликован в канале ТочкаG!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка публикации. Детали: {e}")

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, handle_post))
    bot_app.run_polling()
