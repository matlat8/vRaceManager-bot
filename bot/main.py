import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

import driver as driver
from cogs.stats import Stats
from cogs.events import Events
from version import __version__

#load_dotenv()
TOKEN = os.environ.get('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

activity = discord.Activity(name=f"{os.environ.get('DISCORD_COMMAND_PREFIX')}driver help - v{__version__}", type=discord.ActivityType.listening)
bot = commands.Bot(command_prefix=os.environ.get('DISCORD_COMMAND_PREFIX'), intents=intents, activity=activity)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.add_cog(Stats(bot))
    await bot.add_cog(Events(bot))


bot.add_command(driver.driver)
bot.run(TOKEN)

