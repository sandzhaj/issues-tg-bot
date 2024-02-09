import json
from src.logger import get_logger

logger = get_logger(__name__)


def add_bot_membership(chat_data: dict[str, str]):
    """Добавление бота в список участников группы."""
    try:
        with open('bot_membership.json', 'r') as file:
            bot_membership = json.load(file)
            logger.debug(f'Файл bot_membership.json загружен. {bot_membership}')
    except FileNotFoundError:
        logger.debug('Файл bot_membership.json не найден. Создаем новый.')
        bot_membership = {}
    bot_membership.update(chat_data)
    logger.debug(f'Обновленный список участников: {bot_membership}')
    with open('bot_membership.json', 'w') as file:
        json.dump(bot_membership, file, ensure_ascii=False, indent=4)
    logger.debug('Файл bot_membership.json обновлен.')


def remove_bot_membership(chat_id: int):
    """Удаление бота из списка участников группы."""
    try:
        with open('bot_membership.json', 'r') as file:
            bot_membership = json.load(file)
            logger.debug(f'Файл bot_membership.json загружен. {bot_membership}')
    except FileNotFoundError:
        logger.debug('Файл bot_membership.json не найден. Создаем новый.')
        bot_membership = {}
    bot_membership.pop(str(chat_id), None)
    logger.debug(f'Обновленный список участников: {bot_membership}')
    with open('bot_membership.json', 'w') as file:
        json.dump(bot_membership, file, ensure_ascii=False)
    logger.debug('Файл bot_membership.json обновлен.')


def get_chat_id_list():
    try:
        with open('bot_membership.json', 'r') as file:
            bot_membership = json.load(file)
            logger.debug(f'Файл bot_membership.json загружен. {bot_membership}')
    except FileNotFoundError:
        logger.debug('Файл bot_membership.json не найден. Создаем новый.')
        bot_membership = {}
    return list(bot_membership.keys())
