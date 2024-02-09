from telegram import Update, InlineKeyboardMarkup, CallbackQuery, InlineKeyboardButton
from telegram.ext import ContextTypes
from src.Issue import Issue, load_issues, find_issue_by_message_id, remove_old_issues
from src.logger import get_logger
from src.config import config
from src.UI import render

logger = get_logger(__name__)


async def create_markup(chat_id: int, msg_id: int) -> InlineKeyboardMarkup:
    """Создает кнопки для обращения."""
    logger.debug(f"Создание кнопок для обращения {msg_id} в чате {chat_id}")
    keyboard = [
        [InlineKeyboardButton(
            text=config.ui.buttons.issueAssign,
            callback_data=f"issue_assign:{chat_id}:{msg_id}")],
        [InlineKeyboardButton(
            text=config.ui.buttons.issueCommon,
            callback_data=f"resolve_common:{chat_id}:{msg_id}")],
        [InlineKeyboardButton(
            text=config.ui.buttons.issueClose,
            callback_data=f"close_issue:{chat_id}:{msg_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def buttons_issue_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки в сообщениях об обращениях."""
    query = update.callback_query
    await query.answer()
    data = query.data
    action, chat_id, message_id = data.split(':')
    # Загрузка объектов Issue из хранилища
    issue_list = load_issues()  # Предполагается, что у вас есть функция загрузки
    issue: Issue = find_issue_by_message_id(issue_list, message_id)
    # Получаем исходный текст сообщения
    original_text = query.message.text_markdown_v2
    if not issue:
        logger.error(f"Обращение не найдено")
        return
    if action == "issue_assign":
        await issue_assign(context, query, issue, original_text, chat_id)
    elif action == "resolve_common":
        await resolve_common(context, query, issue, original_text, chat_id, issue_list)
    elif action == "close_issue":
        await close_issue(context, query, issue, original_text, chat_id, issue_list)


async def issue_assign(
        context: ContextTypes.DEFAULT_TYPE,
        query: CallbackQuery,
        issue: Issue,
        original_text: str,
        chat_id: str
):
    logger.debug(f"Обработка кнопки issue_assign, issue: {issue.id}")
    user = query.from_user.username
    msg = render(config.ui.messages.assignIssueReply, issue=issue, user=user)
    # Отправляем сообщение об этом в исходный чат
    await context.bot.send_message(chat_id=chat_id, text=msg)
    # Формируем новый текст обращения в целевой группе, добавляя информацию об исполнителе
    msg = render(config.ui.messages.assignIssueStatus, original_text=original_text, user=user)
    # Оставляем остальные кнопки
    keyboard = query.message.reply_markup.inline_keyboard
    new_keyboard = [
        row for row in keyboard
        if config.ui.buttons.issueAssign not in [button.text for button in row]]
    # Обновляем исходное сообщение, заменяя кнопку на текст об исполнителе
    await query.message.edit_text(
        text=msg,
        parse_mode='MarkdownV2',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=new_keyboard)
    )


async def resolve_common(
        context: ContextTypes.DEFAULT_TYPE,
        query: CallbackQuery,
        issue: Issue,
        original_text: str,
        chat_id: str,
        issue_list: dict[int, Issue]
):
    logger.debug(f"Обработка кнопки resolve_common, issue: {issue.id}")
    # Закрываем обращение
    msg = render(config.ui.messages.resolveCommonStatus, original_text=original_text, user=query.from_user.username)
    await query.message.edit_text(text=msg, parse_mode='MarkdownV2')
    # Отправляем сообщение в исходный чат
    msg = render(config.ui.messages.resolveCommonReply, issue=issue)
    await context.bot.send_message(chat_id=chat_id, text=msg)
    # Удаляем обращение из хранилища
    remove_old_issues(issue, issue_list)


async def close_issue(
        context: ContextTypes.DEFAULT_TYPE,
        query: CallbackQuery,
        issue: Issue,
        original_text: str,
        chat_id: str,
        issue_list: dict[int, Issue]
):
    logger.debug(f"Обработка кнопки close_issue, issue №{issue.id}")
    msg = render(config.ui.messages.resolveStatus, original_text=original_text, user=query.from_user.username)
    await query.message.edit_text(text=msg, parse_mode='MarkdownV2')
    # Отправляем сообщение в исходный чат
    msg = render(config.ui.messages.resolveReply, issue=issue)
    await context.bot.send_message(chat_id=chat_id, text=msg)
    # Удаляем обращение из хранилища
    remove_old_issues(issue, issue_list)
