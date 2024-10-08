import nextcord
from nextcord import *
from nextcord.ext import commands
import datetime
from checks import LogChannel
import requests
from checks import is_staff, SessionChannel
from variables import Important

from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("ERLC_API_KEY")

base_url = "https://api.policeroleplay.community/v1"

headers = {
    'Server-Key': API_KEY,
    'Content-Type': 'application/json'
}

poll_data = {}

class discordButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None
        self.add_item(ui.Button(style=nextcord.ButtonStyle.link, # If you want an emoji, add emoji='<:emojiName:emojiID>'
                                url="https://policeroleplay.community/join/YOUR_JOIN_CODE", # change "YOUR_JOIN_CODE" to your ERLC Private Server Code
                                label="Quick Join", row=1))
        
    @nextcord.ui.button(label="Player Count", style=nextcord.ButtonStyle.grey, row=1, custom_id="session_plrcount") # If you want an emoji, add emoji='<:emojiName:emojiID>'
    async def playercount(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        response = requests.get(f'{base_url}/server', headers=headers)
        statusCode = response.status_code
        embed = interaction.message.embeds[0]

        currentDateTime = datetime.datetime.now()
        unixTimestamp = int(currentDateTime.timestamp())

        try:
            if statusCode == 200:
                responseData = response.json()

                currentPlayers = responseData['CurrentPlayers']
                maxPlayers = responseData['MaxPlayers']

                if "**Current Players:**" in embed.description:
                    lines = embed.description.splitlines()
                    for i, line in enumerate(lines):
                        if line.startswith("**Current Players:**"):
                            lines[i] = f"**Current Players:** {currentPlayers}/{maxPlayers} | Last Updated: <t:{unixTimestamp}:R>"
                            break
                    embed.description = "\n".join(lines)

                await interaction.message.edit(embed=embed, view=self)

            elif statusCode == 429:
                await interaction.send('You are being rate limited.', ephemeral=True)
        except Exception as e:
            await interaction.send(f'An unexpected error occurred, please try again later.\n-# Error: `{e}`', ephemeral=True)
        
        
class sessionButtons(nextcord.ui.View):
    def __init__(self, message_id=None):
        super().__init__(timeout=None)
        self.max_voters = 4 # TODO: Change value of max voters.

        self.value = None
        self.count = 0
        self.voters = []
        self.voted_users = set()
        self.message_id = message_id
        self.is_persistent()

    @nextcord.ui.button(label="Votes: 0/4", style=nextcord.ButtonStyle.green, custom_id="session_vote") # If you want an emoji, add emoji='<:emojiName:emojiID>'
    async def vote(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id in self.voted_users:
            self.count -= 1
            self.voters.remove(interaction.user.id)
            self.voted_users.remove(interaction.user.id)
            button.label = f"Votes: {self.count}/4"
            
            poll_data[self.message_id] = {
                'voters': self.voters,
                'count': self.count
            }

            await interaction.message.edit(view=self)
            await interaction.response.send_message("Your vote has been removed.", ephemeral=True)
        else:
            self.count += 1
            button.label = f"Votes: {self.count}/{self.max_voters}"
            self.voters.append(interaction.user.id)
            self.voted_users.add(interaction.user.id)

            poll_data[self.message_id] = {
                'voters': self.voters,
                'count': self.count
            }

            await interaction.message.edit(view=self)
            await interaction.send("Your vote has been recorded.", ephemeral=True)

    @nextcord.ui.button(label="View Votes", style=nextcord.ButtonStyle.grey, custom_id="session_voters") # If you want an emoji, add emoji='<:emojiName:emojiID>'
    async def voters(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        rgbColour = 43, 45, 49

        if not self.voters:
            voter_mentions = 'N/A'
        else:
            voter_mentions = ' '.join([f"<@!{voter}>" for voter in self.voters])

        voterEmbed = nextcord.Embed(
            title="Session Votes",
            description=f"{voter_mentions}",
            color=int('%02x%02x%02x' % rgbColour, 16)
        )

        voterEmbed.set_footer(text=f"{self.count} total vote(s).")

        await interaction.send(embed=voterEmbed, ephemeral=True)
        

class SSUConfig(commands.Cog):
    def __init__(self, client):
        self.client = client

    @is_staff()
    @nextcord.slash_command(name="session", description="Session Management",
                            guild_ids=[Important.guildID])
    async def session(self, ctx: Interaction):
        pass

    @is_staff()
    @session.subcommand(description="SSU Poll")
    async def poll(self, ctx: Interaction):
        rgbColour = 255, 69, 68
        buttons = sessionButtons()
        
        currentDateTime = datetime.datetime.now()
        unixTimestamp = int(currentDateTime.timestamp())

        # TODO: Edit description

        ssuPollEmbed = nextcord.Embed(
            title="Session Poll",
            description=f"""
            Click the button below if you would like a Server Start Up!

            4+ votes required for a session.
            Poll started by {ctx.user.mention}
            Poll created: <t:{unixTimestamp}:R>
            """,
            color=int('%02x%02x%02x' % rgbColour, 16))
        
        ssuPollEmbed.set_footer(text=ctx.guild.name)

        sessionChannelID = await SessionChannel.fetch_session_channel()
        sessionChannel = ctx.guild.get_channel(sessionChannelID)
        
        logChannelID = await LogChannel.fetch_channel()
        log_channel = ctx.guild.get_channel(logChannelID)

        msg = await sessionChannel.send("@here", embed=ssuPollEmbed, view=buttons) # <@&ROLE_ID> if you want to ping a specific role

        buttons.message_id = msg.id
        poll_data[buttons.message_id] = {
            'voters': [],
            'count': 0
        }

        logE = nextcord.Embed(
            title="Session Command Used",
            description=f"""
            {ctx.user.mention} has used the command `/session poll`.
            This has been sent in the channel <#{sessionChannel.id}>
            """,
            color=nextcord.Colour.orange()
        )

        await log_channel.send(embed=logE)
        await ctx.response.send_message(f"Poll has been announced in the channel <#{sessionChannel.id}>", ephemeral=True)

    @is_staff()
    @session.subcommand(description="Server Start Up")
    async def start(self, ctx: Interaction):
        rgbColour = 255, 69, 68
        dscrdButtons = discordButtons()

        currentDateTime = datetime.datetime.now()
        unixTimestamp = int(currentDateTime.timestamp())

        sessionChannelID = await SessionChannel.fetch_session_channel()
        sessionChannel = ctx.guild.get_channel(sessionChannelID)
        
        logChannelID = await LogChannel.fetch_channel()
        log_channel = ctx.guild.get_channel(logChannelID)

        voter_list = "No votes recorded."

        try:
            if poll_data:
                last_poll_message_id = list(poll_data.keys())[-1]
                voters = poll_data[last_poll_message_id]['voters']
                
                if voters:
                    voter_mentions = ', '.join([f"<@!{voter}>" for voter in voters])
                    voter_list = f"{voter_mentions}"
                else:
                    voter_list = "No votes recorded."

                poll_data.clear()

                # TODO: Edit description

            ssuEmbed = nextcord.Embed(
                title="Session Started!",
                description=f"""
Our server is up! Come join us for a fantastic roleplay experience. Begin exploring different roleplay scenarios, immerse yourself, and enjoy your time here.

**Server Name:** ...
**Server Code:** ...
**Server Owner:** ...

**Session Started:** <t:{unixTimestamp}:R>
                """,
                color=int('%02x%02x%02x' % rgbColour, 16))
            
            ssuEmbed.set_footer(text='Ensure you have read our game rules before joining the session.')

            msg = await sessionChannel.send("@here", embed=ssuEmbed, view=dscrdButtons) # <@&ROLE_ID> if you want to ping a specific role

            if voter_list != 'No votes recorded.':
                await msg.reply(f"The following voters are required to join within 15 minutes or face moderation!\n\n{voter_list}")
            else:
                pass

            logEmbed = nextcord.Embed(
                title="Session Command Used",
                description=f"""
                {ctx.user.mention} has used the command `/session start`.
                This has been sent in the channel <#{sessionChannel.id}>
                """,
                color=nextcord.Colour.orange()
            )

            await log_channel.send(embed=logEmbed)

            await ctx.response.send_message(f"SSU has been announced in the channel <#{sessionChannel.id}>", ephemeral=True)
        except Exception as e:
            await ctx.send(f'An unexpected error has occured, please try again later.\n-# Error: {e}', ephemeral=True)

    @is_staff()
    @session.subcommand(description="Server Shut Down")
    async def end(self, ctx: Interaction):
        ssdColour = 255, 69, 68

        sessionChannelID = await SessionChannel.fetch_session_channel()
        sessionChannel = ctx.guild.get_channel(sessionChannelID)
        
        logChannelID = await LogChannel.fetch_channel()
        log_channel = ctx.guild.get_channel(logChannelID)

        logEmbed = nextcord.Embed(
            title="Session Command Used",
            description=f"""
                    {ctx.user.mention} has used the command `/session end`.
                    This has been sent in the channel <#{sessionChannel.id}>
                    """,
            color=nextcord.Colour.orange()
        )

        await log_channel.send(embed=logEmbed)

        # TODO: Edit description

        ssdEmbed = nextcord.Embed(
            title="Session Shutdown",
            description="""
            The in-game server has shutdown. Thank you for the amazing session, we hope to see you in the next one! We hope you had an amazing roleplay experience within our server.

            Do not join the server during this time, doing so will result in moderation. We will host another session shortly!

            Want to enhance your roleplay experience within our server? [Join a department!](LINK_TO_CHANNEL_HERE)
            """,
            color=int('%02x%02x%02x' % ssdColour, 16)
        )

        ssdEmbed.set_footer(text=ctx.guild.name)

        await sessionChannel.send(embed=ssdEmbed)

        await ctx.response.send_message(f"SSD has been announced in the channel <#{sessionChannel.id}>", ephemeral=True)

def setup(client):
    client.add_cog(SSUConfig(client))