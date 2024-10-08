# // Cogs
import os

# // Nextcord
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands.errors import CommandNotFound
from nextcord import *
from CustomExceptions import *
from variables import Important, Emojis

# // .env
from dotenv import load_dotenv

# // Button Imports

from cogs.session import sessionButtons
from cogs.session import discordButtons

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = nextcord.Intents.all()

# Feel free to replace command_prefix, though the majority of commands will be a discord slash-command.
client = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)
client.remove_command('help')

@client.event
async def on_ready():
    print('Loading...')

    client.add_all_application_commands()

    client.add_view(sessionButtons())
    client.add_view(discordButtons())

    print('Buttons Loaded...')

    await client.sync_application_commands()
    await client.change_presence(
        activity=nextcord.Activity(type=nextcord.ActivityType.watching, name='Development') # "Watching Development"
        # type=nextcord.ActivityType.playing, name='Development' | "Playing Development"
        # type=nextcord.ActivityType.listening, name='Development' | "Listening to Development"
    )

    print('Bot Running.')

@client.event
async def on_member_join(member):
    channel = nextcord.utils.get(member.guild.channels, name="welcome") # Replace "general" with the name of your channel

    if channel is not None:
        member_count = len(member.guild.members)
        last_digit = member_count % 10
        suffix = "th" if 11 <= member_count % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(last_digit, "th")

        message = f"👋 Welcome {member.mention} to **{member.guild.name}**! You are our `{member_count}{suffix}` member."

        await channel.send(message)
    
    else:
        print(f'on_member_join channel: {channel.name} does not exist.')

@client.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        missing_perms = ", ".join(error.missing_permissions)
        if len(error.missing_permissions) > 1:
            description = f'{Emojis.warningEmoji} **You are missing the following permissions: {missing_perms}.**'
        else:
            description = f'{Emojis.warningEmoji} **You are missing the following permission: {missing_perms}.**'

        errorEmbed = nextcord.Embed(title="Missing Permissions", description=description, color=Important.invisEmbedColour)
        await ctx.send(embed=errorEmbed, ephemeral=True)

    elif isinstance(error, commands.CommandOnCooldown):
        description = description={Emojis.cooldownEmoji} + '**Command on Cooldown.**\n Please try again in {:.2f}s'.format(error.retry_after),

        errorEmbed = nextcord.Embed(title="Cooldown", description=description, color=Important.invisEmbedColour)
        await ctx.send(embed=errorEmbed, ephemeral=True)

    elif isinstance(error, commands.MissingRole):
        missing_role = error.missing_role
        description = f'{Emojis.warningEmoji} **You are missing the following role: {missing_role}.**'

        errorEmbed = nextcord.Embed(title="Missing Role", description=description, color=Important.invisEmbedColour)
        await ctx.send(embed=errorEmbed, ephemeral=True)

    elif isinstance(error, commands.MissingAnyRole):
        missing_roles = ", ".join(error.missing_roles)
        if len(error.missing_roles) > 1:
            description = f'{Emojis.warningEmoji} **You are missing the following roles: {missing_roles}.**'
        else:
            description = f'{Emojis.warningEmoji} **You are missing the following role: {missing_roles}.**'

        errorEmbed = nextcord.Embed(title="Missing Role", description=description, color=Important.invisEmbedColour)
        await ctx.send(embed=errorEmbed, ephemeral=True)

    elif isinstance(error, commands.CommandNotFound):
        errorEmbed = nextcord.Embed(title="Unknown Command",
                                    description=f"{Emojis.warningEmoji} Please try a different command.",
                                    color=Important.invisEmbedColour)
        await ctx.send(embed=errorEmbed, ephemeral=True)

    elif isinstance(error, commands.UserInputError):
        errorEmbed = nextcord.Embed(title="Missing Required Argument",
                                    description=f"{Emojis.warningEmoji} Make sure to enter all the key information!",
                                    color=Important.invisEmbedColour)
        await ctx.send(embed=errorEmbed, ephemeral=True)

    elif isinstance(error, MissingStaffRole):
        errorEmbed = nextcord.Embed(title="Missing Roles",
                                    description=f"{Emojis.warningEmoji} {error}",
                                    color=Important.invisEmbedColour)
        await ctx.send(embed=errorEmbed, ephemeral=True)

    elif isinstance(error, MissingAdminRole):
        errorEmbed = nextcord.Embed(title="Missing Permissions",
                                    description=f"{Emojis.warningEmoji} {error}",
                                    color=Important.invisEmbedColour)
        await ctx.send(embed=errorEmbed, ephemeral=True)

    elif isinstance(error, MissingGuildOwner):
        errorEmbed = nextcord.Embed(title="Missing Permissions",
                                    description=f"{Emojis.warningEmoji} {error}",
                                    color=Important.invisEmbedColour)
        await ctx.send(embed=errorEmbed, ephemeral=True)

    elif isinstance(error, MissingPermission):
        errorEmbed = nextcord.Embed(title="Missing Permissions",
                                    description=f"{Emojis.warningEmoji} {error}",
                                    color=Important.invisEmbedColour)
        await ctx.send(embed=errorEmbed, ephemeral=True)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        errorEmbed = nextcord.Embed(title="Command Error",
                                    description=f"{Emojis.warningEmoji} All commands have transferred to `/` slash commands.",
                                    color=Important.invisEmbedColour)
        await ctx.send(embed=errorEmbed, ephemeral=True)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

if __name__ == "__main__":
    client.run(TOKEN)