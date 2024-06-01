import discord
import os
import sqlite3
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands

# Loading .env
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

# Creating instance
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    guild = discord.Object(id=857676061664083978)
    await bot.tree.sync(guild=guild)


# Commands
@bot.tree.command(
    name="setup_master_message", 
    description="Setup the master message in a specified channel",
)
@app_commands.checks.has_permissions(administrator = True)
async def setup_master_message(interaction: discord.Interaction, channel: discord.TextChannel):
    # Connect to the database
    conn = sqlite3.connect('PootBot.db')
    cursor = conn.cursor()

    # Fetch all games from the database
    cursor.execute("SELECT game, role, emoji FROM games")
    games = cursor.fetchall()
    conn.close()

    # Construct the message content
    message_content = "Welcome to the server! Here are the current games, roles, and emojis:\n"
    for game, role, emoji in games:
        message_content += f"{emoji} - {game} (Role: {role})\n"

    # Send the message to the specified channel
    master_message = await channel.send(message_content)

    # Add each emoji as a reaction to the message
    for game, role, emoji in games:
        try:
            await master_message.add_reaction(emoji)
        except discord.HTTPException:
            continue  # If the emoji is invalid or can't be used, skip it

    await interaction.response.send_message(f"Master message setup in {channel.mention}", ephemeral=True)


bot.run(os.getenv('TOKEN'))
