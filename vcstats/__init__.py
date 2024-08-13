from .vcstats import Vcstats
import discord

__red_end_user_data_statement__ = ("This cog does not persistently store data or metadata about users.")

async def setup(bot):
    if discord.__version__[0] == "2":
        await bot.add_cog(Vcstats(bot))
    else:
        bot.add_cog(Vcstats(bot))