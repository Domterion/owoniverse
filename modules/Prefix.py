from discord.ext import commands

from modules import Error

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="prefix", invoke_without_command=True, description="Does nothing without a subcommand.")
    @commands.has_permissions(administrator=True)
    async def _prefix(self, ctx):
        await ctx.send("Please use a subcommand.")

    @_prefix.command(name="set", description="Set your guilds prefix.")
    @commands.has_permissions(administrator=True)
    async def _set(self, ctx, prefix: str):
        if len(prefix) > 20:
            raise Error.InvalidPrefix(ctx)

        await ctx.bot.add_prefix(ctx.guild.id, prefix)
        await ctx.tick()

    @_prefix.command(name="default", aliases=["none", "remove", "delete", "disable"], description="Set guild prefix back to uwu.")
    @commands.has_permissions(administrator=True)
    async def _default(self, ctx):
        if ctx.bot.guild_config[ctx.guild.id]['prefix'] is None:
            raise Error.MissingSetting(ctx)

        await ctx.bot.remove_prefix(ctx.guild.id)
        await ctx.tick()

def setup(bot):
    bot.add_cog(Prefix(bot))