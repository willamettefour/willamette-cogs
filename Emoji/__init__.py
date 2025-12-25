from .emoji import Emoji
import discord

async def setup(bot):
    if discord.__version__[0] == "2":
        await bot.add_cog(Emoji(bot))
    else:
        bot.add_cog(Emoji(bot))