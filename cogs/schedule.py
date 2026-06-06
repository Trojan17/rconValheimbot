import asyncio
import logging

import discord
from discord import app_commands
from discord.ext import commands

from checks import is_admin
from rcon_client import rcon

MAX_LEN = 1900
logger = logging.getLogger(__name__)


class ScheduleCog(commands.Cog, name='Schedule'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._task: asyncio.Task | None = None
        self._rcon_command: str | None = None
        self._interval: int | None = None
        self._channel_id: int | None = None

    async def _loop(self):
        channel = self.bot.get_channel(self._channel_id) or await self.bot.fetch_channel(self._channel_id)
        while True:
            try:
                result = await rcon(self._rcon_command)
                text = result.strip() or '(no response)'
                if len(text) > MAX_LEN:
                    text = text[:MAX_LEN] + '\n... (truncated)'
                await channel.send(f'`{self._rcon_command}` »\n```\n{text}\n```')
            except asyncio.CancelledError:
                return
            except Exception as e:
                logger.error('Scheduled task error: %s', e)
                try:
                    await channel.send(f'Scheduled RCON error: {e}')
                except Exception:
                    pass
            await asyncio.sleep(self._interval)

    schedule_group = app_commands.Group(name='schedule', description='Manage recurring RCON commands')

    @schedule_group.command(name='start', description='Run an RCON command repeatedly on an interval')
    @app_commands.describe(
        command='RCON command to run (e.g. "ping 0 40 0")',
        interval='Interval in seconds between runs (default: 30)',
    )
    @is_admin()
    async def schedule_start(self, interaction: discord.Interaction, command: str, interval: int = 30):
        if interval < 5:
            await interaction.response.send_message('Interval must be at least 5 seconds.', ephemeral=True)
            return

        if self._task and not self._task.done():
            await interaction.response.send_message(
                f'A scheduled task is already running (`{self._rcon_command}` every {self._interval}s). '
                'Use `/schedule stop` first.',
                ephemeral=True,
            )
            return

        self._rcon_command = command
        self._interval = interval
        self._channel_id = interaction.channel_id
        self._task = self.bot.loop.create_task(self._loop())

        await interaction.response.send_message(
            f'Started: `{command}` will run every {interval}s in this channel.'
        )

    @schedule_group.command(name='stop', description='Stop the currently running scheduled RCON command')
    @is_admin()
    async def schedule_stop(self, interaction: discord.Interaction):
        if not self._task or self._task.done():
            await interaction.response.send_message('No scheduled task is currently running.', ephemeral=True)
            return

        self._task.cancel()
        self._task = None
        await interaction.response.send_message(
            f'Stopped scheduled task (`{self._rcon_command}` every {self._interval}s).'
        )
        self._rcon_command = None
        self._interval = None
        self._channel_id = None

    @schedule_group.command(name='status', description='Check if a scheduled RCON command is running')
    @is_admin()
    async def schedule_status(self, interaction: discord.Interaction):
        if self._task and not self._task.done():
            await interaction.response.send_message(
                f'Running: `{self._rcon_command}` every {self._interval}s, posting to <#{self._channel_id}>.'
            )
        else:
            await interaction.response.send_message('No scheduled task is currently running.')


async def setup(bot: commands.Bot):
    await bot.add_cog(ScheduleCog(bot))
