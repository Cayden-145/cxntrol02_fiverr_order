import nextcord
from nextcord import *
from nextcord.ext import commands
from variables import Important
import datetime
import aiosqlite
from checks import *
    
class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name="warn", description="Issue a warning to a member.", guild_ids=[Important.guildID])
    @is_staff()
    async def warn(self, ctx: Interaction, user: nextcord.Member, reason: str):
        log_channel_id = await LogChannel.fetch_channel()
        log_channel = ctx.guild.get_channel(log_channel_id)
        member_id = user.id

        async with aiosqlite.connect('main.db') as db:
            async with db.execute("SELECT role_names FROM staff_roles") as cursor:
                rows = await cursor.fetchall()
                
                if not rows:
                    await ctx.send("You do not have the required staff roles to run this command. **Please configure staff roles using `/config`**", ephemeral=True)
                    return
                
                required_roles = [row[0] for row in rows if row]
                
                for role in required_roles:
                    if role in [r.name for r in user.roles]:
                        await ctx.send(f"You cannot warn {user.mention} because they have a staff role.", ephemeral=True)
                        return
                        

        async with aiosqlite.connect('moderations.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS warnings (member_id INTEGER, reason TEXT)")
                await cursor.execute("INSERT INTO warnings (member_id, reason) VALUES (?, ?)", (member_id, reason,))
            await db.commit()

        logEmbed = nextcord.Embed(
                title='Warning',
                color=nextcord.Color.red())
            
        logEmbed.add_field(name="Member", value=f"{user.display_name} (`{user.id}`)", inline=True)
        logEmbed.add_field(name="Moderator", value=f"{ctx.user.mention}", inline=True)
        logEmbed.add_field(name="Reason", value=reason, inline=False)
            
        avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
            
        logEmbed.set_author(name=user.name, icon_url= avatar_url)

        current_time = datetime.datetime.now().strftime("%d/%m/%Y %I:%M %p")
        logEmbed.set_footer(text=f"{current_time}")

        try:
            await user.send(f'You have been warned in the server **{ctx.guild.name}** with the reason: {reason}')
        except:
            pass

        await ctx.send(f'{user.mention} has been issued a warning for the reason: {reason}', ephemeral=True)
        await log_channel.send(embed=logEmbed)

    @nextcord.slash_command(name="warnings", description="N/A",
                            guild_ids=[Important.guildID])
    @is_staff()
    async def warnings(self, ctx: Interaction, user: nextcord.Member):
        pass

    @is_staff()
    @warnings.subcommand(description="List a users warnings")
    async def list(self, ctx: Interaction, user: nextcord.Member):
        async with aiosqlite.connect('moderations.db') as db:
            async with db.execute("SELECT reason FROM warnings WHERE member_id = ?", (user.id,)) as cursor:
                rows = await cursor.fetchall()
                
                if not rows:
                    await ctx.send(f"{user.mention} has no warnings.", ephemeral=True)
                    return
                
                warnings_list = ""
                for index, row in enumerate(rows):
                    if index == 0:
                        warnings_list += f"> {row[0]}"
                    else:
                        warnings_list += f"\n> {row[0]}"

                embed = nextcord.Embed(
                    description=f"{warnings_list}",
                    color=Important.invisEmbedColour
                )
                    
                avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
                    
                embed.set_author(name=f'{user.name}\'s Warnings', icon_url= avatar_url)

                await ctx.send(embed=embed, ephemeral=True)

    @is_staff()
    @warnings.subcommand(description="Clear a users warnings")
    async def clear(self, ctx: Interaction, user: nextcord.Member):
        log_channel_id = await LogChannel.fetch_channel()
        log_channel = ctx.guild.get_channel(log_channel_id)

        async with aiosqlite.connect('moderations.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT COUNT(*) FROM warnings WHERE member_id = ?", (user.id,))
                count = await cursor.fetchone()
                warning_count = count[0]

                if warning_count == 0:
                    await ctx.send(f"{user.mention} has no warnings to clear.", ephemeral=True)
                    return

                await cursor.execute("DELETE FROM warnings WHERE member_id = ?", (user.id,))
            await db.commit()

        logEmbed = nextcord.Embed(
                title='Warnings Cleared',
                description=f"""
{ctx.user.mention} has cleared {user.mention}'s warnings.
A total of **{warning_count}** warning(s) have been deleted.
    """, color=nextcord.Color.red())
        
        avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
        logEmbed.set_author(name=user.name, icon_url= avatar_url)

        await log_channel.send(embed=logEmbed)
        await ctx.send(f"All warnings for {user.mention} have been cleared.", ephemeral=True)

    @nextcord.slash_command(name="kick", description="Kick a user from the server.", guild_ids=[Important.guildID])
    @has_kick_perms() # ! Requires the user to have a role that has kick permissions.
    @is_staff()
    async def kick(self, ctx: Interaction, user: nextcord.Member, reason: str):
        logChannelID = await LogChannel.fetch_channel()
        log_channel = ctx.guild.get_channel(logChannelID)

        async with aiosqlite.connect('main.db') as db:
            async with db.execute("SELECT role_names FROM staff_roles") as cursor:
                rows = await cursor.fetchall()
                
                if not rows:
                    await ctx.send("You do not have the required staff roles to run this command. **Please configure staff roles using `/config`**", ephemeral=True)
                    return
                
                required_roles = [row[0] for row in rows if row]
                
                for role in required_roles:
                    if role in [r.name for r in user.roles]:
                        await ctx.send(f"You cannot kick {user.mention} because they have a staff role.", ephemeral=True)
                        return

        if user.top_role >= ctx.user.top_role or any(role.permissions.administrator for role in user.roles):
            await ctx.send(f"You cannot kick {user.mention} because they have a higher role or admin permissions.", ephemeral=True)
            return

        try:
            logEmbed = nextcord.Embed(
                title='Kick',
                color=nextcord.Color.red())
            
            logEmbed.add_field(name="Member", value=f"{user.display_name} (`{user.id}`)", inline=True)
            logEmbed.add_field(name="Moderator", value=f"{ctx.user.mention}", inline=True)
            logEmbed.add_field(name="Reason", value=reason, inline=False)
            
            avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
            
            logEmbed.set_author(name=user.name, icon_url= avatar_url)

            current_time = datetime.datetime.now().strftime("%d/%m/%Y %I:%M %p")
            logEmbed.set_footer(text=f"{current_time}")

            try:
                await user.send(f'You have been kicked from **{ctx.guild.name}** with the reason: {reason}')
            except:
                pass

            await user.kick(reason=reason)
            await ctx.send(f'{user.mention} has been kicked from the server.\n-# Reason: {reason}', ephemeral=True)

            await log_channel.send(embed=logEmbed)

        except nextcord.Forbidden:
            await ctx.send(f'Insufficient Permissions\nI don\'t have the necessary permissions to kick {user.mention}', ephemeral=True)

    @nextcord.slash_command(name="ban", description="Ban a user from the server.", guild_ids=[Important.guildID])
    @has_ban_perms() # ! Requires the user to have a role that has ban permissions.
    @is_staff()
    async def ban(self, ctx: Interaction, user: nextcord.Member, reason: str):
        logChannelID = await LogChannel.fetch_channel()
        log_channel = ctx.guild.get_channel(logChannelID)

        async with aiosqlite.connect('main.db') as db:
            async with db.execute("SELECT role_names FROM staff_roles") as cursor:
                rows = await cursor.fetchall()
                
                if not rows:
                    await ctx.send("You do not have the required staff roles to run this command. **Please configure staff roles using `/config`**", ephemeral=True)
                    return
                
                required_roles = [row[0] for row in rows if row]
                
                for role in required_roles:
                    if role in [r.name for r in user.roles]:
                        await ctx.send(f"You cannot ban {user.mention} because they have a staff role.", ephemeral=True)
                        return

        if user.top_role >= ctx.user.top_role or any(role.permissions.administrator for role in user.roles):
            await ctx.send(f"You cannot ban {user.mention} because they have a higher role or admin permissions.", ephemeral=True)
            return

        try:
            logEmbed = nextcord.Embed(title='Ban', color=nextcord.Color.red())
            
            logEmbed.add_field(name="Member", value=f"{user.display_name} (`{user.id}`)", inline=True)
            logEmbed.add_field(name="Moderator", value=f"{ctx.user.mention}", inline=True)
            logEmbed.add_field(name="Reason", value=reason, inline=False)
            
            avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
            
            logEmbed.set_author(name=user.name, icon_url= avatar_url)

            current_time = datetime.datetime.now().strftime("%d/%m/%Y %I:%M %p")
            logEmbed.set_footer(text=f"{current_time}")

            try:
                await user.send(f'You have been banned from **{ctx.guild.name}** with the reason: {reason}')
            except:
                pass

            await user.ban(reason=reason)
            await ctx.send(f'{user.mention} has been banned from the server.\n-# Reason: {reason}', ephemeral=True)

            await log_channel.send(embed=logEmbed)

        except nextcord.Forbidden:
            await ctx.send(f'Insufficient Permissions\nI don\'t have the necessary permissions to ban {user.mention}', ephemeral=True)


def setup(client):
    client.add_cog(Moderation(client))