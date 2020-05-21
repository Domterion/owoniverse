import discord
from discord.ext import commands

class InvalidOrMissingSetting(commands.CommandError):
    def __init__(self, ctx):
        super().__init__(f"You are using an invalid or missing setting for **{ctx.command}**. Reasons can only be upto **512** characters and prefixes upto **20**.")

class NoConfig(commands.CommandError):
    def __init__(self):
        super().__init__(f"Your guild has no config, get started by setting your prefix or log channel.")

class NoCase(commands.CommandError):
    def __init__(self):
        super().__init__("That case doesn't exist or doesn't belong to you or the guild.")

class InvalidLimit(commands.CommandError):
    def __init__(self, limit):
        super().__init__(f"**{limit}** invalid limit, limit can't be more than 15.")

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
        custom_errors = (InvalidOrMissingSetting, NoConfig, NoCase, InvalidLimit)

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