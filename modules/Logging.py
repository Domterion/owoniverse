import asyncio
from datetime import datetime
import sys
import time

import asyncpg
import discord
import psutil
from discord.ext import commands

import config
from modules import Error


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="log", invoke_without_command=True, description="Does nothing without a subcommand.")
    @commands.has_permissions(administrator=True)
    async def _log(self, ctx):
        await ctx.send("Please use a subcommand.")

    @_log.command(name="set", description="Set your guilds logging channel. If no channel is specified will use channel called in.")
    @commands.has_permissions(administrator=True)
    async def _set(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        await ctx.bot.add_log(ctx.guild.id, channel.id)
        await ctx.tick()

    @_log.command(name="default", aliases=["none", "remove", "delete", "disable"], description="Remove guild logging channel.")
    @commands.has_permissions(administrator=True)
    async def _default(self, ctx):
        if ctx.bot.guild_config[ctx.guild.id]['log'] is None:
            raise Error.MissingSetting(ctx)

        await ctx.bot.remove_log(ctx.guild.id)
        await ctx.tick()

    @_log.command(name="toggle", description="Toggle which logs are on, mod_logs, member_logs and message_logs.")
    @commands.has_permissions(administrator=True)
    async def _toggle(self, ctx, log: str):

        logs = ["mod_logs", "message_logs", "member_logs"]

        if ctx.bot.guild_config[ctx.guild.id]['log'] is None:
            raise Error.MissingSetting(ctx)

        if log not in logs:
            raise Error.InvalidSetting(ctx)

        await ctx.bot.toggle_log(ctx.guild.id, log)
        await ctx.tick()

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        channel = await self.bot.get_log_channel(message.guild)

        audit = await message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete).flatten()

        user = "message author" if message.author.id == audit[0].user.id else f"{audit[0].user.name} ({audit[0].user.id})"

        if channel is not None and self.bot.guild_config[message.guild.id]['log']['message_logs']:
            e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""**{message.id}** was deleted by **{user}**
**Content**: {message.content}
**Author**: {message.author} ({message.author.id})
""")

            e.set_footer(text="Deleted at")

            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        channel = await self.bot.get_log_channel(messages[0].guild)

        if channel is not None and self.bot.guild_config[messages.guild.id]['log']['message_logs']:
            e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"**{len(messages)}** were bulk deleted.")

            e.set_footer(text="Deleted at")

            await channel.send(embed=e)

def setup(bot):
    bot.add_cog(Logging(bot))