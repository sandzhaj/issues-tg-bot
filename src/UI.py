from dataclasses import dataclass
from jinja2 import Template
from src.logger import get_logger

logger = get_logger(__name__)


def render(template: str, **kwargs) -> str:
    logger.debug(f'Рендер шаблона: {template}')
    return Template(template).render(**kwargs)


@dataclass
class ButtonsUi:
    broadcast: str
    issueAssign: str
    issueClose: str
    issueCommon: str


@dataclass
class MessagesUi:
    welcome: str
    broadcastSuccess: str
    createIssueReply: str
    createIssueReplyFromDirectAppend: str
    assignIssueReply: str
    assignIssueStatus: str
    resolveCommonReply: str
    resolveCommonStatus: str
    resolveReply: str
    resolveStatus: str
    privateMessageSource: str

class Ui:
    def __init__(self, data: dict):
        self.buttons = ButtonsUi(**data['buttons'])
        self.messages = MessagesUi(**data['messages'])
        self.issue = data['issue']
