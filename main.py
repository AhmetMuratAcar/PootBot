import discord
from discord import app_commands
import os
from dotenv import load_dotenv

# Loading .env
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

# Creating client instance
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

current_game = "No game selected"

@client.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {client.user.name}')


# Commanmds
@tree.command(
    name="current-flavor",
    description="Display the current flavor of the month game."
)
async def current_flavor(interaction: discord.Interaction):
    """Sends message displaying the current game."""
    await interaction.response.send_message(f"The current flavor of the month is: **{current_game}**")


@tree.command(
    name = "change-flavor",
    description = "Change the flavor of the month game."
)
async def change_flavor(interaction: discord.Interaction, new_game: str):
    """
    Input: new game title <string>
    Notifies previous users of flavor change, removes them, and sends new flavor message.
    """
    global current_game
    if current_game == new_game:
        await interaction.response.send_message("That is already the current flavor of the month.")
        return

    current_game = new_game

    role_name = "Current Flavor"
    guild = interaction.guild
    role = discord.utils.get(guild.roles, name=role_name)

    if not role:
        role = await guild.create_role(name=role_name)

    # Notify and clear previous members
    await interaction.response.send_message(f"{role.mention} flavor changing 🤖", allowed_mentions=discord.AllowedMentions(roles=True))
    for member in role.members:
        await member.remove_roles(role)
    
    # Send a follow-up message regarding the new game and adding a reaction
    message = await interaction.followup.send(f"The flavor of the month game has been changed to **'{new_game}'**. If you want to be notified, click the check mark.")
    await message.add_reaction('✅')

    # Listener for reaction adds
    @client.event
    async def on_raw_reaction_add(payload):
        # Check if the reaction is to the correct message, correct emoji, and add role
        if payload.message_id == message.id and str(payload.emoji) == '✅':
            member = guild.get_member(payload.user_id)
            if member and not member.bot:
                await member.add_roles(role)

    # Listener for reaction removals
    @client.event
    async def on_raw_reaction_remove(payload):
        # Check if the reaction removed is from the correct message, correct emoji, and remove role
        if payload.message_id == message.id and str(payload.emoji) == '✅':
            member = guild.get_member(payload.user_id)
            if member and not member.bot:
                await member.remove_roles(role)


client.run(os.getenv('TOKEN'))
