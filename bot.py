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
    await update.message.reply_text(
        "Привет! Я помогу создать пост с кнопкой копирования.\n\n"
        "Напиши мне сообщение по шаблону:\n"
        "Текст поста | Текст для копирования\n\n"
        "Например:\n"
        "Купите наш курс со скидкой! | PROMO2026"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Инструкция:\n\n"
        "1. Напишите текст, разделив его символом | (прямая черта).\n"
        "2. Слева от черты — текст, который увидят люди.\n"
        "3. Справа от черты — текст, который скопируется (до 256 символов).\n\n"
        "Пример: Это мой пост | секретный_код"
    )

async def create_copy_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "|" in text:
        post_text, copy_text = text.split("|", 1)
        post_text = post_text.strip()
        copy_text = copy_text.strip()
    else:
        post_text = text
        copy_text = text

    if len(copy_text) > 256:
        await update.message.reply_text("❌ Ошибка: Текст для копирования слишком длинный (макс. 256 символов).")
        return

    keyboard = [[InlineKeyboardButton("📋 Скопировать", copy_text=CopyTextButton(text=copy_text))]]
    await update.message.reply_text(post_text, reply_markup=InlineKeyboardMarkup(keyboard))

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, create_copy_button))
    bot_app.run_polling()
