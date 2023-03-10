import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import tokens
import discord
from discord.ext import commands
import asyncio
import datetime
import pytz

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=discord.Intents.all(),
            sync_command=True,
            application_id=1069300492305444954
        )
        self.initial_extension = [
            "Cogs.Ping",
            "Cogs.Ssal",
            "Cogs.GameContents",
        ]

    
    async def setup_hook(self):
        for ext in self.initial_extension:
            await self.load_extension(ext)
        
        # await bot.tree.sync(guild=discord.Object(id=tokens.guild_id))
        await bot.tree.sync()


    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("===============")
        game = discord.Game("....")
        await self.change_presence(status=discord.Status.online, activity=game)


bot = MyBot()
bot.run(tokens.token)