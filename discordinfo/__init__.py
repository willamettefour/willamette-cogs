from .discordinfo import DiscordInfo

def setup(bot):
    bot.add_cog(DiscordInfo(bot))