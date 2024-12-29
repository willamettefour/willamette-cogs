import discord
import os
import random, string
import requests
import time
import whirlpool

from redbot.core import commands


class Thumbnail(commands.Cog):
    """Get a YouTube video's thumbnail from its ID."""

    def __init__(self, bot):
        global default_hash
        default_hash = "A005E211EDD213842ED25A9EBFCD4D4E19A3A69DD2D899F899B4307740110651880FF8A8D2F7B95188AF87D62ECC09F401E1A405050A6A4A228497C51EAD3D88"
        self.bot = bot

    async def hashing(self, code, quality):
        script_path = os.path.realpath(__file__)
        script_dir = os.path.dirname(script_path)
        directory = "imgcache"
        path = os.path.join(script_dir, directory)
        os.makedirs(path, exist_ok=True)
        img_name = ''.join(random.choice(string.ascii_letters) for _ in range(32))
        image_url = f"https://i.ytimg.com/vi/{code}/{quality}.jpg"
        img_data = requests.get(image_url).content
        h = whirlpool.new()
        with open(f'{script_dir}/imgcache/{img_name}.jpg', 'wb') as handler:
            handler.write(img_data)
        with open(f'{script_dir}/imgcache/{img_name}.jpg', 'rb') as f:
            file_data = f.read()
        hasher = whirlpool.new()
        hasher.update(file_data)
        file_hash = hasher.hexdigest()
        os.remove(f"{script_dir}/imgcache/{img_name}.jpg")
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
                        thing = maid_url + ".gif?size=2048" if requests.get(maid_url).headers['content-type'] == "image/gif" else maid_url + ".webp?size=2048&quality=lossless"
        embed.set_footer(text = f"executed by {ctx.author}", icon_url=thing)
        return embed

    @commands.command()
    async def thumbnail(self, ctx, code: str):
        """Get a YouTube video's thumbnail from its ID."""
        if len(code) != 11:
            await ctx.send("That ID appears to be invalid!")
        else:
            file_hash = await self.hashing(code, "maxresdefault")
            if file_hash.upper() == default_hash:
                file_hash = await self.hashing(code, "hqdefault")
                if file_hash.upper() == default_hash:
                    await ctx.send("the code provided is either invalid or the video has no thumbnail")
                else:
                    async with ctx.typing():
                        url = f"https://i.ytimg.com/vi/{code}/hqdefault.jpg"
                        embed = await self.build_embed(ctx, url)
                        await ctx.send(embed=embed)
            else:
                url = f"https://i.ytimg.com/vi/{code}/maxresdefault.jpg"
                embed = await self.build_embed(ctx, url)
                await ctx.send(embed=embed)