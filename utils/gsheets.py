import json
import os
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials


def get_project_root() -> str:
    return str(Path(__file__).parent.parent)


def create_json(section, file_name=None):
    gs_key_file = get_project_root() + f"/{file_name if file_name else section}.json"
    if not os.path.isfile(gs_key_file):
        config_file = get_project_root() + "/config.json"
        with open(config_file) as json_file:
            data = json.load(json_file)[section]
        with open(gs_key_file, 'w') as fp:
            json.dump(data, fp)
    return gs_key_file


def get_data(file_name, section):
    config_file = get_project_root() + f"/{file_name}.json"
    with open(config_file) as json_file:
        return json.load(json_file)[section]


class GoogleSheets:
    gs_key_file = create_json('email_key')
    data_columns = {'id': 'A',
                    'email': 'B',
                    'password': 'C',
                    'used_germany': 'D'}

    def __init__(self, name):
        self.ws = self.authorize(name)

    def authorize(self, work_sheet):
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(self.gs_key_file, scopes=scope)
        gs = gspread.authorize(creds).open_by_key('1aYR6tN9BygDJLOVmKkXKAxDkJtxuH1nh6J6pjmHPBNo')
        return gs.worksheet(work_sheet)

    def find_item_by_id(self, visa_item_id):
        cell = self.ws.row_values(visa_item_id + 1)
        return cell

    def update_visa_item_by_id(self, id, column, value):
        self.ws.update_acell("{}{}".format(self.data_columns[column], int(id) + 1), value)
