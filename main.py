import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from utils.message_utils import save_message_id, existence_check, load_message_id

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
    # Check if a master message is already set up
    masterCheck = await existence_check(interaction)
    if masterCheck:
        data = load_message_id()
        existing_channel = interaction.guild.get_channel(data['channel_id'])
        await interaction.response.send_message(
            f"Master message already exists in {existing_channel.mention}", 
            ephemeral=True
        )
        return

    # Construct the message content
    message_content = ("**Hello** :point_up: :nerd:\n\n"
                       "\> Below are the currently available game roles.\n"
                       "\> Interact with the emojis to add/remove roles from yourself.\n"
                       "\> If you want to add a game use the `/add game` function and pass in the game name and emoji you want."
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


if __name__ == "__main__":
    bot.run(os.getenv('TOKEN'))
