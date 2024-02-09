import json
from dataclasses import dataclass, asdict
from src.logger import get_logger
from src.config import config
from src.UI import render

logger = get_logger(__name__)


def load_issues(filename='issues.json') -> dict[int, 'Issue']:
    """Загружает все обращения и последний ID из файла JSON."""
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            logger.debug(f'Файл {filename} загружен.')
            return {int(k): Issue.from_dict(v) for k, v in data.items()}
    except FileNotFoundError:
        logger.debug(f'Файл {filename} не найден. Создаем новый.')
        return {}


def get_last_id(issues_list):
    last_id = max(issues_list.keys(), default=0)
    logger.debug(f'Последний ID: {last_id}')
    return last_id


def find_issue_by_message_id(issues_list, message_id):
    """Находит первый объект Issue с указанным messageId."""
    for issue in issues_list.values():
        if issue.messageId == message_id:
            logger.debug(f'Обращение с messageId {message_id} найдено: Issue №{issue.id}')
            return issue
    return None


def save_issues(issues_list, filename='issues.json'):
    """Сохраняет все обращения и последний ID в файл JSON."""
    with open(filename, 'w') as file:
        logger.debug(f'Сохранение обращений в файл {filename}')
        json.dump(issues_list, file, ensure_ascii=False, indent=4, default=lambda o: o.to_dict())


def remove_old_issues(current_issue, issues_list):
    """Удаляет закрытые обращения из списка, кроме последнего."""
    keys_to_remove = []  # Список для хранения ключей (ID) обращений, которые нужно удалить
    # Проверяем и обновляем статус текущего обращения
    if current_issue.id != get_last_id(issues_list):
        keys_to_remove.append(current_issue.id)
    else:
        current_issue.status = "closed"
    # Добавляем закрытые обращения в список на удаление, кроме последнего
    for issue_id, data in issues_list.items():
        if data.status == "closed" and issue_id != get_last_id(issues_list):
            keys_to_remove.append(issue_id)
    # Удаляем обращения после итерации
    logger.debug(f'Удаляем закрытые обращения: {keys_to_remove}')
    for key in keys_to_remove:
        del issues_list[key]
    save_issues(issues_list)


@dataclass
class Issue:
    message: str
    author: str
    source: str
    isDirectMsg: bool
    id: int = None
    messageId: str = None
    issueMsg: str = None
    createIssueReply: str = None
    resolveCommonReply: str = None
    resolveReply: str = None
    status: str = "open"

    def __post_init__(self):
        if not self.id:
            issues_list = load_issues()
            self.id = get_last_id(issues_list) + 1
        self.createIssueReply = render(config.ui.messages.createIssueReply, issue=self)
        if self.isDirectMsg:
            self.source = config.ui.messages.privateMessageSource
            self.createIssueReply += render(config.ui.messages.createIssueReplyFromDirectAppend, issue=self)
        if self.author:
            self.author = self.escape_md_v2(self.author)
        if self.source:
            self.source = self.escape_md_v2(self.source)
        self.issueMsg = render(config.ui.issue, issue=self)
        self.resolveCommonReply = render(config.ui.messages.resolveCommonReply, issue=self)
        self.resolveReply = render(config.ui.messages.resolveReply, issue=self)
        logger.debug(f'Инициализировано обращение: {self.id}')

    def to_dict(self):
        """Сериализует объект в словарь."""
        return asdict(self)

    @staticmethod
    def escape_md_v2(text):
        escape_chars = '_[]()~`>#+-=|{}.!'
        return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

    @staticmethod
    def from_dict(data):
        """Создает объект из словаря."""
        return Issue(**data)
