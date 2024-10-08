import nextcord
from nextcord import *
from nextcord.ext import commands, application_checks
from erlcpy import *
import requests

from checks import is_staff, LogChannel

from dotenv import load_dotenv
import os
from variables import Important

load_dotenv()
API_KEY = os.getenv("ERLC_API_KEY")

base_url = "https://api.policeroleplay.community/v1"

command_api = Command(base_url, API_KEY)

info_api = Information(base_url, API_KEY)

logs_api = Logs(base_url, API_KEY)

headers = {
    'Server-Key': API_KEY,
    'Content-Type': 'application/json'
}

rgbColour = 43, 45, 49
        

class infoButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @nextcord.ui.button(label="Vehicles", style=nextcord.ButtonStyle.grey, row=1) # If you want an emoji, add emoji='<:emojiName:emojiID>'
    async def vehicles(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        try:
            serverVehicles = info_api.get_vehicles()

            if serverVehicles:
                formatted_logs = " ".join([f"`{log['Owner']}`\n**Model:** {log['Name']}\n**Livery:** {log['Texture']}\n\n" for log in serverVehicles])

                embed = nextcord.Embed(
                    title = "Server Vehicles",
                    description=formatted_logs,
                    color=int('%02x%02x%02x' % rgbColour, 16))
                    
                embed.set_image("https://media.discordapp.net/attachments/1083119698545213551/1264137301592903702/Banner_8.png?ex=66a012db&is=669ec15b&hm=5107083accbe113e3a6de7cf6c6cc1f6a07f2f30f5c9c6c51b26e36a99fe1e32&=&format=webp&quality=lossless&width=1274&height=292")
            
                await interaction.send(embed=embed)

            await interaction.message.delete()

        except Exception as e:
            await interaction.send(f"An error occured: {e}")

    @nextcord.ui.button(label="Server Queue", style=nextcord.ButtonStyle.grey, row=1) # If you want an emoji, add emoji='<:emojiName:emojiID>'
    async def serverQueue(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        try:
            serverQueue = info_api.get_queue()

            if serverQueue:
                formatted_logs = "\n".join([f"{log['Player']}" for log in serverQueue])

                embed = nextcord.Embed(
                    title = "In-game Queue",
                    description=formatted_logs,
                    color=int('%02x%02x%02x' % rgbColour, 16))
                    
                embed.set_image("https://media.discordapp.net/attachments/1083119698545213551/1264137269909127198/Banner_5.png?ex=66a012d3&is=669ec153&hm=2007a2a0dbad70df0f412fa8f79426dc90dfacbdddb94ab241d1368b983e19a4&=&format=webp&quality=lossless&width=550&height=126")
            
                await interaction.send(embed=embed)
            
            else:
                await interaction.send("Unable to find server queue.")

            await interaction.message.delete()

        except Exception as e:
            await interaction.send(f"An error occured: {e}")

    @nextcord.ui.button(label="Server Players", style=nextcord.ButtonStyle.grey, row=1) # If you want an emoji, add emoji='<:emojiName:emojiID>'
    async def serverPlayers(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        try:
            joinLogs = info_api.get_players()

            if joinLogs:
                formatted_logs = " ".join([f"`{log['Player']}`\n**Team:** {log['Team']}\n\n" for log in joinLogs])

                embed = nextcord.Embed(
                    title = "Current Players",
                    description=formatted_logs,
                    color=int('%02x%02x%02x' % rgbColour, 16))
                    
                embed.set_image("https://media.discordapp.net/attachments/1083119698545213551/1264134128765505557/SSU_Banner_2.png?ex=66a00fe6&is=669ebe66&hm=1e33e1f779aa95b1cc449228927b633605f887f0a66eba9d3bad667dd62940ee&=&format=webp&quality=lossless&width=550&height=126")
            
                await interaction.send(embed=embed)

            await interaction.message.delete()

        except Exception as e:
            await interaction.send(f"An error occured: {e}")


class logsButtons(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @nextcord.ui.button(label="Join Logs", style=nextcord.ButtonStyle.grey, row=1) # If you want an emoji, add emoji='<:emojiName:emojiID>'
    async def joinLogs(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        try:
            joinLogs = logs_api.get_join_logs()

            if joinLogs:
                formatted_logs = " ".join([f"{log['Player']} <t:{log['Timestamp']}:R>\n" for log in joinLogs])

                embed = nextcord.Embed(
                    title = "Join Logs",
                    description=formatted_logs,
                    color=int('%02x%02x%02x' % rgbColour, 16))
                    
                embed.set_image("https://media.discordapp.net/attachments/1083119698545213551/1264137280071929978/Banner_6.png?ex=66a012d6&is=669ec156&hm=6605a20be383edbcb53b25f0cb087e6d2e74bee51b7b3c51ffb2cb88b36cc490&=&format=webp&quality=lossless&width=1274&height=292")
            
                await interaction.send(embed=embed)

            else:
                await interaction.send("Unable to find recent join logs.")

            await interaction.message.delete()

        except Exception as e:
            await interaction.send(f"An error occured: {e}")

    @nextcord.ui.button(label="Command Logs", style=nextcord.ButtonStyle.grey, row=1) # If you want an emoji, add emoji='<:emojiName:emojiID>'
    async def commandLogs(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        try:
            commandLogs = logs_api.get_command_logs()

            if commandLogs:
                formatted_logs = " ".join([f"**{log['Player']}**\n`{log['Command']}`\n<t:{log['Timestamp']}:R>\n\n" for log in commandLogs])

                embed = nextcord.Embed(
                    title = "Command Logs",
                    description=formatted_logs,
                    color=int('%02x%02x%02x' % rgbColour, 16))
                    
                embed.set_image("https://media.discordapp.net/attachments/1083119698545213551/1264137293011357696/Banner_7.png?ex=66a012d9&is=669ec159&hm=fef5a979523befe580ca4b0f08b19538ac7c8c2655b5cde6273b9dbafdd36ba7&=&format=webp&quality=lossless&width=1440&height=330")
            
                await interaction.send(embed=embed)

            else:
                await interaction.send("Unable to find recent command logs.")

            await interaction.message.delete()

        except Exception as e:
            await interaction.send(f"An error occured: {e}")

    @nextcord.ui.button(label="Kill Logs", style=nextcord.ButtonStyle.grey, row=1) # If you want an emoji, add emoji='<:emojiName:emojiID>'
    async def killLogs(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        try:
            commandLogs = logs_api.get_kill_logs()

            if commandLogs:
                formatted_logs = " ".join([f"`{log['Killer']}`\n**Killed:**{log['Killed']}\n<t:{log['Timestamp']}:R>\n\n" for log in commandLogs])

                embed = nextcord.Embed(
                    title = "Kill Logs",
                    description=formatted_logs,
                    color=int('%02x%02x%02x' % rgbColour, 16))
                    
                embed.set_image("https://media.discordapp.net/attachments/1083119698545213551/1264531844544856137/Banner_9.png?ex=669f880d&is=669e368d&hm=73284f475cfa31cc580d51654592d27675cb603f1f23182864d62242fc70a4ae&=&format=webp&quality=lossless&width=550&height=126")
            
                await interaction.send(embed=embed)

            else:
                await interaction.send("Unable to find recent kill logs.")

            await interaction.message.delete()

        except Exception as e:
            await interaction.send(f"An error occured: {e}")

# TODO
    @nextcord.ui.button(label="Bans", style=nextcord.ButtonStyle.grey, row=2) # If you want an emoji, add emoji='<:emojiName:emojiID>'
    async def bans(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        try:
            commandLogs = logs_api.get_bans()
            print(commandLogs)

            if commandLogs:
                formatted_logs = " ".join([f"> {log['PlayerId']}`" for log in commandLogs])

                embed = nextcord.Embed(
                    title = "In-game Bans",
                    description=formatted_logs,
                    color=int('%02x%02x%02x' % rgbColour, 16))
                    
                embed.set_image("https://media.discordapp.net/attachments/1083119698545213551/1264137293011357696/Banner_7.png?ex=66a012d9&is=669ec159&hm=fef5a979523befe580ca4b0f08b19538ac7c8c2655b5cde6273b9dbafdd36ba7&=&format=webp&quality=lossless&width=1440&height=330")
            
                await interaction.send(embed=embed)

            else:
                await interaction.send("Unable to find server bans.")

        except Exception as e:
            await interaction.send(f"An error occured: {e}")

    @nextcord.ui.button(label="Mod Calls", style=nextcord.ButtonStyle.grey, row=2) # If you want an emoji, add emoji='<:emojiName:emojiID>'
    async def modCalls(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        try:
            commandLogs = logs_api.get_mod_calls()

            if commandLogs:
                formatted_logs = " ".join([f"{log['Caller']} <t:{log['Timestamp']}:R> \n" for log in commandLogs])

                embed = nextcord.Embed(
                    title = "Recent Mod Calls",
                    description=formatted_logs,
                    color=int('%02x%02x%02x' % rgbColour, 16))
                    
                embed.set_image("https://media.discordapp.net/attachments/1083119698545213551/1264137247142445096/Banner_3.png?ex=66a012ce&is=669ec14e&hm=f828283cf7204e2ec97e58247058964be49abcf26be9dd094ce38da4bd827643&=&format=webp&quality=lossless&width=1274&height=292")
            
                await interaction.send(embed=embed)

            else:
                await interaction.send("Unable to find recent mod calls.")

            await interaction.message.delete()

        except Exception as e:
            await interaction.send(f"An error occured: {e}")

    

class ERLCApi(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.announcement_task = None

    @nextcord.slash_command(name="erlc", description="ERLC API",
                            guild_ids=[Important.guildID])
    @is_staff()
    async def erlc(self, ctx: Interaction):
        pass

    @is_staff()
    @erlc.subcommand(description="ERLC Private Server Info")
    async def server(self, ctx: Interaction):
        try:
            response = requests.get(f'{base_url}/server', headers=headers)
            statusCode = response.status_code
            
            if statusCode == 200:
                responseData = response.json()

                coOwnerList = len(responseData['CoOwnerIds'])
                currentPlayers = responseData['CurrentPlayers']
                maxPlayers = responseData['MaxPlayers']
                joinCode = responseData['JoinKey']

                embed = nextcord.Embed(
                    title='Queens County Roleplay', color=int('%02x%02x%02x' % rgbColour, 16))
                
                embed.add_field(name="Owner", value=f"Building_Jayden", inline=True)
                embed.add_field(name="Co-Owners", value=f"{coOwnerList}", inline=True)
                embed.add_field(name="‎ ", value=f"‎ ", inline=True) # Blank Line [U+200E] (not required, just makes it look nicer)
                embed.add_field(name="Current Players", value=f"{currentPlayers}/{maxPlayers}", inline=True)
                embed.add_field(name="Join Code", value=f"{joinCode} | [Link](https://www.policeroleplay.community/join?code={joinCode})", inline=True)
                embed.add_field(name="‎ ", value=f"‎ ", inline=True)
                
                if ctx.guild.icon.url is not None:
                    embed.set_thumbnail(url=ctx.guild.icon.url)

                embed.set_image('https://media.discordapp.net/attachments/1083119698545213551/1272188708304719963/Banner_17.png?ex=66be0610&is=66bcb490&hm=dffdd24746c8eb6d3dd07d93cc0a696aacac032407955a696574c2bae5cdbc40&=&format=webp&quality=lossless&width=1440&height=330')
            
                await ctx.send(embed=embed)
            elif statusCode == 429:
                await ctx.send('You are being rate limited.', ephemeral=True)
                print(statusCode)
        except Exception as e:
            await ctx.send(f'An unexpected error occured, please try again later.\nError: `{e}`')

    @is_staff()
    @erlc.subcommand(description="Select from a list of in-game information.")
    async def info(self, ctx: Interaction):
        buttons=infoButtons()

        await ctx.send(view=buttons)

    @is_staff()
    @erlc.subcommand(description="Select from a list of in-game logs.")
    async def logs(self, ctx: Interaction):
        buttons=logsButtons()

        await ctx.send(view=buttons)

    @is_staff()
    @erlc.subcommand(description="Select from a list of commands to run.")
    async def command(self, ctx: Interaction, command = SlashOption(
        name="command", 
        choices=["weather", "unmod", "mod", "unban", "ban", "kill", "h", "m", "teleport", "refresh", "heal", "startfire", "unwanted", "priority", "wanted", "time", "stopfire", "jail", "pt", "load", "kick", "pm"],
        required=True), input: str = SlashOption(
        name="input",
        description="Only use if you are using a command that requires extra text, i.e :h",
        required=False)):


        logChannelID = await LogChannel.fetch_channel()
        log_channel = ctx.guild.get_channel(logChannelID)

        logEmbed = nextcord.Embed(
                    title="API Command Log",
                    description=f"""
                    {ctx.user.mention} has used the command `:{command} {input}`.
                    :warning: **This is an in-game ERLC command.**
                    """,
                    color=int('%02x%02x%02x' % rgbColour, 16))

        try:
            command_api.send_command(f":{command} {input}")

            await ctx.send(f"Successfully ran the command `:{command} {input}`")
            await log_channel.send(embed=logEmbed)

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")


def setup(client):
    client.add_cog(ERLCApi(client))