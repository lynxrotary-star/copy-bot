import os
import threading
from flask import Flask
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler, InlineQueryHandler

TOKEN = os.environ.get('TOKEN')
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я помогу оформить посты с промтами.\n\n"
        "1. В личке: Отправь мне картинку с подписью: Описание | Промт\n"
        "2. В канале: Напиши в поле ввода @Copy69Botik_bot Описание | Промт",
        parse_mode='HTML'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 <b>Инструкция:</b>\n\n"
        "Чтобы использовать меня в канале или чате, просто начните писать сообщение и введите:\n"
        "<code>@Copy69Botik_bot Описание | Промт</code>\n\n"
        "Выберите появившийся вариант, и пост опубликуется от вашего имени!",
        parse_mode='HTML'
    )

# --- Логика для ЛИЧНЫХ СООБЩЕНИЙ (с картинками) ---
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

    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        await update.message.reply_photo(photo=photo_file_id, caption=final_text, parse_mode='HTML')
    else:
        await update.message.reply_text(final_text, parse_mode='HTML')

# --- Логика для INLINE-РЕЖИМА (вызов через @ в любом чате) ---
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query: return

    if "|" in query:
        description, prompt = query.split("|", 1)
        description = description.strip()
        prompt = prompt.strip()
    else:
        description = query
        prompt = ""

    if prompt:
        final_text = f"{description}\n\n<b>Промт:</b>\n<code>{prompt}</code>"
    else:
        final_text = description

    results = [
        InlineQueryResultArticle(
            id="1",
            title="Опубликовать пост",
            description="Нажмите, чтобы отправить в чат/канал",
            input_message_content=InputTextMessageContent(
                message_text=final_text,
                parse_mode='HTML'
            )
        )
    ]
    await update.inline_query.answer(results)

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(InlineQueryHandler(inline_query))
    bot_app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, handle_post))
    bot_app.run_polling()
