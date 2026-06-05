import discord

from rcon_client import rcon

MAX_LEN = 1900


async def send_rcon(interaction: discord.Interaction, command: str) -> None:
    """Run an RCON command and send the result. Assumes response is already deferred."""
    try:
        result = await rcon(command)
        text = result.strip() or '(no response)'
        if len(text) > MAX_LEN:
            text = text[:MAX_LEN] + '\n... (truncated)'
        await interaction.followup.send(f'```\n{text}\n```')
    except Exception as e:
        await interaction.followup.send(f'❌ RCON error: {e}', ephemeral=True)
