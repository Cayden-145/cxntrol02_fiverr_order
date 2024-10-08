import nextcord
from nextcord.ext import application_checks
import aiosqlite
from CustomExceptions import *

def has_kick_perms():
    async def predicate(interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.kick_members:
            raise MissingPermission("This command requires kick permissions.")
        return True
    return application_checks.check(predicate)

def has_ban_perms():
    async def predicate(interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.ban_members:
            raise MissingPermission("This command requires ban permissions.")
        return True
    return application_checks.check(predicate)

def is_admin():
    async def predicate(interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            raise MissingAdminRole("This command requires administrator permissions.")
        return True
    return application_checks.check(predicate)

def is_guild_owner():
    async def predicate(interaction: nextcord.Interaction):
        if interaction.guild is None or interaction.user.id != interaction.guild.owner_id:
            raise MissingGuildOwner("This command can only be ran by the guild owner.")
        return True
    return application_checks.check(predicate)

def is_staff():
    async def predicate(interaction: nextcord.Interaction):
        async with aiosqlite.connect('main.db') as db:
            async with db.execute("SELECT role_names FROM staff_roles") as cursor:
                rows = await cursor.fetchall()
                
                if not rows:
                    raise MissingStaffRole("You do not have the required staff roles to run this command. **Please configure staff roles using `/config`**")
                
                required_roles = [row[0] for row in rows if row]
                
                for role in required_roles:
                    if role in [r.name for r in interaction.user.roles]:
                        return True
                
                raise MissingStaffRole("You do not have the required staff roles to run this command.")

    return application_checks.check(predicate)
            
class LogChannel:
    @staticmethod
    async def fetch_channel():
        async with aiosqlite.connect('main.db') as db:
            async with db.execute("SELECT channel_id FROM log_channel") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
            
class SessionChannel:
    @staticmethod
    async def fetch_session_channel():
        async with aiosqlite.connect('main.db') as db:
            async with db.execute("SELECT channel_id FROM session_channel") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None