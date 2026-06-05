from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from checks import is_admin
from utils import send_rcon


class AdminCog(commands.Cog, name='Admin'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── Server ────────────────────────────────────────────────────────────────

    @app_commands.command(name='save', description='Save the current world state')
    @is_admin()
    async def save(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await send_rcon(interaction, 'save')

    @app_commands.command(name='console', description='Execute a raw console command on the server')
    @app_commands.describe(command='Console command to execute (e.g. "sleep 1")')
    @is_admin()
    async def console(self, interaction: discord.Interaction, command: str):
        await interaction.response.defer()
        await send_rcon(interaction, f'consoleCommand {command}')

    @app_commands.command(name='rcon', description='Send any raw RCON command directly to the server')
    @app_commands.describe(command='Full RCON command string (e.g. "say Hello!")')
    @is_admin()
    async def raw_rcon(self, interaction: discord.Interaction, command: str):
        await interaction.response.defer()
        await send_rcon(interaction, command)

    # ── Spawn ─────────────────────────────────────────────────────────────────

    @app_commands.command(name='spawn', description='Spawn a creature or object at the given coordinates')
    @app_commands.describe(
        prefab='Prefab name (e.g. Boar, Troll, Rock)',
        x='X coordinate', y='Y coordinate', z='Z coordinate',
        count='Number to spawn (default: 1)',
        level='Creature level (default: 0)',
        tamed='Spawn as tamed (default: false)',
        radius='Random spawn radius around position',
    )
    @is_admin()
    async def spawn(
        self,
        interaction: discord.Interaction,
        prefab: str,
        x: float,
        y: float,
        z: float,
        count: Optional[int] = None,
        level: Optional[int] = None,
        tamed: Optional[bool] = None,
        radius: Optional[float] = None,
    ):
        await interaction.response.defer()
        cmd = f'spawn {prefab} {x} {y} {z}'
        if count is not None:
            cmd += f' -count {count}'
        if level is not None:
            cmd += f' -level {level}'
        if radius is not None:
            cmd += f' -radius {radius}'
        if tamed:
            cmd += ' -tamed'
        await send_rcon(interaction, cmd)

    # ── Global keys ───────────────────────────────────────────────────────────

    @app_commands.command(name='globalkeys', description='Show all global keys and their values')
    @is_admin()
    async def globalkeys(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await send_rcon(interaction, 'globalKeys')

    @app_commands.command(name='addglobalkey', description='Add a global key to the server (e.g. defeated_bonemass)')
    @app_commands.describe(key='Global key name')
    @is_admin()
    async def addglobalkey(self, interaction: discord.Interaction, key: str):
        await interaction.response.defer()
        await send_rcon(interaction, f'addGlobalKey {key}')

    @app_commands.command(name='removeglobalkey', description='Remove a global key from the server')
    @app_commands.describe(key='Global key name')
    @is_admin()
    async def removeglobalkey(self, interaction: discord.Interaction, key: str):
        await interaction.response.defer()
        await send_rcon(interaction, f'removeGlobalKey {key}')

    # ── Events ────────────────────────────────────────────────────────────────

    @app_commands.command(name='eventslist', description='List all available random events')
    @is_admin()
    async def eventslist(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await send_rcon(interaction, 'eventsList')

    @app_commands.command(name='currentevent', description='Show the currently active random event')
    @is_admin()
    async def currentevent(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await send_rcon(interaction, 'currentEvent')

    @app_commands.command(name='stopevent', description='Stop the currently active random event')
    @is_admin()
    async def stopevent(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await send_rcon(interaction, 'stopEvent')

    @app_commands.command(name='startevent', description='Start a random event at the given coordinates')
    @app_commands.describe(
        event='Event name (use /eventslist to see all)',
        x='X coordinate', y='Y coordinate', z='Z coordinate',
    )
    @is_admin()
    async def startevent(self, interaction: discord.Interaction, event: str, x: float, y: float, z: float):
        await interaction.response.defer()
        await send_rcon(interaction, f'startEvent {event} {x} {y} {z}')

    # ── Objects ───────────────────────────────────────────────────────────────

    @app_commands.command(name='findobjects', description='Find world objects by prefab, tag, creator, or position')
    @app_commands.describe(
        prefab='Filter by prefab name',
        tag='Filter by tag',
        creator='Filter by creator ID (not Steam ID)',
        near_x='Centre X for radius search', near_y='Centre Y', near_z='Centre Z', near_radius='Search radius',
    )
    @is_admin()
    async def findobjects(
        self,
        interaction: discord.Interaction,
        prefab: Optional[str] = None,
        tag: Optional[str] = None,
        creator: Optional[str] = None,
        near_x: Optional[float] = None,
        near_y: Optional[float] = None,
        near_z: Optional[float] = None,
        near_radius: Optional[float] = None,
    ):
        await interaction.response.defer()
        cmd = 'findObjects'
        if prefab:
            cmd += f' -prefab {prefab}'
        if tag:
            cmd += f' -tag {tag}'
        if creator:
            cmd += f' -creator {creator}'
        if near_x is not None and near_y is not None and near_z is not None and near_radius is not None:
            cmd += f' -near {near_x} {near_y} {near_z} {near_radius}'
        if cmd == 'findObjects':
            await interaction.followup.send('At least one filter must be provided.', ephemeral=True)
            return
        await send_rcon(interaction, cmd)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
