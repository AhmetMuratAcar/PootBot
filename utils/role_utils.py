import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
JSON_PATH = os.path.join(DATA_DIR, "roles.json")


def save_inputs(role_name: str, emoji: str):
    """Adds role and emoji to JSON file"""
    # Check if the JSON file exists, if not, create an empty dictionary
    if not os.path.exists(JSON_PATH):
        roles_data = {}
    else:
        # Load existing data from the JSON file
        with open(JSON_PATH, 'r') as file:
            try:
                roles_data = json.load(file)
            except json.JSONDecodeError:
                roles_data = {}

    # Add the role and emoji to the dictionary
    roles_data[role_name] = emoji

    # Write the updated data back to the JSON file
    with open(JSON_PATH, 'w') as file:
        json.dump(roles_data, file, indent=4)

    print(f"Saved role {role_name} with emoji {emoji} to {JSON_PATH}")


def emoji_check(emoji: str):
    """Checks if emoji chosen by user is already being used."""
    pass


def role_check(role: str):
    """Checks if role name chosen by user is already being used."""
    pass
