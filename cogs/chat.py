import discord
from discord import app_commands
from discord.ext import commands

from checks import is_admin
from utils import send_rcon


class ChatCog(commands.Cog, name='Chat'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='say', description='Send a shout message to all players in global chat')
    @app_commands.describe(message='Message to broadcast')
    @is_admin()
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()
        await send_rcon(interaction, f'say {message}')

    @app_commands.command(name='showmessage', description='Display a message in the centre of all players\' screens')
    @app_commands.describe(message='Message to display')
    @is_admin()
    async def showmessage(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()
        await send_rcon(interaction, f'showMessage {message}')

    @app_commands.command(name='ping', description='Send a map ping to all players at the given coordinates')
    @app_commands.describe(x='X coordinate', y='Y coordinate', z='Z coordinate')
    @is_admin()
    async def ping(self, interaction: discord.Interaction, x: float, y: float, z: float):
        await interaction.response.defer()
        await send_rcon(interaction, f'ping {x} {y} {z}')


async def setup(bot: commands.Bot):
    await bot.add_cog(ChatCog(bot))
