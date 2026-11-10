import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CopyTextButton
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

TOKEN = os.environ.get('TOKEN')

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли мне текст (до 256 символов), и я добавлю к нему кнопку копирования.")

async def create_copy_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_to_copy = update.message.text
    if len(text_to_copy) > 256:
        await update.message.reply_text("❌ Ошибка: Текст слишком длинный (макс. 256 символов).")
        return
    keyboard = [[InlineKeyboardButton("📋 Скопировать", copy_text=CopyTextButton(text=text_to_copy))]]
    await update.message.reply_text(text_to_copy, reply_markup=InlineKeyboardMarkup(keyboard))

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, create_copy_button))
    bot_app.run_polling()
