import nextcord
from nextcord import *
from nextcord.ext import commands
from nextcord.ui import *

from variables import Important
from checks import is_staff

class EmbedModal(nextcord.ui.Modal):
    def __init__(self, channelID: str):
        super().__init__(title="Embed Creator")
        self.channel_id = channelID

        self.title_input = nextcord.ui.TextInput(label="Title", min_length=1, max_length=256, required=True,
                                                  placeholder="Start typing here...")
        self.add_item(self.title_input)

        self.description_input = nextcord.ui.TextInput(label="Description", min_length=1, max_length=2048, required=True,
                                                        placeholder="Start typing here...",
                                                        style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.description_input)

        self.footer = nextcord.ui.TextInput(label="Footer", min_length=1, max_length=2048, required=False,
                                                       placeholder="Start typing here...")
        self.add_item(self.footer)

        self.thumbnail_input = nextcord.ui.TextInput(label="Thumbnail", min_length=1, max_length=500, required=False,
                                                      placeholder="Paste URL here...")
        self.add_item(self.thumbnail_input)

        self.large_image_input = nextcord.ui.TextInput(label="Large Img", min_length=1, max_length=500, required=False,
                                                       placeholder="Paste URL here...")
        self.add_item(self.large_image_input)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        title = self.title_input.value
        description = self.description_input.value
        thumbnail = self.thumbnail_input.value
        large_image = self.large_image_input.value
        footer = self.footer.value

        embed = nextcord.Embed(title=title, description=description, color=Important.invisEmbedColour)

        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        if large_image:
            embed.set_image(url=large_image)

        if footer:
            embed.set_footer(text=footer)

        embed_channel = interaction.guild.get_channel(int(self.channel_id))

        msg = await embed_channel.send(embed=embed)
        await interaction.response.send_message(f'Embed sent: {msg.jump_url}', ephemeral=True)
        

class Buttons(nextcord.ui.View):
    def __init__(self, channelID: str):
        super().__init__(timeout=None)
        self.channel = channelID

    @nextcord.ui.button(label="Create", style=nextcord.ButtonStyle.grey, row=1)
    async def create(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):

        modal = EmbedModal(self.channel)
        try:
            await interaction.response.send_modal(modal)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

class CustomEmbed(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name="embed", description="Send a custom embed", guild_ids=[Important.guildID])
    @is_staff()
    async def embed(self, ctx: Interaction, channel: nextcord.TextChannel):
        bot_user = self.client.user
        view = Buttons(channel.id)

        embed = nextcord.Embed(
            title="Embed Creator Instructions",
            description=f"""
Ensure {bot_user.mention} has permissions to speak in {channel.mention}

> Your entered description will appear in __this__ area.
> "Embed Creator Instructions" is where your title will go.
> The footer, if used, will appear at the bottom of your embed, below the description.
> Inputs left blank won't appear in your embed.
> Thumbnail image appears top-right, Large Image appears at the bottom of the embed.
""", 
            color=Important.invisEmbedColour)
            
        if ctx.guild.icon.url is not None:
            embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.guild.icon.url)
        else:
            embed.set_author(name=f"{ctx.guild.name}")
            
        await ctx.send(embed=embed, view=view, ephemeral=True)

def setup(client):
    client.add_cog(CustomEmbed(client))
