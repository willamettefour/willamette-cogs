import asyncio
import aiohttp
import discord
import re
import requests
import whirlpool

from redbot.core import commands


class Thumbnail(commands.Cog):
    """Get a YouTube video's thumbnail from its ID."""
    default_hash = "A005E211EDD213842ED25A9EBFCD4D4E19A3A69DD2D899F899B4307740110651880FF8A8D2F7B95188AF87D62ECC09F401E1A405050A6A4A228497C51EAD3D88"

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        await self.session.close()
        
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass

    async def hashing(self, ctx, code, quality):
        url = f"https://i.ytimg.com/vi/{code}/{quality}.jpg"
        hasher = whirlpool.new()
        try:
            with requests.get(url, stream=True) as response:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        hasher.update(chunk)
        except requests.exceptions.HTTPError:
            if quality == "maxresdefault":
                resolution = "high"
            else:
                resolution = "low"
            await ctx.send(f"failed to download {resolution} resolution thumbnail with error `{response.status_code}`.")
        file_hash = hasher.hexdigest()
        return file_hash
 
    async def build_embed(self, ctx, url):
        embed = discord.Embed(title="here's the thumbnail!", color=0xff0000)
        embed.set_image(url=url)
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
                        async with self.session.head(maid_url, allow_redirects=True) as res:
                            file_type = res.headers.get("content-type", "").split(";")[0].strip().lower()
                        thing = maid_url + ".gif?size=2048" if file_type == "image/gif" else maid_url + ".webp?size=2048&quality=lossless"
        embed.set_footer(text = f"executed by {ctx.author}", icon_url=thing)
        return embed

    @commands.command()
    async def thumbnail(self, ctx, code: str):
        """Get a YouTube video's thumbnail from its ID."""
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", code):
            return await ctx.send("that ID appears to be invalid!")
        async with ctx.typing():
            file_hash = await self.hashing(ctx, code, "maxresdefault")
            if file_hash.upper() == Thumbnail.default_hash:
                file_hash = await self.hashing(ctx, code, "hqdefault")
                if file_hash.upper() == Thumbnail.default_hash:
                    await ctx.send("the code provided is either invalid or the video has no thumbnail.")
                else:
                    url = f"https://i.ytimg.com/vi/{code}/hqdefault.jpg"
                    embed = await self.build_embed(ctx, url)
                    await ctx.send(embed=embed)
            else:
                url = f"https://i.ytimg.com/vi/{code}/maxresdefault.jpg"
                embed = await self.build_embed(ctx, url)
                await ctx.send(embed=embed)