import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from utils.message_utils import save_message_id, existence_check, load_message_id
from utils.role_utils import save_inputs, emoji_check, role_check, format_roles_content, load_roles_json

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


# Commands
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
    message_header = ("**Hello** :point_up: :nerd:\n\n"
                    "\> Below are the currently available roles.\n"
                    "\> Interact with the emojis to add/remove roles from yourself.\n"
                    "\> If you want to add a role use the `/add_role` function and pass in the role name and emoji you want.\n"
                    "\> Only admins can use the `/remove_role` function."
                    )
    updated_roles_content = await format_roles_content()
    new_content = f"{message_header}```\n{updated_roles_content}\n```"
    await master_message.edit(content=new_content)

    # Creating the new role and adding reaction emoji
    await interaction.guild.create_role(name=role_name)
    await master_message.add_reaction(emoji)

    # Notifying the user
    await interaction.response.send_message(
        f"Role {role_name} with emoji {emoji} added to the master message!",
        ephemeral=True
    )


# TODO: implement remove_role
@bot.tree.command(
    name="remove_role",
    description="Removes chosen role from the master message and server",
)
@app_commands.checks.has_permissions(administrator=True)
async def remove_role(interaction: discord.Interaction, role_name: str):
    pass


@remove_role.error
async def setup_master_message_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Send an ephemeral message if the user lacks admin permissions"""
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "You do not have the required permissions (Administrator) to run this command.",
            ephemeral=True
        )


# Events
@bot.event
async def on_reaction_add(reaction, user):
    """Assign a role to a user when they react with the corresponding emoji to the master message."""
    # Ignore bot reactions
    if user.bot:
        return

    # Load the master message ID and roles data from roles.json
    data = load_message_id()
    roles_data = load_roles_json()

    # Check if the reaction is on the master message
    if reaction.message.id != data['message_id']:
        return

    # Check if the emoji used in the reaction corresponds to a role
    emoji = str(reaction.emoji)  # Convert the reaction emoji to string
    if emoji in roles_data.values():
        # Get the corresponding role name
        role_name = next(role for role, emoji_value in roles_data.items() if emoji_value == emoji)

        # Find the role object on the server
        role = discord.utils.get(reaction.message.guild.roles, name=role_name)

        # Add the role to the user
        if role:
            await user.add_roles(role)
            await user.send(f"You have been given the role: {role_name}")


@bot.event
async def on_reaction_remove(reaction, user):
    """Remove a role from a user when they remove the corresponding emoji reaction from the master message."""
    # Ignore bot reactions
    if user.bot:
        return

    # Load the master message ID and roles data from roles.json
    data = load_message_id()
    roles_data = load_roles_json()

    # Check if the reaction is on the master message
    if reaction.message.id != data['message_id']:
        return

    # Check if the emoji used in the reaction corresponds to a role
    emoji = str(reaction.emoji)  # Convert the reaction emoji to string
    if emoji in roles_data.values():
        # Get the corresponding role name
        role_name = next(role for role, emoji_value in roles_data.items() if emoji_value == emoji)

        # Find the role object on the server
        role = discord.utils.get(reaction.message.guild.roles, name=role_name)

        # Remove the role from the user
        if role:
            await user.remove_roles(role)
            await user.send(f"You have been removed from the role: {role_name}")


if __name__ == "__main__":
    bot.run(os.getenv('TOKEN'))
