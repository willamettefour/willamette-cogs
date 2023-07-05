from .discordinfo import DiscordInfo


async def setup(bot):
    cog = DiscordInfo(bot)
    await bot.add_cog(cog)