import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from utils.msgJSON import save_message_id, load_message_id

# Loading .env
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

# Creating instance
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    guild = discord.Object(id=os.getenv('GUILD_ID'))
    await bot.tree.sync(guild=guild)


# Commands
@bot.tree.command(
    name="setup_master_message",
    description="Setup the master message in a specified channel",
)
@app_commands.checks.has_permissions(administrator=True)
async def setup_master_message(interaction: discord.Interaction, channel: discord.TextChannel):

    # Construct the message content
    message_content = "Welcome to the server! Here are the current games, roles, and emojis:\n"

    # Send the message to the specified channel and save its data as JSON
    master_message = await channel.send(message_content)
    save_message_id(master_message.id, channel.id)

    await interaction.response.send_message(f"Master message setup in {channel.mention}", ephemeral=True)

@setup_master_message.error
async def setup_master_message_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """ Send an ephemeral message if the user lacks admin permissions """
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "You do not have the required permissions (Administrator) to run this command.",
            ephemeral=True
        )


if __name__ == "__main__":
    bot.run(os.getenv('TOKEN'))
