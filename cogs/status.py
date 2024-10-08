import nextcord
from nextcord import *
from nextcord.ext import commands
from variables import Important
import aiosqlite
import platform
    
class Status(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name="status", description="Status of the bot", guild_ids=[Important.guildID])
    async def status(self, ctx: Interaction):
        ping = round(self.client.latency * 1000)

        nextcord_version = nextcord.__version__
        python_version = platform.python_version()
        aiosqlite_version = aiosqlite.__version__

        embed = nextcord.Embed(title="Bot Status", color=Important.invisEmbedColour)
        
        embed.add_field(name="Ping", value=f"{ping} ms", inline=True)
        embed.add_field(name="Nextcord Version", value=nextcord_version, inline=True)
        embed.add_field(name="‎ ", value=f"‎ ", inline=True) # Blank Line [U+200E] (not required, just makes it look nicer)
        embed.add_field(name="Python Version", value=python_version, inline=True)
        embed.add_field(name="Database Version", value=aiosqlite_version, inline=True)

        avatar_url = self.client.user.display_avatar.url
        embed.set_thumbnail(url=avatar_url)

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Status(client))