import copy
from pprint import pprint

import requests
import json
import os
from urllib3.exceptions import InsecureRequestWarning
import warnings
warnings.filterwarnings('ignore', category=InsecureRequestWarning)  # Optional: suppress SSL warnings


NEXTCLOUD_URL = "https://nc.uni-bremen.de"
NEXTCLOUD_LOGIN = os.environ["NEXTCLOUD_LOGIN"]
NEXTCLOUD_APP_PASSWORD = os.environ["DEADLINE_REMINDER_NEXTCLOUD_APP_PASSWORD"]
BOARD_ID = 3139

NEXTCLOUD_USER_URL = f"{NEXTCLOUD_URL}/index.php/apps/deck/board/{BOARD_ID}"

BASE_API = f'{NEXTCLOUD_URL}/index.php/apps/deck/api/v1.0'
AUTH = (NEXTCLOUD_LOGIN, NEXTCLOUD_APP_PASSWORD)
HEADERS = {'OCS-APIRequest': 'true', 'Accept': 'application/json'}


def get(u, p=None):
    r = requests.get(u, auth=AUTH, params=p, verify=False)
    return r.json() if r.ok else None

def fetch_work_stack():
    stacks = get(f'{BASE_API}/boards/{BOARD_ID}/stacks', {'includeAssignedUsers': 1})

    work_stacks = {
        "TODO": [],
        "In Work": [],
        # "Done": []
    }

    #pprint(stacks)

    for s in stacks:
        title = s["title"]
        if title in work_stacks:
            for c in s.get("cards", []):
                card = {
                    "title": c["title"],
                    "id": c["id"],
                    "assignedUsers": [],
                    "duedate": c.get("duedate")
                }

                for u in c["assignedUsers"]:
                    card["assignedUsers"].append(u["participant"]["uid"])

                work_stacks[title].append(card)

    return work_stacks

#fetch_work_stack()