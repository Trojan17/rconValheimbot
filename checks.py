import os

import discord
from discord import app_commands


def is_admin():
    """Restricts a command to roles listed in ADMIN_ROLE_IDS (comma-separated).
    If ADMIN_ROLE_IDS is not set, all users are allowed."""
    async def predicate(interaction: discord.Interaction) -> bool:
        role_ids_str = os.getenv('ADMIN_ROLE_IDS', '').strip()
        if not role_ids_str:
            return True
        if not hasattr(interaction.user, 'roles'):
            raise app_commands.CheckFailure('❌ This command can only be used inside a server.')
        allowed_ids = {int(r.strip()) for r in role_ids_str.split(',') if r.strip()}
        user_role_ids = {role.id for role in interaction.user.roles}
        if not allowed_ids.intersection(user_role_ids):
            raise app_commands.CheckFailure('❌ You do not have the required role to use this command.')
        return True
    return app_commands.check(predicate)
