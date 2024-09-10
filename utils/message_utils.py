import json
import os
import discord

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

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


def delete_message_id():
    if os.path.exists(JSON_PATH):
        os.remove(JSON_PATH)


async def existence_check(interaction: discord.Interaction):
    """Goes through the various possibilities of master message's existance."""
    data = load_message_id()
    # If the path does not exist terminate early
    if not data:
        return False, None

    # If the data exist but the message no longer exists
    try:
        # Fetch the channel from the saved channel_id
        channel = interaction.guild.get_channel(data['channel_id'])

        # The channel no longer exists
        if not channel:
            delete_message_id()
            return False, "channel"

        # Try to fetch the master message using the saved message_id
        await channel.fetch_message(data['message_id'])

        # If you get here the message and channel exist.
        return True, None
    
    except:
        delete_message_id()
        return False, "message"


async def update_master_message(guild: discord.Guild, updated_roles_content: str):
    """Fetches the master message and updates it with new content."""
    # Load the master message and channel data
    data = load_message_id()
    channel = guild.get_channel(data['channel_id'])
    master_message = await channel.fetch_message(data['message_id'])

    # Construct the updated master message content
    message_header = (
        "**Hello** :point_up: :nerd:\n\n"
        "\> Below are the currently available game roles.\n"
        "\> Interact with the emojis to add/remove roles from yourself.\n"
        "\> If you want to add a game, use the `/add_game` function and pass in the role name and emoji you want.\n"
    )
    new_message_content = f"{message_header}\n{updated_roles_content}"

    # Update the master message with the new content
    await master_message.edit(content=new_message_content)
