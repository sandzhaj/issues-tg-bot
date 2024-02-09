import os
import yaml
from dataclasses import dataclass
from src.UI import Ui

@dataclass
class Person:
    login: str
    id: int = None
    name: str = None


class Config:
    def __init__(self):
        root_dir = os.path.dirname(os.path.realpath('main.py'))
        file_path = os.path.join(root_dir, "config.yaml")
        with open(file_path, 'r') as yaml_file:
            data = yaml.safe_load(yaml_file)

        self.targetChatId = data["targetChatId"]
        self.token = data["token"]
        self.team = [Person(**person) for person in data["team"]]
        self.mentions = [p.login for p in self.team]
        self.allowedBroadcastIds = [p.id for p in self.team if p.id]
        self.ui = Ui(data["ui"])

    def get_person_by_id(self, id_num: int):
        for person in self.team:
            if person.id == id_num:
                return person
        return None


config = Config()