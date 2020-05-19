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


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        channel = await self.bot.get_log_channel(message.guild)

        audit = await message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete).flatten()

        user = "message author" if message.author.id == audit[0].user.id else f"**{audit[0].user.name}** (**{audit[0].user.id}**)"

        if channel is not None and self.bot.guild_config[message.guild.id]['log']['message_logs']:
            e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""**{message.id}** was deleted by {user}
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

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        channel = await self.bot.get_log_channel(before.guild)

        if channel is not None and self.bot.guild_config[before.guild.id]['log']['member_logs']:
            if before.roles != after.roles:
                audit = await before.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update).flatten()

                user = "role owner" if before.id == audit[0].user.id else f"**{audit[0].user.name}** (**{audit[0].user.id}**)"

                roles = before.roles + after.roles
                roles_changed = []

                for r in roles:
                    if r not in before.roles:
                        roles_changed.append(f"+{r.name}")
                    if r not in after.roles:
                        roles_changed.append(f"-{r.name}")

                e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""**{before.name}** (**{before.id}**) roles were updated by {user}
**Roles**: {", ".join(roles_changed)}
""")

                await channel.send(embed=e)

    # Custom errors

    async def on_member_ban(self, guild, user, mod, reason: str, case: int):
        channel = await self.bot.get_log_channel(guild)

        if channel is not None and self.bot.guild_config[guild.id]['log']['mod_logs']:
            e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""[**{case}**] **{user.name}** (**{user.id}**) was banned by **{mod.name}** (**{mod.id}**)
**Reason**: {reason}
""")

            e.set_footer(text="Banned at")

            await channel.send(embed=e)

    async def on_member_unban(self, guild, user, mod, reason: str, case: int):
        channel = await self.bot.get_log_channel(guild)

        if channel is not None and self.bot.guild_config[guild.id]['log']['mod_logs']:
            e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""[**{case}**] **{user.name}** (**{user.id}**) was unbanned by **{mod.name}** (**{mod.id}**)
**Reason**: {reason}
""")

            e.set_footer(text="Unbanned at")

            await channel.send(embed=e)

def setup(bot):
    bot.add_cog(Events(bot))