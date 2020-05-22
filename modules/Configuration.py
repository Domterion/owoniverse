import discord
from discord.ext import commands

from modules import Error


class Configuration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="prefix",
        invoke_without_command=True,
        description="Does nothing without a subcommand.",
    )
    @commands.has_permissions(administrator=True)
    async def _prefix(self, ctx):
        await ctx.send("Please use a subcommand.")

    @_prefix.command(name="set", description="Set your guilds prefix.")
    @commands.has_permissions(administrator=True)
    async def _set(self, ctx, prefix: str):
        if len(prefix) > 20:
            raise Error.InvalidOrMissingSetting(ctx)

        await ctx.bot.add_prefix(ctx.guild.id, prefix)
        await ctx.tick()

    @_prefix.command(
        name="default",
        aliases=["none", "remove", "delete", "disable"],
        description="Set guild prefix back to uwu.",
    )
    @commands.has_permissions(administrator=True)
    async def _default(self, ctx):
        if ctx.bot.get_guild_config(ctx.guild.id)["prefix"] is None:
            raise Error.InvalidOrMissingSetting(ctx)

        await ctx.bot.remove_prefix(ctx.guild.id)
        await ctx.tick()

    @commands.group(
        name="log",
        invoke_without_command=True,
        description="Does nothing without a subcommand.",
    )
    @commands.has_permissions(administrator=True)
    async def _log(self, ctx):
        await ctx.send("Please use a subcommand.")

    @_log.command(
        name="channel",
        description="Set your guilds logging channel. If no channel is specified will use channel called in.",
    )
    @commands.has_permissions(administrator=True)
    async def _channel(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        await ctx.bot.add_log(ctx.guild.id, channel.id)
        await ctx.tick()

    @_log.command(
        name="default",
        aliases=["none", "remove", "delete", "disable"],
        description="Remove guild logging channel.",
    )
    @commands.has_permissions(administrator=True)
    async def __default(self, ctx):
        if ctx.bot.get_guild_config(ctx.guild.id)["log"] is None:
            raise Error.InvalidOrMissingSetting(ctx)

        await ctx.bot.remove_log(ctx.guild.id)
        await ctx.tick()

    @_log.command(
        name="toggle",
        description="Toggle which logs are on, mod_logs, member_logs and message_logs.",
    )
    @commands.has_permissions(administrator=True)
    async def _toggle(self, ctx, log: str):
        if (
            ctx.bot.get_guild_config(ctx.guild.id)["log"] is None
            or log not in ctx.config.logs
        ):
            raise Error.InvalidOrMissingSetting(ctx)

        await ctx.bot.toggle_log(ctx.guild.id, log)
        await ctx.tick()

    @commands.command(name="config", description="Check your guild config")
    async def _config(self, ctx):
        config = ctx.bot.get_guild_config(ctx.guild.id)
        if config is None:
            raise Error.NoConfig()

        log = f"You have no logging setup, do **{ctx.prefix}log set** to set your logging channel."
        if config["log"]["channel"] is not None:
            log = f"""Your log channel is **{config['log']['channel']}**
**member_logs**: {ctx.bot.config.emotes['tick'] if config['log']['member_logs'] else ctx.bot.config.emotes['cross']}
**message_logs**: {ctx.bot.config.emotes['tick'] if config['log']['message_logs'] else ctx.bot.config.emotes['cross']}
**mod_logs**: {ctx.bot.config.emotes['tick'] if config['log']['mod_logs'] else ctx.bot.config.emotes['cross']}
**guild_logs**: {ctx.bot.config.emotes['tick'] if config['log']['guild_logs'] else ctx.bot.config.emotes['cross']}
"""
        e = discord.Embed(
            color=ctx.bot.config.color,
            description=f"""
Your guilds prefix is "**{config['prefix'] if config['prefix'] is not None else ctx.prefix}**".

Logging:
{log}
""",
        )

        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Configuration(bot))
