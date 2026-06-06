import asyncio
import logging

import discord
from discord import app_commands
from discord.ext import commands

from checks import is_admin
from rcon_client import rcon

MAX_LEN = 1900
MAX_TASKS = 6
logger = logging.getLogger(__name__)


class ScheduleCog(commands.Cog, name='Schedule'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # name -> (rcon_command, interval_secs, channel)
        self._configs: dict[str, tuple[str, int, discord.abc.Messageable]] = {}
        self._tasks: dict[str, asyncio.Task] = {}

    async def _loop(self, name: str):
        rcon_cmd, interval, channel = self._configs[name]
        while True:
            try:
                result = await rcon(rcon_cmd)
                text = result.strip() or '(no response)'
                if len(text) > MAX_LEN:
                    text = text[:MAX_LEN] + '\n... (truncated)'
                await channel.send(f'[{name}] `{rcon_cmd}` »\n```\n{text}\n```')
            except asyncio.CancelledError:
                return
            except Exception as e:
                logger.error('Scheduled task [%s] error: %s', name, e)
                try:
                    await channel.send(f'[{name}] RCON error: {e}')
                except Exception:
                    pass
            await asyncio.sleep(interval)

    schedule_group = app_commands.Group(name='schedule', description='Manage recurring RCON commands')

    @schedule_group.command(name='add', description=f'Add a recurring RCON command (max {MAX_TASKS})')
    @app_commands.describe(
        name='Short identifier for this task (e.g. "ping")',
        command='RCON command to run (e.g. "ping 0 40 0")',
        interval='Interval in seconds between runs (default: 30)',
    )
    @is_admin()
    async def schedule_add(self, interaction: discord.Interaction, name: str, command: str, interval: int = 30):
        await interaction.response.defer(ephemeral=True)

        if interval < 5:
            await interaction.followup.send('Interval must be at least 5 seconds.')
            return

        active = sum(1 for t in self._tasks.values() if not t.done())
        if active >= MAX_TASKS:
            await interaction.followup.send(f'Maximum of {MAX_TASKS} tasks reached. Use `/schedule remove` first.')
            return

        if name in self._tasks and not self._tasks[name].done():
            await interaction.followup.send(f'Task `{name}` is already running. Use `/schedule remove {name}` first.')
            return

        self._configs[name] = (command, interval, interaction.channel)
        self._tasks[name] = self.bot.loop.create_task(self._loop(name))

        await interaction.followup.send(f'Started `{name}`: `{command}` every {interval}s in this channel.')

    @schedule_group.command(name='remove', description='Stop and remove a scheduled task by name')
    @app_commands.describe(name='Name of the task to remove')
    @is_admin()
    async def schedule_remove(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=True)
        task = self._tasks.pop(name, None)
        self._configs.pop(name, None)
        if task and not task.done():
            task.cancel()
            await interaction.followup.send(f'Stopped and removed task `{name}`.')
        else:
            await interaction.followup.send(f'No running task named `{name}`.')

    @schedule_group.command(name='list', description='List all active scheduled tasks')
    @is_admin()
    async def schedule_list(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        running = [(n, cmd, ivl) for n, (cmd, ivl, _) in self._configs.items()
                   if n in self._tasks and not self._tasks[n].done()]
        if not running:
            await interaction.followup.send('No scheduled tasks running.')
            return
        lines = [f'`{n}`: `{cmd}` every {ivl}s' for n, cmd, ivl in running]
        await interaction.followup.send('**Scheduled tasks:**\n' + '\n'.join(lines))

    @schedule_group.command(name='clear', description='Stop and remove all scheduled tasks')
    @is_admin()
    async def schedule_clear(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        count = sum(1 for t in self._tasks.values() if not t.done())
        for task in self._tasks.values():
            task.cancel()
        self._tasks.clear()
        self._configs.clear()
        await interaction.followup.send(f'Cleared {count} scheduled task(s).')


async def setup(bot: commands.Bot):
    await bot.add_cog(ScheduleCog(bot))
