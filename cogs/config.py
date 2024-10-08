import nextcord
from nextcord import *
from nextcord.ext import commands
import aiosqlite
from nextcord.ui import Select, View
from variables import Important
from checks import is_admin

class sessionChannelModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Session Channel Config")

        self.channelID = nextcord.ui.TextInput(label="Channel ID", min_length=1, max_length=124, required=True,
                                                 placeholder="Log channel ID")
        self.add_item(self.channelID)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        channelID = int(self.channelID.value)

        async with aiosqlite.connect('main.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS session_channel (channel_id INTEGER)")
                await cursor.execute("INSERT OR REPLACE INTO session_channel (channel_id) VALUES (?)", (channelID,))
            await db.commit()
        
        await interaction.message.edit(f"Saved Session Channel: <#{channelID}>", embed=None, view=None)

class logChannelModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Log Channel Config")

        self.channelID = nextcord.ui.TextInput(label="Channel ID", min_length=1, max_length=124, required=True,
                                                 placeholder="Log channel ID")
        self.add_item(self.channelID)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        channelID = int(self.channelID.value)

        async with aiosqlite.connect('main.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS log_channel (channel_id INTEGER)")
                await cursor.execute("INSERT OR REPLACE INTO log_channel (channel_id) VALUES (?)", (channelID,))
            await db.commit()
        
        await interaction.message.edit(f"Saved Log Channel: <#{channelID}>", embed=None, view=None)

class StaffRoleSelect(Select):
    def __init__(self, roles):
        limited_roles = roles[:25]
        options = [nextcord.SelectOption(label=role.name, value=role.name) for role in limited_roles]

        super().__init__(placeholder="Select Staff Roles", min_values=1, max_values=len(limited_roles), options=options)

    async def callback(self, interaction: nextcord.Interaction):
        selected_role_names = self.values
        guild_id = interaction.guild.id
        
        async with aiosqlite.connect('main.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS staff_roles (guild_id INTEGER PRIMARY KEY, role_names TEXT)")
                await cursor.execute("INSERT OR REPLACE INTO staff_roles (guild_id, role_names) VALUES (?, ?)", 
                                     (guild_id, ', '.join(selected_role_names)))
            await db.commit()

        role_mentions = ", ".join([f"<@&{role_name}>" for role_name in selected_role_names])

        await interaction.message.edit(f"Saved Staff Roles: {role_mentions}", embed=None, view=None)

class RoleDropdownView(View):
    def __init__(self, roles):
        super().__init__()
        self.add_item(StaffRoleSelect(roles))

class selectionButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @nextcord.ui.button(label="Configure Staff Roles", style=nextcord.ButtonStyle.grey, row=1, custom_id="config_select_staff") # If you want an emoji, add emoji='<:emojiName:emojiID>'
    async def select_staff(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        roles = interaction.guild.roles

        if not roles:
            await interaction.message.edit(content="No roles are available.", embed=None, view=None)

        embed = nextcord.Embed(title="Staff Role Configuration", description="Please select the staff roles from the dropdown below:", color=Important.invisEmbedColour)
        await interaction.message.edit(embed=embed, view=RoleDropdownView(roles))

    @nextcord.ui.button(label="Configure Log Channel", style=nextcord.ButtonStyle.grey, row=1) # If you want an emoji, add emoji='<:emojiName:emojiID>'
    async def select_log_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        text_channels = [channel for channel in interaction.guild.text_channels if channel.type == nextcord.ChannelType.text]

        if not text_channels:
            await interaction.message.edit("No text channels available for logging.", embed=None, view=None)
            return

        modal = logChannelModal()
        await interaction.response.send_modal(modal=modal)

    @nextcord.ui.button(label="Configure Session Channel", style=nextcord.ButtonStyle.grey, row=1) # If you want an emoji, add emoji='<:emojiName:emojiID>'
    async def select_session_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        text_channels = [channel for channel in interaction.guild.text_channels if channel.type == nextcord.ChannelType.text]

        if not text_channels:
            await interaction.message.edit("No text channels available for logging.", embed=None, view=None)
            return

        modal = sessionChannelModal()
        await interaction.response.send_modal(modal=modal)
    
class Config(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name="config", description="Configure bot settings.", guild_ids=[Important.guildID])
    @is_admin()
    async def config(self, ctx: Interaction):
        view = selectionButtons()

        embed = nextcord.Embed(
            title = f"{ctx.guild.name} Configuration",
            description="Use the buttons below to configure the settings for this bot.",
            color=Important.invisEmbedColour)
        
        if ctx.guild.icon.url is not None:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        
        await ctx.send(embed=embed, view=view)


def setup(client):
    client.add_cog(Config(client))