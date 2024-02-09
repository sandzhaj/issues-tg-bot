from src.config import config
from src.Issue import Issue, load_issues, save_issues
from telegram import Update
from telegram.ext import ContextTypes
from src.buttons_issue import create_markup
from src.logger import get_logger

logger = get_logger(__name__)


async def create_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.effective_message
    issue = Issue(
        message=msg.text_markdown_v2,
        author=msg.from_user.username,
        source=chat.title or chat.first_name or str(update.effective_chat.id),
        isDirectMsg=chat.type in ['private'],
        messageId=str(msg.message_id)
    )
    # Сохраняем объект issue в контексте
    issues = load_issues()
    issues[issue.id] = issue
    save_issues(issues)
    # Создаем кнопки для Issue
    markup = await create_markup(chat.id, msg.message_id)

    # Отправляем уведомление об обращении в targetChatId канал
    await context.bot.send_message(
        chat_id=config.targetChatId,
        text=issue.issueMsg,
        parse_mode='MarkdownV2',
        reply_markup=markup)
    # Отправляем уведомление в исходный чат, что обращение было отправлено
    await context.bot.send_message(
        chat_id=chat.id,
        text=issue.createIssueReply)
