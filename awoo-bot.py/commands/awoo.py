import discord
from discord.ext import commands
from discord import app_commands
from discord import state
import json
import random
from pathlib import Path

# Set up the path to the JSON file with awoo URLs
awoo_urls_file = Path(__file__).parent.parent / 'config' / 'awooUrls.json'


class AwooCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='awoo', description='Awooooooooooooo.')
    async def awoo(self, ctx):
        """Sends a random awoo image."""
        try:
            # Read existing fileUrls from awooUrls.json
            with open(awoo_urls_file, 'r', encoding='utf-8') as file:
                file_urls = json.load(file)

            # Select a random URL from the fileUrls
            random_url = random.choice(file_urls)

            # Create an embed with the image
            embed = discord.Embed(title="Awoo!")
            embed.set_image(url=random_url)
            await ctx.send(embed=embed)

        except Exception as error:
            print(error)
            await ctx.send('Failed to execute the command.', ephemeral=True)


async def setup(bot):
    await bot.add_cog(AwooCommand(bot))
