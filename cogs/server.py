import discord
from discord import app_commands
from discord.ext import commands

from checks import is_admin
from utils import send_rcon


class ServerCog(commands.Cog, name='Server'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='status', description='Show server statistics (players, FPS, memory, world info)')
    @is_admin()
    async def status(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await send_rcon(interaction, 'serverStats')

    @app_commands.command(name='time', description='Show current server time and in-game day')
    @is_admin()
    async def time(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await send_rcon(interaction, 'time')

    @app_commands.command(name='logs', description='Get the last 5 lines of the server log')
    @is_admin()
    async def logs(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await send_rcon(interaction, 'logs')

    @app_commands.command(name='players', description='Show all currently online players with their positions')
    @is_admin()
    async def players(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await send_rcon(interaction, 'players')

    @app_commands.command(name='list', description='List all available RCON commands on the server')
    @is_admin()
    async def list_commands(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await send_rcon(interaction, 'list')


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerCog(bot))
