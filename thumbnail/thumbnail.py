from redbot.core import commands
import discord
import requests

class Thumbnail(commands.Cog):
    """Get a YouTube video's thumbnail from its ID."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def thumbnail(self, ctx, code: str):
        """Get a YouTube video's thumbnail from its ID."""
        if len(code) != 11:
            await ctx.send("That ID appears to be invalid!")
        else:
            embed = discord.Embed(title="here's the thumbnail!", color=0xff0000)
            embed.set_image(url=f"https://i.ytimg.com/vi/{code}/maxresdefault.jpg")
            embed.add_field(name="not working?", value="[try this link](https://i.ytimg.com/vi/{}/hqdefault.jpg)".format(code))
            if ctx.author.avatar is None:
                thing = ctx.author.default_avatar
            else:
                if discord.__version__[0] == "2":
                    thing = str(ctx.author.display_avatar.replace(size=2048, static_format="webp"))
                    if ctx.author.display_avatar.is_animated() is False:
                        thing += "&quality=lossless"
                else:
                    thing = str(ctx.author.avatar_url) + "&quality=lossless"
                    if ctx.author.is_avatar_animated():
                        thing = ctx.author.avatar_url_as(format="gif", size=2048)
                    if ctx.guild:
                        req = await self.bot.http.request(discord.http.Route("GET", "/guilds/{gid}/members/{uid}", gid=ctx.guild.id, uid=ctx.author.id))
                        thing_av = req["avatar"]
                        if thing_av:
                            maid_url = f"https://cdn.discordapp.com/guilds/{ctx.guild.id}/users/{ctx.author.id}/avatars/{thing_av}"
                            thing = maid_url + ".gif?size=2048" if requests.get(maid_url).headers['content-type'] == "image/gif" else maid_url + ".webp?size=2048&quality=lossless"
            embed.set_footer(text = f"executed by {ctx.author}", icon_url=thing)
            await ctx.send(embed=embed)