import discord
from discord.ext import commands
from discord import app_commands
import interactions
import json
import os

# Load configuration from config.json
with open('./config/config.json') as config_file:
    config = json.load(config_file)
    guildIds = config['guildIds']
    token = config['token']

# Set up the client with intents
intents = discord.Intents.all()
intents.guilds = True
intents.messages = True

client = commands.Bot(command_prefix='/', intents=intents)


async def set_bot_status():
    for guild_id in guildIds:
        guild = await client.fetch_guild(guild_id)
        if guild:
            await client.change_presence(activity=discord.Game(name='mugi.pages.dev | /awoo'))
            print(f'Bot status set successfully for guild: {guild_id}')


@client.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.application_command:
        command = client.get_application_command(interaction.command.name)
        if command:
            try:
                await command.callback(interaction)
            except Exception as e:
                print(f'Error executing command {interaction.command.name}:', e)
                await interaction.response.send_message('An error occurred while executing this command.',
                                                        ephemeral=True)


async def load_commands():
    print('Started refreshing application (/) commands.')

    # Load commands from files
    for filename in os.listdir('./commands'):
        if filename.endswith('.py') and not filename.startswith('__'):
            extension = filename[:-3]
            try:
                await client.load_extension(f'commands.{extension}')
                print(f'Successfully loaded command: {extension}')
            except Exception as e:
                print(f'Failed to load command {extension}: {str(e)}')

    print('Successfully registered application (/) commands.')


@client.event
async def on_ready():
    await client.user.edit(username='awoo')
    print(f'Logged in as {client.user}!')
    await load_commands()
    await set_bot_status()


client.run(token)
