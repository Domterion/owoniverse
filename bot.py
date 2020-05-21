import asyncio
import os
import sys
from datetime import datetime

import aiohttp
import asyncpg
import discord
import psutil
from discord.ext import commands

import config
import utils

try:
    import uvloop
except ImportError:
    if (sys.platform == "linux"):
        print("UVLoop not detected")
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class owoniverse(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self.get_pre,
            case_insensitive=True,
            description=config.description,
            reconnect=True,
            status=discord.Status.idle,
        )
        self.config = config
        self.session = None
        self.pool = None
        self.loop = asyncio.get_event_loop()
        self.used = 0
        self.process = psutil.Process(os.getpid())
        self.beta = '--beta' in sys.argv
        self.launch_time = datetime.utcnow()
        self.invite = None
        # self.prefixes = {}
        self.guild_config = {}

    async def get_pre(self, bot, message):
        if not message.guild:
            return commands.when_mentioned_or(*self.config.prefix)(bot, message)
        try:
            prefix = self.guild_config[message.guild.id]['prefix']
            if prefix or prefix is not None:
                return commands.when_mentioned_or(prefix)(bot, message)
            else:
                return commands.when_mentioned_or(*self.config.prefix)(bot, message)
        except KeyError:
            return commands.when_mentioned_or(*self.config.prefix)(bot, message)

    async def start(self):
        self.session = aiohttp.ClientSession(loop=self.loop)
        for ext in self.config.extensions:
            try:
                self.load_extension(f"{ext}")
            except Exception as e:
                print(f"Failed to load {ext}, {e}")

        await super().start(self.config.token)

    async def on_ready(self):
        self.pool = await asyncpg.create_pool(
            **self.config.db, max_size=150
        )

        try:
            with open("utils/schema.sql") as f:
                await self.pool.execute(f.read())
        except:
            pass

        for i in await self.pool.fetch("SELECT * FROM settings"):
            self.guild_config[i['id']] = {"prefix": i['prefix'], "log": {"channel": i['log'], "member_logs": i['member_logs'], "mod_logs": i['mod_logs'], "message_logs": i['message_logs'], "guild_logs": i['guild_logs']}}


        await self.change_presence(
            status=discord.Status.dnd,
            activity=discord.Game(f"I don't know."),
        )

        permissions = discord.Permissions()

        permissions.update(
            add_reactions=True,
            attach_files=True,
            change_nickname=True,
            embed_links=True,
            external_emojis=True,
            manage_messages=True,
            read_messages=True,
            read_message_history=True,
            send_messages=True,
            send_tts_messages=True,
            view_audit_log=True,
        )

        self.invite = discord.utils.oauth_url(self.user.id, permissions=permissions)

        print(
            f"Bot started with {len(self.guilds)} guilds and {len(self.users)} users."
        )

    async def on_message(self, message):
        if message.author.bot:
            return

        ctx = await self.get_context(message)

        if ctx.command:
            await self.process_commands(message)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=utils.context.Context)

        if ctx.command is None:
            return

        self.used += 1
        await self.invoke(ctx)

    async def add_to_cache(self, guild: int, logging: bool=False):
        if guild in self.guild_config:
            return

        self.guild_config[guild] = {"prefix": None, "log": {"channel": None, "member_logs": logging, "mod_logs": logging, "message_logs": logging, "guild_logs": logging}}

    async def add_prefix(self, guild: int, prefix: str):
        await self.add_to_cache(guild)

        self.guild_config[guild]['prefix'] = prefix
        await self.pool.execute("INSERT INTO settings(id, prefix) VALUES ($1, $2) ON CONFLICT (id) DO UPDATE SET prefix = $2", guild, prefix)

    async def remove_prefix(self, guild: int):
        await self.add_to_cache(guild)

        self.guild_config[guild]['prefix'] = None
        await self.pool.execute("UPDATE settings SET prefix = NULL WHERE id = $1", guild)

    async def add_log(self, guild: int, channel: int):
        await self.add_to_cache(guild, True)

        self.guild_config[guild]['log']['channel'] = channel
        await self.pool.execute("INSERT INTO settings(id, log) VALUES ($1, $2) ON CONFLICT (id) DO UPDATE SET log = $2", guild, channel)

    async def remove_log(self, guild: int):
        await self.add_to_cache(guild)

        self.guild_config[guild]['log']['channel'] = None
        await self.pool.execute("UPDATE settings SET log = NULL WHERE id = $1", guild)

    async def toggle_log(self, guild: int, log: str):
        await self.add_to_cache(guild)

        current = self.guild_config[guild]['log'][log]

        self.guild_config[guild]['log'][log] = not current
        await self.pool.execute(f"UPDATE settings SET {log} = $1 WHERE id = $2", not current, guild)

    async def get_log_channel(self, guild):
        try:
            return guild.get_channel(self.guild_config[guild.id]['log']['channel'])
        except KeyError:
            return

    def get_guild_config(self, guild: int):
        try:
            return self.guild_config[guild]
        except KeyError:
            return None

    async def remove_from_bot(self, guild: discord.Guild):
        del self.guild_config[guild.id]
        await self.pool.execute("DELETE FROM settings WHERE id = $1", guild.id)

    async def add_case(self, guild: int, action: str, mod: int, user: int, reason: str):
        case = await self.pool.fetchval("INSERT INTO cases(guild, action, mod, \"user\", reason) VALUES ($1, $2, $3, $4, $5) RETURNING id", guild, action, mod, user, reason)
        return case

    async def get_case(self, guild: int, case: int):
        case = await self.pool.fetchrow("SELECT * FROM cases WHERE guild = $1 AND id = $2", guild, case)
        return case

    async def get_all_cases(self, guild: int, limit: int, mod: int = None):
        if mod is None:
            case = await self.pool.fetch("SELECT * FROM cases WHERE guild = $1 LIMIT $2", guild, limit)
        if mod is not None:
            case = await self.pool.fetch("SELECT * FROM cases WHERE guild = $1 AND mod = $2 LIMIT $3", guild, mod, limit)
        return case

    async def modify_case(self, guild: int, id: int, mod: int, owner: bool, reason: str):
        if owner:
            case = await self.pool.fetchval("UPDATE cases SET reason=$1 WHERE guild = $2 AND id = $3 RETURNING id", reason, guild, id)
        if not owner:
            case = await self.pool.fetchval("UPDATE cases SET reason=$1 WHERE guild = $2 AND id = $3 AND mod = $4 RETURNING id", reason, guild, id, mod)
        return case


if __name__ == "__main__":
    owoniverse().run()