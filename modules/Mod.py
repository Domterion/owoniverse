from discord.ext import commands

from modules import Error

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Mod(bot))