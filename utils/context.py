from discord.ext import commands


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def tick(self):
        await self.message.add_reaction(self.bot.config.emotes["tick"])

    async def cross(self):
        await self.message.add_reaction(self.bot.config.emotes["cross"])
