import discord
from discord.ext import commands

from modules import Error
from modules.Events import Events


class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(
                    f"{argument} is not a valid member or ID."
                ) from None
        else:
            can_execute = (
                ctx.author.id == ctx.bot.owner_id
                or ctx.author == ctx.guild.owner
                or ctx.author.top_role > m.top_role
            )

            if not can_execute:
                raise commands.BadArgument(
                    "You cannot perform this action due to role hierarchy."
                )
            return m.id


class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        ban_list = await ctx.guild.bans()
        try:
            member_id = int(argument, base=10)
            entity = discord.utils.find(lambda u: u.user.id == member_id, ban_list)
        except ValueError:
            entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)
        if entity is None:
            raise commands.BadArgument("That user wasn't previously banned.")
        return entity

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(ban_members=True)
    @commands.command(name="ghostban", aliases=["gb"], description="Ghost ban someone, or ban them even if they aren't in the guild.")
    async def _ghostban(self, ctx, user: MemberID, *, reason):
        if len(reason) > 512:
            raise Error.InvalidReason(ctx)

        case = await self.bot.add_case(ctx.guild.id, "ghostban", ctx.author.id, user, reason)
        await self.bot.get_cog("Events").on_member_ghostban(ctx.guild, ctx.author, user, reason, case)

        await ctx.guild.ban(discord.Object(id=user), reason=f"[Ghostban][{case}] {user} for {reason}")

        await ctx.tick()

    @commands.has_permissions(ban_members=True)
    @commands.command(name="ban", aliases=["bean"], description="Bans a member")
    async def _ban(self, ctx, user: discord.Member, *, reason):
        if len(reason) > 512:
            raise Error.InvalidReason(ctx)

        case = await self.bot.add_case(ctx.guild.id, "ban", ctx.author.id, user.id, reason)
        await self.bot.get_cog("Events").on_member_ban(ctx.guild, ctx.author, user, reason, case)

        await ctx.guild.ban(user, reason=f"[Ban][{case}] {user} for {reason}")

        await ctx.tick()

    @commands.has_permissions(ban_members=True)
    @commands.command(name="softban", description="Ban then unban a member to delete their messages")
    async def _softban(self, ctx, user: discord.Member, *, reason):
        if len(reason) > 512:
            raise Error.InvalidReason(ctx)

        case = await self.bot.add_case(ctx.guild.id, "softban", ctx.author.id, user.id, reason)
        await self.bot.get_cog("Events").on_member_softban(ctx.guild, ctx.author, user, reason, case)

        await ctx.guild.ban(user, reason=f"[Softban][{case}] {user} for {reason}")
        await ctx.guild.unban(user, reason=f"[Softban unban][{case}]")

        await ctx.tick()

    @commands.has_permissions(kick_members=True)
    @commands.command(name="kick", description="Kick a member")
    async def _kick(self, ctx, user: discord.Member, *, reason):
        if len(reason) > 512:
            raise Error.InvalidReason(ctx)

        case = await self.bot.add_case(ctx.guild.id, "kick", ctx.author.id, user.id, reason)
        await self.bot.get_cog("Events").on_member_kick(ctx.guild, ctx.author, user, reason, case)

        await ctx.guild.kick(user, reason=f"[Kick][{case}] {user} for {reason}")

        await ctx.tick()

def setup(bot):
    bot.add_cog(Mod(bot))