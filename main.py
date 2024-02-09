from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler
)

from src.config import config
from src.logger import get_logger
from src.buttons_issue import buttons_issue_handler
from src.create_issue import create_issue
from src.welcome_message import send_welcome_message
from src.send_broadcast import send_broadcast
from src.track_bot_membership import add_bot_membership, remove_bot_membership

logger = get_logger(__name__)


# Приветственное сообщение при /start
async def start(update: Update, _):
    user_id = update.effective_user.id
    logger.info(f'Запуск start пользователем {user_id}')
    if user_id in config.allowedBroadcastIds:
        logger.debug(f'Пользователь {user_id} разрешен для отправки broadcast сообщений')
        keyboard = [[KeyboardButton('Отправить сообщение для всех групп')]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            f'Привет, {config.get_person_by_id(user_id).name}. Тебе доступна волшебная кнопка.',
            reply_markup=reply_markup
        )
    else:
        logger.debug(f'Обычный пользователь. {user_id}')
        await update.message.reply_text(
            text='Опишите проблему и первый освободившийся сотрудник возьмется за нее.',
            reply_markup=ReplyKeyboardRemove()
        )


# Обработка сообщений
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_mentioned = any(mention in update.effective_message.text for mention in config.mentions)
    if not (update.effective_chat.type in ['private'] or is_mentioned):
        return

    # Не обрабатываем сообщения внутри самой targetChatId группы
    if str(update.effective_chat.id) == str(config.targetChatId):
        return

    if update.message.text == config.ui.buttons.broadcast:
        logger.info(f'Пользователь {update.effective_user.id} запросил отправку broadcast сообщения')
        if update.effective_user.id in config.allowedBroadcastIds:
            context.user_data['awaiting_broadcast_message'] = True
            await update.message.reply_text('Введите сообщение для рассылки:')
            logger.debug('Ожидаем ввода сообщения для broadcast')
        else:
            logger.warning(f'Пользователь {update.effective_user.id} не разрешен для отправки broadcast сообщений')
            await update.message.reply_text(text='У вас нет прав для этой команды.',
                                            reply_markup=ReplyKeyboardRemove())
    elif 'awaiting_broadcast_message' in context.user_data:
        await send_broadcast(update, context)
        logger.info('Cообщение broadcast отправлено')
    else:
        logger.info('Создание обращения')
        await create_issue(update, context)


# Обработка событий новых участников
async def membership_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info('Обработка события нового участника')
    member_data = update.my_chat_member.new_chat_member
    status = member_data.status
    chat_id = update.my_chat_member.chat.id
    chat_title = update.my_chat_member.chat.title
    if status == "member":
        # Приветственное сообщение при добавлении бота в группу
        await send_welcome_message(update, context)
        # Добавление бота в список участников группы
        # для дальнейшего использования в отправке broadcast сообщений
        logger.info(f'Бот был добавлен в группу {chat_id} {chat_title}')
        add_bot_membership({str(chat_id): chat_title})
    elif status in ["left", "kicked"]:
        logger.info(f'Бот был удален из группы {chat_id} {chat_title}')
        remove_bot_membership(chat_id)

    # # Приветственное сообщение при добавлении бота в группу
    # if member_data.status == 'member' and member_data.user.id == context.bot.id:
    #     await welcome_message(update, context)


def main() -> None:
    application = Application.builder().token(config.token).build()

    handlers = [
        ChatMemberHandler(membership_handler, ChatMemberHandler.MY_CHAT_MEMBER),
        CommandHandler('start', start),
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler),
        CallbackQueryHandler(buttons_issue_handler)
    ]

    for handler in handlers:
        application.add_handler(handler)

    application.run_polling()


if __name__ == '__main__':
    main()
