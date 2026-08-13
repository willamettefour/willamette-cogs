import asyncio
import aiohttp
import discord
import io
import math
import os
import random, string
import re
import requests
import textwrap
import urllib.parse
import validators

from discord.ui import button, View, Button
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops
from redbot.core import commands, Config
from redbot.core.data_manager import bundled_data_path, cog_data_path
from word2num import word2num

from .claudescorner import draw_text_with_glass, to_rgb_tuple, validate_color

class Bio(commands.Cog):
    """Create and display Bios."""
    full_socials = ["instagram", "tumblr", "cashapp"]
    allowed_socials = ["carrd", "lastfm", "linktree", "instagram", "tumblr", "cashapp"]
    types = ["image/avif", "image/gif", "image/jpeg", "image/png", "image/webp"]
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=4153800057, force_registration=True)
        default_member = {"description": None, "image": None, "socials": {}, "color": "#000000"}
        default_global = {"max_file_size": 10}
        self.config.register_member(**default_member)
        self.config.register_global(**default_global)
        self.session = aiohttp.ClientSession()
        
    async def cog_unload(self):
        await self.session.close()
        
    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        all_members = await self.config.all_members()
        for guild_id, members in all_members.items():
            if user_id in members:
                image = await self.config.member_from_ids(guild_id, user_id).image()
                if image is not None:
                    os.remove(cog_data_path(self) / "backgrounds" / image)
                await self.config.member_from_ids(guild_id, user_id).clear()
 
    async def ripper(self, ctx, url, ext_helper):
        max_file_size = await self.config.max_file_size()
        max_bytes = max_file_size * 1024**2
        cleaned_url = urllib.parse.urlparse(url).path
        original_name = Path(cleaned_url).name.split(".")
        if original_name[-1] not in ["avif", "gif", "jpeg", "jpg", "jfif", "png", "webp"]:
            extensions = ["avif", "gif", "jpeg", "png", "webp"]
            file_ext = extensions[ext_helper]
        else:
            file_ext = original_name[-1]
        file_name = "".join(random.choice(string.ascii_letters) for _ in range(32)) + "." + file_ext
        dir_path = cog_data_path(self) / "backgrounds"
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = dir_path / file_name
        while file_path.exists() is True:
            file_name = "".join(random.choice(string.ascii_letters) for _ in range(32)) + "." + file_ext
            file_path = dir_path / file_name
        try:
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                total = 0
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            total += len(chunk)
                            if total > max_bytes:
                                file_path.unlink(missing_ok=True)
                                return await ctx.send(f"that file is too large (max {max_file_size} MiB).")
                            file.write(chunk)
            await self.config.member(ctx.author).image.set(file_name)
            await ctx.send("your attachment will now be used as your Bio's image.")
        except requests.exceptions.HTTPError:
            await ctx.send(f"failed to download attachment with error `{response.status_code}`.")

    async def corner_rounding(self, image):
        if image.mode in ["LA", "PA"]:
            image = image.convert(mode = "RGBA")
        if image.mode in ["1", "L", "P"]:
            image = image.convert(mode = "RGB")
        mask = Image.new(mode = "L", size = image.size, color = 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), image.size], 8, fill=255)
        if image.mode == "RGBA":
            alpha = image.getchannel("A")
            if alpha.getextrema()[0] == 255:
                image = image.convert(mode = "RGB")
            else:
                mask = ImageChops.multiply(alpha, mask)
        image.putalpha(mask)
        return image
    
    async def r_text(self, member, description, color, image, the_everything_app):
        if color == "random":
            font_color = tuple(random.randint(0, 255) for _ in range(3))
        else:
            font_color = to_rgb_tuple(color)
        medium_font32 = ImageFont.truetype(bundled_data_path(self) / "fonts" / "IBMPlexSans-Medium.ttf", size=32)
        bold_font = ImageFont.truetype(bundled_data_path(self) / "fonts" / "IBMPlexSans-Bold.ttf", size=32)
        blocks = [
            ((the_everything_app[0], 13), "about", medium_font32),
            ((the_everything_app[1], 13), textwrap.fill(member.display_name, width=12), bold_font),
        ]
        if description is not None:
            font20 = ImageFont.truetype(bundled_data_path(self) / "fonts" / "IBMPlexSans-Light.ttf", size=20)
            blocks.append(((the_everything_app[0], 50 + (math.ceil(len(member.display_name)/12) - 1)*37), textwrap.fill(description, width=27), font20))
        draw_text_with_glass(image, blocks, fill = font_color)
            
    async def buttons(self, socials):
        view = discord.ui.View()
        for social in socials.keys():
            if social == "carrd":
                button = discord.ui.Button(label="carrd", url=f"https://{socials[social]}.carrd.co")
            if social == "cashapp":
                button = discord.ui.Button(label="Cash App", url=f"https://cash.app/${socials[social]}")
            if social == "lastfm":
                button = discord.ui.Button(label="last.fm", url=f"https://www.last.fm/user/{socials[social]}")
            if social == "linktree":
                button = discord.ui.Button(label="linktree", url=f"https://linktr.ee/{socials[social]}")
            if social == "tumblr":
                button = discord.ui.Button(label="Tumblr", url=f"https://{socials[social]}.tumblr.com")
            if social == "instagram":
                button = discord.ui.Button(label="instagram", url=f"https://www.instagram.com/{socials[social]}")
            view.add_item(item=button)
        return view

    @commands.command()
    @commands.guild_only()
    async def bio(self, ctx, member: discord.Member=None):
        """Shows a member's Bio."""
        # Your code will go here
        if ctx.invoked_subcommand is not None:
            return
        if member is None:
            member = ctx.author
        socials = await self.config.member(member).socials()
        description = await self.config.member(member).description()
        image = await self.config.member(member).image()
        color = await self.config.member(member).color()
        if not socials and description is None and image is None:
            return await ctx.send("the requested member doesn't have enough info set for a profile.")
        async with ctx.typing():
            font = ImageFont.truetype(bundled_data_path(self) / "fonts" / "IBMPlexSans-Light.ttf", size=16)
            medium_font = ImageFont.truetype(bundled_data_path(self) / "fonts" / "IBMPlexSans-Medium.ttf", size=24)
            url = member.default_avatar if member.avatar is None else str(member.avatar.replace(size=2048, format="webp")) + "&quality=lossless"
            avatar_temp = io.BytesIO()
            with requests.get(url, stream=True) as response:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        avatar_temp.write(chunk)
                avatar_temp.seek(0)
            avatar = Image.open(avatar_temp)
            scaled_av = avatar.resize(size = (258, 258), resample = Image.Resampling.LANCZOS)
            rounded_av = await self.corner_rounding(scaled_av)
            full_size = False
            true_social = [social for social in socials.keys() if social in Bio.full_socials]
            false_social = [social for social in socials.keys() if social not in Bio.full_socials]
            if true_social:
                full_size = True
            height = 306 + (len(true_social)*44) if full_size is True else 258
            if socials:
                view = await self.buttons(socials)
            if true_social:
                lb = Image.new(mode = "RGBA", size = (258, height), color = (196, 196, 196))
                lb_rounded = await self.corner_rounding(lb)
                lb_draw = ImageDraw.Draw(lb_rounded)
                lb_draw.text(xy = (15, 266), text = "socials", fill = (0, 0, 0), font = medium_font)
                social_height = 306
                for social in true_social:
                    logo = Image.open(bundled_data_path(self) / "logos" / f"{social}.webp")
                    lb_draw.text(xy = (59, social_height + 3) if len(socials[social]) <= 25 else (59, social_height - 7), text = textwrap.fill(socials[social], width=25), fill = (0, 0, 0), font = font)
                    lb_rounded.alpha_composite(im = logo, dest = (15, social_height))
                    social_height += 44
                lb_rounded.alpha_composite(im = rounded_av)
                if description is None and image is None:
                    profile_temp = io.BytesIO()
                    lb_rounded.save(profile_temp, "WEBP", lossless=True, quality=100, method=6)
                    profile_temp.seek(0)
                    file = discord.File(profile_temp, filename="profile.webp")
                    return await ctx.send(file=file, view=view)
            if description is not None or image is not None:
                complete = Image.new(mode = "RGBA", size = (822, height))
                if true_social:
                    complete.paste(im = lb_rounded)
                else:
                    complete.paste(im = rounded_av)
                the_everything_app = [22, 116]
                if image is None:
                    the_everything_app = [x + 283 for x in the_everything_app]
                    await self.r_text(member, description, color, complete, the_everything_app)
                else:
                    dir_path = cog_data_path(self) / "backgrounds"
                    file_path = dir_path / image
                    background_img = Image.open(file_path)
                    background_img = ImageOps.fit(image = background_img, size = (539, height), method = Image.Resampling.LANCZOS)
                    background_rounded = await self.corner_rounding(background_img)
                    await self.r_text(member, description, color, background_rounded, the_everything_app)
                    complete.paste(im = background_rounded, box = (283, 0))
                profile_temp = io.BytesIO()
                complete.save(profile_temp, "WEBP", lossless=True, quality=100, method=6)
                profile_temp.seek(0)
                file = discord.File(profile_temp, filename="profile.webp")
                embed = discord.Embed(color=await ctx.embed_color())
                embed.add_field(name="IMPORTANT!", value=f"this cog doesn't check for account ownership", inline=False)
                if false_social:
                    embed.set_footer(text="for legal reasons, these platforms cannot be displayed in the main Bio image")
                    for social in false_social:
                        if social == "carrd" or social == "linktree":
                            name = social
                        else:
                            name = "last.fm"
                        embed.add_field(name=name, value=f"{socials[social]}")
                try:
                    await ctx.send(file=file, embed=embed, view=view)
                except UnboundLocalError:
                    await ctx.send(file=file, embed=embed)
                
    @commands.command()
    @commands.guild_only()
    async def bioset(self, ctx, field: str, *, value: str=None):
        """
        Set a field to a value.
        Bio colors must be in hexadecimal format (eg. `#FFFF00`), an 8-bit tuple (eg. `(255, 255, 0)`), or `random` to set random bio colors.
        Attach an avif, gif, jpeg, png, or webp file when setting a bio image.
        """
        member = ctx.author
        field = field.lower()
        if value is None and field != "image":
            return await ctx.send("no value was given for the given Bio field.")
        other_params = ["description", "image"]
        colorz = ["color", "colour"]
        if field in Bio.allowed_socials:
            if not re.fullmatch(r"[A-Za-z0-9_.-]{1,32}", value):
                return await ctx.send("that doesn't look like a valid handle! only letters, numbers, and the following punctuation marks are allowed, up to 32 characters: '.', '_', and '-'.")
            socials = await self.config.member(member).socials()
            if field in socials.keys():
                await ctx.send(f"you already have something set for `{field}`; would you like to replace what's currently set? (yes/no)")
                def check(msg):
                    return msg.author == ctx.author and msg.channel == ctx.channel
                try:
                    msg = await ctx.bot.wait_for('message', check=check, timeout=60)
                    if msg.content.lower() == "yes":
                        socials[field] = value
                        await self.config.member(member).socials.set(socials)
                        return await ctx.send(f"`{field}` has been set to `{value}`")
                    elif msg.content.lower() == "no":
                        return await ctx.send(f"`{field}` will remain set to `{value}`")
                    else:
                        await ctx.send("the input wasn't valid! please try again.")
                except asyncio.TimeoutError:
                    return await ctx.send("sorry, you didn't reply in time!")
            else:
                socials[field] = value
                await self.config.member(member).socials.set(socials)
                return await ctx.send(f"`{field}` has been set to `{value}`")
        elif field in other_params:
            if field == "image":
                url = None
                if ctx.message.attachments:
                    url = ctx.message.attachments[0].url
                else:
                    return await ctx.send("no image was attached (links are not accepted).")
                async with self.session.head(url, allow_redirects=True) as res:
                    file_type = res.headers.get("content-type", "").split(";")[0].strip().lower()
                if file_type in Bio.types:
                    ext_helper = Bio.types.index(file_type)
                    content_length = res.headers.get("content-length")
                    if content_length is not None:
                        try:
                            max_file_size = await self.config.max_file_size()
                            max_bytes = max_file_size * 1024**2
                            if int(content_length) > max_bytes:
                                return await ctx.send(f"that file is too large (max {max_file_size} MiB).")
                        except ValueError:
                            pass
                    async with ctx.typing():        
                        await self.ripper(ctx, url, ext_helper)
                else:
                    return await ctx.send(f"the attached file isn't a supported image format (avif, gif, jpeg, png, webp).")
            if field == "description":
                true_social = [social for social in socials.keys() if social in Bio.full_socials]
                max_desc_length = 162 - math.ceil(((math.ceil(len(member.display_name)/12) - 1)*37)/25)*27
                if true_social:
                    max_desc_length = 189 + math.floor(len(true_social)*44/25)*27 - math.ceil(((math.ceil(len(member.display_name)/12) - 1)*37)/25)*27
                if len(value) > max_desc_length:
                    return await ctx.send(f"your description is too long (your limit is `{max_desc_length}` characters).")
                description = await self.config.member(member).description()
                if description == value:
                    await ctx.send("your Bio's description already has that value.")
                else:
                    await self.config.member(member).description.set(value)
                    await ctx.send("your Bio's description has been set.")
        elif field in colorz:
            current_color = await self.config.member(member).color()   
            if value.lower() == "random":
                if current_color == "random":
                    return await ctx.send("your Bio already uses a random color for description text.")
                else:
                    await self.config.member(ctx.author).color.set("random")
                    return await ctx.send(f"your Bio will now use a random color for description text.")
            current_tuple = None
            if current_color != "random":
                current_tuple = to_rgb_tuple(current_color)
            if value.lower() == "black":
                new_color = "#000000"
            elif value.lower() == "white":
                new_color = "#ffffff"
            else:
                result = validate_color(value)
                if result.is_valid is True:
                    new_color = value
                else:
                    return await ctx.send(f"the color provided appears to be invalid for the following reason: {result.reason}.")
            new_tuple = to_rgb_tuple(new_color)
            if new_tuple == current_tuple:
                return await ctx.send("your Bio already uses that color for description text.")
            else:
                if new_tuple == (0, 0, 0):
                    await ctx.send(f"your Bio will now use black text for your description.")
                    return await self.config.member(member).color.clear()
                elif new_tuple == (255, 255, 255):
                    await ctx.send("your Bio will now use white text for your description.")
                else:
                    await ctx.send(f"your Bio will now use color `{value}` for description text.")
                await self.config.member(ctx.author).color.set(new_color)
        else:
            await ctx.send("that field is not available.")
            
    @commands.command()
    @commands.guild_only()
    async def biodel(self, ctx, field: str):
        """Remove a field's value."""
        member = ctx.author
        field = field.lower()
        if field == "description":
            await self.config.member(member).description.clear()
        elif field in ["color", "colour"]:
            await self.config.member(member).color.clear()
        elif field == "image":
            image = await self.config.member(member).image()
            if image is not None:
                os.remove(cog_data_path(self) / "backgrounds" / image)
            await self.config.member(member).image.clear()
        elif field in Bio.allowed_socials:
            socials = await self.config.member(member).socials()
            socials.pop(field, None)
            await self.config.member(member).socials.set(socials)
        else:
            return await ctx.send("you haven't specified a valid field to remove.")
        return await ctx.message.add_reaction("✅")
        
    @commands.command()
    @commands.is_owner()
    async def biosize(self, ctx, size: str=None):
        """Configures the maximum allowable file size for images."""
        if size is None:
            await self.config.max_file_size.clear()
            await ctx.send("the max allowed size for images has been reset to `10 MiB`.")
        else:
            try:
                int_size = int(size)
            except ValueError:
                try:
                    int_size = word2num(size)
                except ValueError:
                    return await ctx.send("The requested value doesn't appear to be a number.")
            if int_size > 0:
                await self.config.max_file_size.set(int_size)
                await ctx.send(f"the max allowed size for images is now `{int_size} MiB`.")
            else:
                await ctx.send("it appears that you've specified a negative value or zero as the max possible size.")
                
    @commands.command()
    async def biofields(self, ctx):
        """Lists the available Bio fields."""
        fields = ["carrd", "lastfm", "linktree", "instagram", "Tumblr", "cashapp", "description", "image", "color"]
        fields_str = ""
        for field in fields:
            fields_str += "- " + field + "\n"
        max_file_size = await self.config.max_file_size()
        embed = discord.Embed(title="Bio Fields Available", description=fields_str, color=await ctx.embed_color())
        embed.set_footer(text=f"the maximum image size is currently {max_file_size}MiB.")
        await ctx.send(embed=embed)