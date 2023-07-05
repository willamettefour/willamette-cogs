from .discordinfo import DiscordInfo

async def setup(bot):
    await bot.add_cog(DiscordInfo(bot))