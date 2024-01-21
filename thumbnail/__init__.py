from .thumbnail import Thumbnail
import discord

__red_end_user_data_statement__ = ("This cog does not persistently store data or metadata about users.")

async def setup(bot):
    if discord.__version__[0] == "2":
        await bot.add_cog(Thumbnail(bot))
    else:
        bot.add_cog(Thumbnail(bot))