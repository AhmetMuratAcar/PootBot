import discord
import json
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from utils.message_utils import save_message_id, existence_check, load_message_id, update_master_message
from utils.role_utils import save_inputs, emoji_check, role_check, format_roles_content, load_roles_json, JSON_PATH

# Loading .env
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

# Creating instance
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.tree.sync()

    try:
        # Attempt to load the master message data
        master_data = load_message_id()  # Load message data from master_message.json
        if master_data and 'channel_id' in master_data and 'message_id' in master_data:
            channel = bot.get_channel(master_data['channel_id'])
            bot.master_message = await channel.fetch_message(master_data['message_id'])
            print(f'Master message re-fetched: {bot.master_message.id}')
        else:
            bot.master_message = None  # No master message is set
            print("No master message set up.")
    except Exception as e:
        bot.master_message = None
        print(f"Error fetching master message: {e}")


# ----------Commands----------
@bot.tree.command(
    name="setup_master_message",
    description="Cretes message that will be used to control roles in the give channel",
)
@app_commands.checks.has_permissions(administrator=True)
async def setup_master_message(interaction: discord.Interaction, channel: discord.TextChannel):
    """Creates master message which will be used for creating and assigning roles."""
    # Check if a master message is already set up
    master_check, reason = await existence_check(interaction)
    if master_check:
        data = load_message_id()
        message_url = f"https://discord.com/channels/{interaction.guild.id}/{data['channel_id']}/{data['message_id']}"
        await interaction.response.send_message(
            f"Master message already exists at: {message_url}", 
            ephemeral=True
        )
        return

    # Telling user whats happening
    if reason == "channel":
        await interaction.response.send_message(
            f"Old master message's channel was deleted, setting up new one.", 
            ephemeral=True
            )
    elif reason == "message":
        await interaction.response.send_message(
            f"Old master message was deleted, setting up new one.", 
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"Creating master message . . .", 
            ephemeral=True
        )

    # Construct the message content
    message_content = ("**Hello** :point_up: :nerd:\n\n"
                       "\> Below are the currently available roles.\n"
                       "\> Interact with the emojis to add/remove roles from yourself.\n"
                       "\> If you want to add a role use the `/add_role` function and pass in the role name and emoji you want.\n"
                       "\> Only admins can use the `/remove_role` function."
                       )

    # Send the message to the specified channel and save its data as JSON
    master_message = await channel.send(message_content)
    save_message_id(master_message.id, channel.id)

    await interaction.response.send_message(f"Master message setup in {channel.mention}", ephemeral=True)


@setup_master_message.error
async def setup_master_message_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Send an ephemeral message if the user lacks admin permissions"""
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "You do not have the required permissions (Administrator) to run this command.",
            ephemeral=True
        )


@bot.tree.command(
    name="add_role",
    description="Adds role and corresponding emoji to the master message"
)
async def add_role(interaction: discord.Interaction, role_name: str, emoji: str):
    """Adds role and emoji to master message."""
    # Checking if master message exists
    master_check, reason = await existence_check(interaction)
    if not master_check:
        await interaction.response.send_message(
            "A master message must first be set up using the `/setup_master_message` command",
            ephemeral=True
        )
        return
    
    # Check if role or emoji are already used
    role_used = role_check(role_name, interaction.guild)  # True if invalid role
    if role_used:
        await interaction.response.send_message(
            "The role name you entered is already being used.",
            ephemeral=True
        )
        return

    emoji_used = await emoji_check(emoji, interaction.guild)  # True if valid emoji
    if not emoji_used:
        await interaction.response.send_message(
            "The emoji you entered is either invalid or already being used.",
            ephemeral=True
        )
        return

    # Updating roles JSON with new role name and emoji
    save_inputs(role_name, emoji)

    # Grabbing master message content for editing
    data = load_message_id()
    channel = interaction.guild.get_channel(data['channel_id'])
    master_message = await channel.fetch_message(data['message_id'])

    # Reconstructing master message
    updated_roles_content = await format_roles_content()
    await update_master_message(interaction.guild, updated_roles_content)

    # Creating the new role and adding reaction emoji
    random_color = discord.Color.random()
    await interaction.guild.create_role(name=role_name, color=random_color)
    await master_message.add_reaction(emoji)

    # Notifying the user
    await interaction.response.send_message(
        f"Role {role_name} with emoji {emoji} added to the master message!",
        ephemeral=True
    )


@bot.tree.command(
    name="remove_role",
    description="Removes chosen role from the master message and server",
)
@app_commands.checks.has_permissions(administrator=True)
async def remove_role(interaction: discord.Interaction, role_name: str):
    # Load roles data from roles.json
    roles_data = load_roles_json()

    # Check if the role exists in roles.json
    if role_name not in roles_data:
        await interaction.response.send_message(
            f"The role '{role_name}' is not valid or does not exist in the master message.",
            ephemeral=True
        )
        return

    # Grab emoji and remove the role from roles.json
    emoji = roles_data[role_name]
    del roles_data[role_name]

    # Save the updated roles.json
    with open(JSON_PATH, 'w') as file:
        json.dump(roles_data, file, indent=4)

    # Grabbing master message content for editing
    data = load_message_id()  # Assuming this loads the master message ID and channel ID
    channel = interaction.guild.get_channel(data['channel_id'])
    master_message = await channel.fetch_message(data['message_id'])

    # Rebuild the master message content without the deleted role
    updated_roles_content = await format_roles_content()
    await update_master_message(interaction.guild, updated_roles_content)

    # Removing emoji reaction
    await master_message.clear_reaction(emoji)

    # Delete the role from the server
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    if role:
        await role.delete()

    # Notify the user
    await interaction.response.send_message(
        f"The role '{role_name}' has been removed from the master message and the server.",
        ephemeral=True
    )


@remove_role.error
async def setup_master_message_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Send an ephemeral message if the user lacks admin permissions"""
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "You do not have the required permissions (Administrator) to run this command.",
            ephemeral=True
        )


# ----------Events----------
@bot.event
async def on_raw_reaction_add(payload):
    if bot.master_message and payload.message_id == bot.master_message.id:
        roles_data = load_roles_json()  # Load emoji-to-role mapping from roles.json
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        
        for role_name, emoji in roles_data.items():
            if str(payload.emoji) == emoji:
                role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    await member.add_roles(role)
                    print(f"Added {role.name} to {member.name}")
                    break


@bot.event
async def on_raw_reaction_remove(payload):
    if bot.master_message and payload.message_id == bot.master_message.id:
        roles_data = load_roles_json()  # Load emoji-to-role mapping from roles.json
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        
        for role_name, emoji in roles_data.items():
            if str(payload.emoji) == emoji:
                role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    await member.remove_roles(role)
                    print(f"Removed {role.name} from {member.name}")
                    break

if __name__ == "__main__":
    bot.run(os.getenv('TOKEN'))
