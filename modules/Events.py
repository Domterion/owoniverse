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

    #######################################################
    #
    # Message Logs
    #
    ########################################################

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        log_channel = await self.bot.get_log_channel(message.guild)

        audit = await message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete).flatten()

        user = "message author" if message.author.id == audit[0].user.id else f"**{audit[0].user.name}** (**{audit[0].user.id}**)"

        if log_channel is not None and self.bot.guild_config[message.guild.id]['log']['message_logs']:
            e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""**{message.id}** was deleted by {user}
**Content**: {message.content}
**Author**: {message.author} ({message.author.id})
""")

            await log_channel.send(embed=e)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        log_channel = await self.bot.get_log_channel(messages[0].guild)

        if log_channel is not None and self.bot.guild_config[messages.guild.id]['log']['message_logs']:
            e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"**{len(messages)}** were bulk deleted.")

            await log_channel.send(embed=e)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        log_channel = await self.bot.get_log_channel(before.guild)

        if log_channel is not None and self.bot.guild_config[before.guild.id]['log']['message_logs']:
            if before.content != after.content:
                e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(),
                                  description=f"""
**{before.id}** was edited 
**Author**: {before.author.name} ({before.author.id})

**Before**: {before.content if len(before.content) < 700 else f"Message content too long"}
**After**: {after.content if len(after.content) < 700 else f"[jump]({after.jump_url})"}
""")

                await log_channel.send(embed=e)

    #######################################################
    #
    # Member Logs
    #
    ########################################################

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        log_channel = await self.bot.get_log_channel(before.guild)

        if log_channel is not None and self.bot.guild_config[before.guild.id]['log']['member_logs']:
            if before.roles != after.roles:
                audit = await before.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update).flatten()

                user = "role owner" if before.id == audit[0].user.id else f"**{audit[0].user.name}** (**{audit[0].user.id}**)"

                roles = before.roles + after.roles
                roles_changed = []

                for r in roles:
                    if r not in before.roles:
                        roles_changed.append(f"**+**{r.name}")
                    if r not in after.roles:
                        roles_changed.append(f"**-**{r.name}")

                e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""**{before.name}** (**{before.id}**) roles were updated by {user}
**Roles**: {", ".join(roles_changed)}
""")

                await log_channel.send(embed=e)

    #######################################################
    #
    # Guild Logs
    #
    ########################################################

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        log_channel = await self.bot.get_log_channel(channel.guild)

        if log_channel is not None and self.bot.guild_config[channel.guild.id]['log']['guild_logs']:
            audit = await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create).flatten()

            data = "Unknown channel type."

            if isinstance(channel, discord.TextChannel):
                data = f"""**Category**: {channel.category}
**Type**: Text
**NSFW**: {channel.is_nsfw()}
"""
            if isinstance(channel, discord.VoiceChannel):
                data = f"""**Category**: {channel.category}
**Type**: Voice
**User limit**: {channel.user_limit if channel.user_limit != 0 else "Unlimited"}
"""

            e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""
**{channel.name}** (**{channel.id}**) was just made by **{audit[0].user.name}** (**{audit[0].user.id}**)

{data}
""")

            await log_channel.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        log_channel = await self.bot.get_log_channel(channel.guild)

        if log_channel is not None and self.bot.guild_config[channel.guild.id]['log']['guild_logs']:
            audit = await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete).flatten()

            e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""
**{channel.name}** (**{channel.id}**) was just deleted by **{audit[0].user.name}** (**{audit[0].user.id}**)""")

            await log_channel.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        log_channel = await self.bot.get_log_channel(before.guild)

        if log_channel is not None and self.bot.guild_config[before.guild.id]['log']['guild_logs']:
            if before.name != after.name:
                audit = await before.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create).flatten()

                e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""
    **{before.name}** was renamed to **{after.name}** (**{after.id}**) by **{audit[0].user.name}** (**{audit[0].user.id}**)""")

                await log_channel.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        log_channel = await self.bot.get_log_channel(role.guild)

        if log_channel is not None and self.bot.guild_config[role.guild.id]['log']['guild_logs']:
            audit = await role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create).flatten()

            e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""
**{role.name}** (**{role.id}**) was just made by **{audit[0].user.name}** (**{audit[0].user.id}**)
**Color**: {role.color}
**Position**: {role.position}
""")

            await log_channel.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        log_channel = await self.bot.get_log_channel(role.guild)

        if log_channel is not None and self.bot.guild_config[role.guild.id]['log']['guild_logs']:
            audit = await role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete).flatten()

            e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""
**{role.name}** (**{role.id}**) was just deleted by **{audit[0].user.name}** (**{audit[0].user.id}**)
""")

            await log_channel.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        log_channel = await self.bot.get_log_channel(before.guild)

        if log_channel is not None and self.bot.guild_config[before.guild.id]['log']['guild_logs']:
            if before.name != after.name:
                audit = await before.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update).flatten()

                e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""
**{before.name}** was renamed to **{after.name}** (**{after.id}**) by **{audit[0].user.name}** (**{audit[0].user.id}**)
""")
                await log_channel.send(embed=e)
            if before.color != after.color:
                audit = await before.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update).flatten()

                e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""
**{before.name}** color was changed from **{before.color}** to **{after.color}** (**{after.id}**) by **{audit[0].user.name}** (**{audit[0].user.id}**)
""")
                await log_channel.send(embed=e)
            if before.permissions != after.permissions:
                audit = await before.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update).flatten()

                permissions = list(before.permissions) + list(after.permissions)
                permissions_changed = []

                for p in permissions:
                    if p not in before.permissions:
                        permissions_changed.append(f"**+**{p[0]}")
                    if p not in after.permissions:
                        permissions_changed.append(f"**-**{p[0]}")

                e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""
**{before.name}** (**{before.id}**) permissions were changed by **{audit[0].user.name}** (**{audit[0].user.id}**)

**Permissions**: {", ".join(permissions_changed)}
""")
                await log_channel.send(embed=e)

    #######################################################
    #
    # Custom/Mod Logs
    #
    ########################################################

    async def on_member_ban(self, guild, user, mod, reason: str, case: int):
        log_channel = await self.bot.get_log_channel(guild)

        if log_channel is not None and self.bot.guild_config[guild.id]['log']['mod_logs']:
            e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""[**{case}**] **{user.name}** (**{user.id}**) was banned by **{mod.name}** (**{mod.id}**)
**Reason**: {reason}
""")
            await log_channel.send(embed=e)

    async def on_member_unban(self, guild, user, mod, reason: str, case: int):
        log_channel = await self.bot.get_log_channel(guild)

        if log_channel is not None and self.bot.guild_config[guild.id]['log']['mod_logs']:
            e = discord.Embed(color=self.bot.config.color, timestamp=datetime.utcnow(), description=f"""[**{case}**] **{user.name}** (**{user.id}**) was unbanned by **{mod.name}** (**{mod.id}**)
**Reason**: {reason}
""")

            await log_channel.send(embed=e)

def setup(bot):
    bot.add_cog(Events(bot))