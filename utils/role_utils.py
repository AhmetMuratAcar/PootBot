import json
import os
import discord
import re

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


async def emoji_check(emoji: str, guild: discord.Guild) -> bool:
    """Checks if emoji chosen by user is valid and not being used already."""
    # Check if it's a valid Unicode emoji using Discord's built-in function
    try:
        await guild.fetch_emoji(int(emoji.strip('<:a:>')))  # Trying to fetch a custom emoji
        is_custom_emoji = True
    except (ValueError, discord.NotFound):
        # Not a custom emoji, check if it's a valid Unicode emoji
        is_custom_emoji = False

    if not is_custom_emoji:
        # Validate if it's a standard Unicode emoji
        emoji_pattern = re.compile(
            "["  
            "\U0001F600-\U0001F64F"  # Emoticons
            "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
            "\U0001F680-\U0001F6FF"  # Transport & Map
            "\U0001F700-\U0001F77F"  # Alchemical Symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"
            "]+", 
            flags=re.UNICODE
        )
        
        # Check if it's a valid Unicode emoji
        if not emoji_pattern.match(emoji):
            return False

    # Check if the emoji is already used in roles.json
    if not os.path.exists(JSON_PATH):
        return True  # If file doesn't exist, emoji hasn't been used yet

    with open(JSON_PATH, 'r') as file:
        try:
            roles_data = json.load(file)
        except json.JSONDecodeError:
            roles_data = {}

    return emoji not in roles_data.values()


def role_check(role: str, guild: discord.Guild) -> bool:
    """Checks if role name chosen by user is already being used."""
    # Check if the role is already being used in the server
    existing_role = discord.utils.get(guild.roles, name=role)
    if existing_role:
        return True

    # Check if role exists in roles.json
    if not os.path.exists(JSON_PATH):
        return False
    
    with open(JSON_PATH, 'r') as file:
        try:
            roles_data = json.load(file)
        except json.JSONDecodeError:
            roles_data = {}

    return role in roles_data


async def format_roles_content() -> str:
    """
    Reads the roles.json file and formats the roles and emojis
    into a structured list within a code block.
    """
    if not os.path.exists(JSON_PATH):
        return

    with open(JSON_PATH, 'r') as file:
        try:
            roles_data = json.load(file)
        except json.JSONDecodeError:
            roles_data = {}

    # Format the roles and emojis into a text block
    formatted_roles = []
    for role, emoji in roles_data.items():
        formatted_roles.append(f"{emoji} - {role}")

    # Join all the role-emoji pairs into a string
    return "\n".join(formatted_roles)


def load_roles_json():
    """Loads the roles and emoji data from roles.json."""
    if not os.path.exists(JSON_PATH):
        return {}

    with open(JSON_PATH, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}
