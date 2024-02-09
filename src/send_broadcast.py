from telegram import Update
from telegram.ext import ContextTypes
from src.logger import get_logger
from src.track_bot_membership import get_chat_id_list
from src.config import config

logger = get_logger(__name__)


async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_ids = get_chat_id_list()
    for chat_id in chat_ids:
        try:
            logger.debug(f"Отправка сообщения в чат {chat_id}")
            await context.bot.send_message(chat_id=chat_id,
                                           text=update.message.text_markdown_v2,
                                           parse_mode='MarkdownV2')
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение в чат {chat_id}: {e}")
    await update.message.reply_text(config.ui.messages.broadcastSuccess, parse_mode='MarkdownV2')
    del context.user_data['awaiting_broadcast_message']
