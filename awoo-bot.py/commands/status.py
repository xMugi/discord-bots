import discord
from discord.ext import commands
import json
from pathlib import Path

# Load configuration for user ID
config_path = Path(__file__).parent.parent / 'config' / 'config.json'
with open(config_path, 'r', encoding='utf-8') as file:
    config = json.load(file)
    user_ids = [int(id) for id in config["userIDs"]]  # Convert all elements in the list to integers


class StatusCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='status', description='Set bot status')
    async def status(self, ctx, *, new_status: str):
        """Sets the bot's custom status."""
        author_id = ctx.author.id if hasattr(ctx, 'author') else ctx.message.author.id
        if author_id not in user_ids:
            await ctx.send('You do not have permission to use this command.', ephemeral=True)
            return

        try:
            # Set the new status
            await self.bot.change_presence(activity=discord.Game(name=new_status))
            await ctx.send(f"Bot status updated to: {new_status}")
        except Exception as e:
            print(f"Failed to set bot status: {e}")
            await ctx.send('An error occurred while setting the bot status.', ephemeral=True)


async def setup(bot):
    await bot.add_cog(StatusCommand(bot))
