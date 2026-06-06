import logging
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)

EXTENSIONS = ['cogs.server', 'cogs.players', 'cogs.chat', 'cogs.admin', 'cogs.schedule']


class ValheimBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        for ext in EXTENSIONS:
            await self.load_extension(ext)
            logger.info(f'Loaded {ext}')

        async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
            if isinstance(error, app_commands.CheckFailure):
                msg = str(error) or 'You do not have the required role to use this command.'
            else:
                logger.error('Slash command error', exc_info=error)
                msg = f'An error occurred: {error}'
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)

        self.tree.on_error = on_tree_error

        guild_id = os.getenv('GUILD_ID')
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f'Slash commands synced to guild {guild_id}')
        else:
            await self.tree.sync()
            logger.info('Slash commands synced globally (may take up to 1 hour to propagate)')

    async def on_ready(self):
        logger.info(f'Bot ready: {self.user} (ID: {self.user.id})')
        await self.change_presence(activity=discord.Game(name='Valheim'))


def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise RuntimeError('DISCORD_TOKEN environment variable is not set')
    bot = ValheimBot()
    bot.run(token, log_handler=None)


if __name__ == '__main__':
    main()
