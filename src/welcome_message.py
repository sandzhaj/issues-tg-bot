from telegram import Update
from telegram.ext import ContextTypes
from src.config import config
from src.UI import render


async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    bot_name = context.bot.username
    welcome_msg = render(config.ui.messages.welcome, bot_name=bot_name, mentions=config.mentions)
    await context.bot.send_message(chat_id=chat.id, text=welcome_msg)
