import asyncio
import discord
import os
import random, string
import requests
import time
import zipfile

from redbot.core import checks, commands, Config


class Emoji(commands.Cog):
    """Emoji-related tools"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=8086, force_registration=True)
        self.config.register_user(image_format=[])

    @commands.group()
    async def emoji(self, ctx):
        """Emoji-related tools"""
    
    @emoji.command()
    async def format(self, ctx, file_format: str):
        """
        Changes the format emoji will be displayed in/saved as. (default: lossless WebP)
        Available options are png, jpeg, webp, and webp_ls (lossless).
        Does not affect the format used for adding emoji; also note that JPEG doesn't support transparency.
        """
        file_format = file_format.lower()
        if file_format not in ["png", "jpeg", "jpg", "webp", "webp_ls"]:
            return await ctx.send(f"invalid file format specified! use `{ctx.prefix}help emoji format` for more info") 
        saved_format = await self.config.user(ctx.author).image_format()
        if file_format == "jpg":
            file_format = "jpeg"
        await self.config.user(ctx.author).image_format.set(file_format)
        if file_format == "webp":
            file_format = "WebP"
        elif file_format == "webp_ls":
            file_format = "lossless WebP"
        else:
            file_format = file_format.upper()
        await ctx.send(f"your default format for saving/displaying emoji is now `{file_format}`")
        
    @emoji.command()
    async def info(self, ctx, emoji: discord.Emoji):
        """Get info on a custom emoji."""
        embed = discord.Embed(title=emoji.name, color=await ctx.embed_color())
        heathen = int(time.mktime(emoji.created_at.timetuple()))
        embed.add_field(name="emoji created:", value=f"<t:{heathen}:D> (<t:{heathen}:R>)")
        embed.add_field(name="animated?", value="✅" if emoji.animated else "❌", inline=False)
        saved_format = await self.config.user(ctx.author).image_format()
        emoji_url = emoji.url
        if not emoji.animated:
            if discord.__version__[0] == "2":
                if not saved_format or saved_format == "webp_ls":
                    emoji_url = emoji.url.replace(".png", ".webp?quality=lossless")
                if saved_format == "webp":
                    emoji_url = emoji.url.replace(".png", ".webp")
                if saved_format == "jpeg":
                    emoji_url = emoji.url.replace(".png", ".jpg")
            else:
                if not saved_format or saved_format == "webp_ls":
                    emoji_url = str(emoji.url_as(format="webp")) + "?quality=lossless"
                if saved_format == "webp":
                    emoji_url = str(emoji.url_as(format="webp"))
                if saved_format == "jpeg":
                    emoji_url = str(emoji.url_as(format="jpg"))
        embed.set_thumbnail(url=emoji_url)
        embed.set_footer(text=f"ID: {emoji.id}")
        await ctx.send(embed=embed)
        
    @emoji.command()
    @checks.admin()
    @commands.cooldown(rate=1, per=30)
    async def add(self, ctx, emoji: discord.Emoji, name: str=None):
        """Adds a custom emoji from another server."""
        try:
            if name is None:
                name = emoji.name
            if discord.__version__[0] == "2":
                await ctx.guild.create_custom_emoji(name=name, image=await emoji.read(), reason=f"emoji added by {ctx.author.display_name} through {ctx.me.display_name}")
            else:
                await ctx.guild.create_custom_emoji(name=name, image=await emoji.url.read(), reason=f"emoji added by {ctx.author.display_name} through {ctx.me.display_name}")
            await ctx.message.add_reaction("✅")
        except:
            await ctx.send("i couldn't add that emoji! please check if the guild has reached its limit")
            
    @emoji.command()
    @commands.guild_only()
    async def zip(self, ctx):
        """Creates a zip file with the current server's emojis."""
        if ctx.guild.emojis is None:
            return await ctx.send("this server has no custom emojis")
        async with ctx.typing():
            script_path = os.path.realpath(__file__)
            script_dir = os.path.dirname(script_path)
            directory = ''.join(random.choice(string.ascii_letters) for _ in range(32))
            path = os.path.join(script_dir, directory)
            os.makedirs(path, exist_ok=True)
            saved_format = await self.config.user(ctx.author).image_format()
            for emoji in ctx.guild.emojis:
                emoji_url = emoji.url
                extension = "gif"
                if not emoji.animated:
                    if discord.__version__[0] == "2":
                        if not saved_format or saved_format == "webp_ls":
                            extension = "webp"
                            emoji_url = emoji.url.replace(".png", ".webp?quality=lossless")
                        if saved_format == "webp":
                            extension = "webp"
                            emoji_url = emoji.url.replace(".png", ".webp")
                        if saved_format == "jpeg":
                            extension = "jpg"
                            emoji_url = emoji.url.replace(".png", ".jpg")
                    else:
                        if not saved_format or saved_format == "webp_ls":
                            extension = "webp"
                            emoji_url = str(emoji.url_as(format="webp")) + "?quality=lossless"
                        if saved_format == "webp":
                            extension = "webp"
                            emoji_url = str(emoji.url_as(format="webp"))
                        if saved_format == "jpeg":
                            extension = "jpg"
                            emoji_url = str(emoji.url_as(format="jpg"))
                img_data = requests.get(emoji_url).content
                with open(f'{script_dir}/{directory}/{emoji.name}.{extension}', 'wb') as handler:
                    handler.write(img_data)
            with zipfile.ZipFile(f'{script_dir}/{directory}.zip', 'w') as zipf:
                for foldername, subfolders, filenames in os.walk(path):
                    for filename in filenames:
                        file_path = os.path.join(foldername, filename)
                        zipf.write(file_path, os.path.relpath(file_path, path))
            file = discord.File(f'{script_dir}/{directory}.zip')
            try:
                await ctx.send(file=file)
            except:
                await ctx.send("i can't send the zip archive! it's possible the file is bigger than the server's file limit, in which case consider using a lossy format if you weren't before")
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename) 
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(path)
            os.remove(f"{script_dir}/{directory}.zip")
            await ctx.message.add_reaction("✅")