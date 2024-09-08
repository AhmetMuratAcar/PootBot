import json
import os

DATA_DIR = DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# Making sure data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

JSON_PATH = os.path.join(DATA_DIR, "master_message.json")


def save_message_id(message_id: int, channel_id: int):
    data = {
        "message_id": message_id,
        "channel_id": channel_id
    }

    with open(JSON_PATH, "w") as f:
        json.dump(data, f)


def load_message_id():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r") as f:
            return json.load(f)
    
    return None

