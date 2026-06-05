from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from checks import is_admin
from utils import send_rcon


class PlayersCog(commands.Cog, name='Players'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── Kick / Ban ────────────────────────────────────────────────────────────

    @app_commands.command(name='kick', description='Kick a player from the server')
    @app_commands.describe(player='Player name or Steam ID')
    @is_admin()
    async def kick(self, interaction: discord.Interaction, player: str):
        await interaction.response.defer()
        await send_rcon(interaction, f'kick {player}')

    @app_commands.command(name='ban', description='Ban a player by name or Steam ID')
    @app_commands.describe(player='Player name or Steam ID')
    @is_admin()
    async def ban(self, interaction: discord.Interaction, player: str):
        await interaction.response.defer()
        await send_rcon(interaction, f'ban {player}')

    @app_commands.command(name='ban_steamid', description='Ban a player by their Steam ID')
    @app_commands.describe(steamid='64-bit Steam ID')
    @is_admin()
    async def ban_steamid(self, interaction: discord.Interaction, steamid: str):
        await interaction.response.defer()
        await send_rcon(interaction, f'banSteamId {steamid}')

    @app_commands.command(name='unban', description='Unban a player by name or Steam ID')
    @app_commands.describe(player='Player name or Steam ID')
    @is_admin()
    async def unban(self, interaction: discord.Interaction, player: str):
        await interaction.response.defer()
        await send_rcon(interaction, f'unban {player}')

    @app_commands.command(name='disconnectall', description='Disconnect all currently connected players')
    @is_admin()
    async def disconnectall(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await send_rcon(interaction, 'disconnectAll')

    # ── Admin list ────────────────────────────────────────────────────────────

    @app_commands.command(name='adminlist', description='Show the list of server administrators')
    @is_admin()
    async def adminlist(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await send_rcon(interaction, 'adminlist')

    @app_commands.command(name='addadmin', description='Add a player to the admin list')
    @app_commands.describe(steamid='64-bit Steam ID')
    @is_admin()
    async def addadmin(self, interaction: discord.Interaction, steamid: str):
        await interaction.response.defer()
        await send_rcon(interaction, f'addAdmin {steamid}')

    @app_commands.command(name='removeadmin', description='Remove a player from the admin list')
    @app_commands.describe(steamid='64-bit Steam ID')
    @is_admin()
    async def removeadmin(self, interaction: discord.Interaction, steamid: str):
        await interaction.response.defer()
        await send_rcon(interaction, f'removeAdmin {steamid}')

    # ── Permitted list ────────────────────────────────────────────────────────

    @app_commands.command(name='banlist', description='Show the list of banned players')
    @is_admin()
    async def banlist(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await send_rcon(interaction, 'banlist')

    @app_commands.command(name='permitted', description='Show the list of permitted players')
    @is_admin()
    async def permitted(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await send_rcon(interaction, 'permitted')

    @app_commands.command(name='addpermitted', description='Add a player to the permitted list')
    @app_commands.describe(steamid='64-bit Steam ID')
    @is_admin()
    async def addpermitted(self, interaction: discord.Interaction, steamid: str):
        await interaction.response.defer()
        await send_rcon(interaction, f'addPermitted {steamid}')

    @app_commands.command(name='removepermitted', description='Remove a player from the permitted list')
    @app_commands.describe(steamid='64-bit Steam ID')
    @is_admin()
    async def removepermitted(self, interaction: discord.Interaction, steamid: str):
        await interaction.response.defer()
        await send_rcon(interaction, f'removePermitted {steamid}')

    # ── Player interaction ────────────────────────────────────────────────────

    @app_commands.command(name='findplayer', description='Find a player and show their details')
    @app_commands.describe(player='Player name or Steam ID')
    @is_admin()
    async def findplayer(self, interaction: discord.Interaction, player: str):
        await interaction.response.defer()
        await send_rcon(interaction, f'findPlayer {player}')

    @app_commands.command(name='heal', description='Heal a player to the specified health value')
    @app_commands.describe(steamid='64-bit Steam ID', amount='Health value to restore to')
    @is_admin()
    async def heal(self, interaction: discord.Interaction, steamid: str, amount: int):
        await interaction.response.defer()
        await send_rcon(interaction, f'heal {steamid} {amount}')

    @app_commands.command(name='damage', description='Damage a player by the specified amount')
    @app_commands.describe(steamid='64-bit Steam ID', amount='Damage amount')
    @is_admin()
    async def damage(self, interaction: discord.Interaction, steamid: str, amount: int):
        await interaction.response.defer()
        await send_rcon(interaction, f'damage {steamid} {amount}')

    @app_commands.command(name='teleport', description='Teleport a player to the specified coordinates')
    @app_commands.describe(steamid='64-bit Steam ID', x='X coordinate', y='Y coordinate', z='Z coordinate')
    @is_admin()
    async def teleport(self, interaction: discord.Interaction, steamid: str, x: float, y: float, z: float):
        await interaction.response.defer()
        await send_rcon(interaction, f'teleport {steamid} {x} {y} {z}')

    @app_commands.command(name='give', description='Give an item to a player')
    @app_commands.describe(
        steamid='64-bit Steam ID',
        item='Item prefab name (e.g. SwordBlackmetal)',
        count='Number of items (default: 1)',
        quality='Item quality level (default: 1)',
        variant='Item variant (default: 0)',
        durability='Item durability (default: max for quality)',
    )
    @is_admin()
    async def give(
        self,
        interaction: discord.Interaction,
        steamid: str,
        item: str,
        count: Optional[int] = None,
        quality: Optional[int] = None,
        variant: Optional[int] = None,
        durability: Optional[float] = None,
    ):
        await interaction.response.defer()
        cmd = f'give {steamid} {item}'
        if count is not None:
            cmd += f' -count {count}'
        if quality is not None:
            cmd += f' -quality {quality}'
        if variant is not None:
            cmd += f' -variant {variant}'
        if durability is not None:
            cmd += f' -durability {durability}'
        await send_rcon(interaction, cmd)


async def setup(bot: commands.Bot):
    await bot.add_cog(PlayersCog(bot))
