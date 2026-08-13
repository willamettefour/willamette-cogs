import discord

from redbot.core.utils import get_end_user_data_statement_or_raise

from .thumbnail import Thumbnail

__red_end_user_data_statement__ = get_end_user_data_statement_or_raise(__file__)

async def setup(bot):
    if discord.__version__[0] == "2":
        await bot.add_cog(Thumbnail(bot))
    else:
        bot.add_cog(Thumbnail(bot))