import discord
from discord.ext import commands


class InvalidPrefix(commands.CommandError):
    def __init__(self, ctx):
        super().__init__(f"Prefixes can only be upto **20** characters in length.")

class InvalidSetting(commands.CommandError):
    def __init__(self, ctx):
        super().__init__(f"You are using an invalid setting for **{ctx.command}**.")

class MissingSetting(commands.CommandError):
    def __init__(self, ctx):
        super().__init__(f"You are missing a setting for **{ctx.command}**.")

class NoConfig(commands.CommandError):
    def __init__(self, ctx):
        super().__init__(f"Your guild has no config, get started by setting your prefix or log channel.")

class InvalidReason(commands.CommandError):
    def __init__(self, ctx):
        super().__init__(f"Reasons can only be upto **512** characters in length.")

class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, "on_error"):
            return

        errors = (
            commands.NoPrivateMessage,
            commands.CommandInvokeError,
            commands.UserInputError,
        )
        custom_errors = (InvalidPrefix, MissingSetting, InvalidSetting, NoConfig, InvalidReason)

        if isinstance(error, errors):
            await ctx.send(error)
        elif isinstance(error, discord.Forbidden):
            pass
        elif isinstance(error, commands.NotOwner):
            await ctx.send("This is an owner only command.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"Invalid argument. Did you type it correct?")
        elif isinstance(error, commands.TooManyArguments):
            await ctx.send(f"Too many arguments. Try less?")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(error)
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(f"{ctx.command} is disabled.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                f'I need the permission {", ".replace(error.missing_perms)}. You can check my role or channel overrides to find permissions.'
            )
        elif isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            seconds = round(seconds, 2)
            hours, remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(
                f"You are on cooldown for **{hours}**h **{minutes}**m **{seconds}**sec"
            )

        elif isinstance(error, custom_errors):
            await ctx.send(error)
        else:
            print(error)


def setup(bot):
    bot.add_cog(Error(bot))