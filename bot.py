import os
import threading
import html
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

TOKEN = os.environ.get('TOKEN')
CHANNEL_ID = "@g_to4ka" 

# ТВОИ ХЭШТЕГИ И ССЫЛКА НА КАНАЛ
HASHTAGS = "\n\n🔗 <a href='https://t.me/g_to4ka'><b>ТочкаG</b></a> | Подписаться\n#шедеврум #девушка #бёдра #бюст #красиво #нежно #ИИ #арт #картина"

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли мне картинку с подписью в формате:\n"
        "<b>Платформа | Промт</b>\n\n"
        "Я сразу опубликую это в канале!",
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
        await update.message.reply_text("❌ Не найден разделитель |. Формат: Платформа | Промт")
        return

    safe_prompt = html.escape(prompt)
    safe_description = html.escape(description)

    final_text = f"{safe_description}\n\n<b>Промт:</b>\n<code>{safe_prompt}</code>{HASHTAGS}"

    try:
        if update.message.photo:
            photo_file_id = update.message.photo[-1].file_id
            await context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo_file_id, caption=final_text, parse_mode='HTML')
        else:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=final_text, parse_mode='HTML')
            
        await update.message.reply_text("✅ Пост успешно опубликован!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, handle_post))
    bot_app.run_polling()
