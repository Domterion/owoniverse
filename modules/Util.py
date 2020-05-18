import asyncio
from datetime import datetime
import sys
import time

import asyncpg
import discord
import psutil
from discord.ext import commands

import config


class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", aliases=["about"], description="Get info about the bot.")
    async def _info(self, ctx):

        ver = discord.version_info
        p_ver = sys.version_info

        cpu_usage = self.bot.process.cpu_percent()
        cpu_count = psutil.cpu_count()
        memory_usage = self.bot.process.memory_full_info().uss / (1024 ** 2)

        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        e = discord.Embed(color=ctx.bot.config.color, description=f"Hello, I am **owoniverse**! I am made by **mellowmarshe#0001**.")

        e.add_field(name="Stats", value=f"""
I'm in **{len(ctx.bot.guilds)}** guilds with **{len(ctx.bot.users)}** users.
Made with **[dpy](https://github.com/Rapptz/discord.py)** version **{ver.major}**.**{ver.minor}**.**{ver.micro}** using Python **{p_ver.major}**.**{p_ver.minor}**.**{p_ver.micro}**

Host:
I'm using **{round(cpu_usage/cpu_count, 2)}**% CPU and **{round(memory_usage, 2)}**MiB of memory.

Links: 
You can add me to your server with **[invite]({ctx.bot.invite})**
""")
        e.add_field(name="Commands used since restart:", value=f"**{ctx.bot.used}**", inline=False)
        e.add_field(name="Latency", value=f"**{round(ctx.bot.latency*1000)}**ms")
        e.add_field(name="Time alive", value=f"I've been alive for **{days}**d **{hours}**h **{minutes}**m.")

        await ctx.send(embed=e)

    @commands.command(name="ping", description="Get the bots ping.")
    async def _ping(self, ctx):
        await ctx.send(f"Ping to websocket is **{round(ctx.bot.latency*1000)}**ms.")

def setup(bot):
    bot.add_cog(Util(bot))