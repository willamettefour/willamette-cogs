import discord
import requests
import time

from reactionmenu import ReactionMenu, Button, ButtonType
from redbot.core import commands

class DiscordInfo(commands.Cog):
    """Get info on users, servers, and other things on Discord."""

    def __init__(self, bot):
        self.bot = bot

    async def thing(self, ctx):
        thing = str(ctx.author.avatar_url)
        if requests.get(thing).headers['content-type'] == "image/webp":
            thing += "&quality=lossless"
        if ctx.author.is_avatar_animated():
            thing = ctx.author.avatar_url_as(format="gif", size=2048)
        thing_req = await self.bot.http.request(discord.http.Route("GET", "/guilds/{gid}/members/{uid}", gid=ctx.guild.id, uid=ctx.author.id))
        thing_av = thing_req["avatar"]
        if thing_av:
            maid_url = f"https://cdn.discordapp.com/guilds/{ctx.guild.id}/users/{ctx.author.id}/avatars/{thing_av}"
            thing = maid_url + ".webp?size=2048&quality=lossless"
            if requests.get(maid_url).headers['content-type'] == "image/gif":
                thing = maid_url + ".gif?size=2048"
        return thing

    async def build_embed(self, g, ctx, member: discord.Member=None):
        if g.details is None:
            embed = discord.Embed(title=g.name, color=await ctx.embed_color())
        else:
            embed = discord.Embed(title=g.name, description=f"{g.state}\n{g.details}", color=await ctx.embed_color())
        if g.large_image_url is None:
            if g.small_image_url is None:
                embed.set_thumbnail(url="https://i.redd.it/notarealimage.jpg")
            else:
                embed.set_thumbnail(url=g.small_image_url)
        else:
            embed.set_thumbnail(url=g.large_image_url)
        thing = await self.thing(ctx)
        if member.nick:
            embed.set_author(name=f"{member.nick}'s Activities", icon_url=thing)
        else:
            embed.set_author(name=f"{member.name}'s Activities", icon_url=thing)
        if g.small_image_url is None:
            pass
        else:
            embed.set_footer(text="", icon_url=g.small_image_url)
        return embed

    @commands.command()
    async def avatar(self, ctx, user: discord.User=None):
        """Get a user's avatar using their ID.
        A username with/without a discriminator can be used for a member of this server."""
        # Your code will go here
        if user is None:
            user = ctx.author
        if ctx.guild:
            guild = self.bot.get_guild(ctx.guild.id)
            try:
                member = guild.get_member(user.id)
                color = member.color
            except AttributeError:
                member = None
                color = await ctx.embed_color()
        else:
            member = None
            color = await ctx.embed_color()
        embed = discord.Embed(title=f"{user.name}'s avatar", color=color)
        url = str(user.avatar_url)
        if user.is_avatar_animated() or requests.get(url).headers['content-type'] == "image/png":
            if user.is_avatar_animated():
                url = user.avatar_url_as(format="gif", size=2048)
            if requests.get(url).headers['content-type'] == "image/png":
                pass
        else:
            url += "&quality=lossless"
            png = user.avatar_url_as(static_format="png")
            jpg = user.avatar_url_as(static_format="jpeg")
            embed.add_field(name="also available as", value=f"[png]({png}), [jpeg]({jpg})")
        thing = str(ctx.author.avatar_url)
        if requests.get(thing).headers['content-type'] == "image/webp":
            thing += "&quality=lossless"
        if ctx.author.is_avatar_animated():
            thing = ctx.author.avatar_url_as(format="gif", size=2048)
        embed.set_image(url=url)
        embed.set_footer(text = f"executed by {ctx.author} for {user}", icon_url=thing)
        if user == ctx.author:
            embed.set_footer(text = f"executed by {ctx.author}", icon_url=thing)
        if member is None:
            await ctx.send(embed=embed)
        else:
            req = await self.bot.http.request(discord.http.Route("GET", "/guilds/{gid}/members/{uid}", gid=ctx.guild.id, uid=user.id))
            thing_req = await self.bot.http.request(discord.http.Route("GET", "/guilds/{gid}/members/{uid}", gid=ctx.guild.id, uid=ctx.author.id))
            maid = req["avatar"]
            thing_av = thing_req["avatar"]
            if maid:
                menu = ReactionMenu(ctx, back_button='◀️', next_button='▶️', show_page_director=False, config=ReactionMenu.STATIC)
                embed2 = discord.Embed(title=f"{member.name}'s server avatar", color=color)
                maid_url = f"https://cdn.discordapp.com/guilds/{ctx.guild.id}/users/{member.id}/avatars/{maid}"
                final_url = maid_url + ".webp?size=2048&quality=lossless"
                if requests.get(maid_url).headers['content-type'] == "image/gif":
                    final_url = banner_url + ".gif?size=2048"
                if requests.get(maid_url).headers['content-type'] == "image/png":
                    png = maid_url + ".png?size=2048"
                    jpg = maid_url + ".jpg?size=2048"
                    embed2.add_field(name="also available as", value=f"[png]({png}), [jpeg]({jpg})")
                    if thing_av:
                        user_maid_url = f"https://cdn.discordapp.com/guilds/{ctx.guild.id}/users/{ctx.author.id}/avatars/{thing_av}"
                        thing = user_maid_url + ".webp?size=2048&quality=lossless"
                        if requests.get(maid_url).headers['content-type'] == "image/gif":
                            thing = user_maid_url + ".gif?size=2048"
                    embed2.set_image(url=final_url)
                    embed2.set_footer(text = f"executed by {ctx.author} for {member}", icon_url=thing)
                    if user == ctx.author:
                        embed2.set_footer(text = f"executed by {ctx.author}", icon_url=thing)
                    menu.add_page(embed)
                    menu.add_page(embed2)
                    await menu.start(send_to = ctx.channel)
            else:
                if thing_av:
                    user_maid_url = f"https://cdn.discordapp.com/guilds/{ctx.guild.id}/users/{ctx.author.id}/avatars/{thing_av}"
                    thing = user_maid_url + ".webp?size=2048&quality=lossless"
                    if requests.get(user_maid_url).headers['content-type'] == "image/gif":
                        thing = user_maid_url + ".gif?size=2048"
                    embed.set_footer(text = f"executed by {ctx.author} for {user}", icon_url=thing)
                    if user == ctx.author:
                        embed.set_footer(text = f"executed by {ctx.author}", icon_url=thing)
                await ctx.send(embed=embed)

    @commands.command()
    async def banner(self, ctx, user: discord.User=None):
        """Get a user's banner using their ID.
        A username with/without a discriminator can be used for a member of this server.
        NOTE: This doesn't support server-only banners"""
        # Your code will go here
        if user is None:
            user = ctx.author
        req = await self.bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=user.id))
        banner_id = req["banner"]
        # If statement because the user may not have a banner
        if banner_id:
            banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}"
        else:
            if user is ctx.author:
                await ctx.send("you haven't set a custom banner image!")
            elif user.id == 793623351339384872:
                await ctx.send("i don't have a custom banner image!") 
            else:
                await ctx.send("this user hasn't set a custom banner image!")
            return
        if requests.get(banner_url).headers['content-type'] == "image/png":
            final_url = banner_url + ".webp?size=2048&quality=lossless"
        else:
            final_url = banner_url + ".gif?size=2048"
        if ctx.guild:
            guild = self.bot.get_guild(ctx.guild.id)
            try:
                member = guild.get_member(user.id)
                color = member.color
            except AttributeError:
                member = None
                color = await ctx.embed_color()
        else:
            member = None
            color = await ctx.embed_color()
        embed = discord.Embed(title=f"{user.name}'s banner", color=color)   
        if requests.get(banner_url).headers['content-type'] == "image/png":
            png = banner_url + ".png?size=2048"
            jpg = banner_url + ".jpg?size=2048"
            embed.add_field(name="also available as", value=f"[png]({png}), [jpeg]({jpg})")
        thing = await self.thing(ctx)
        embed.set_image(url=final_url)
        embed.set_footer(text = f"executed by {ctx.author} for {user}", icon_url=thing)
        if user == ctx.author:
            embed.set_footer(text = f"executed by {ctx.author}", icon_url=thing)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def serverinfo(self, ctx):
        """Gets info on this server."""
        # Your code will go here
        embed = discord.Embed(title=ctx.guild.name, color=await ctx.embed_color())
        if ctx.guild.description:
            embed = discord.Embed(title=ctx.guild.name, description=ctx.guild.description, color=await ctx.embed_color())
        bit = int(ctx.guild.bitrate_limit//1000)
        embed.add_field(name="perks", value=f"file limit: `{ctx.guild.filesize_limit//1048576}MB`\nemoji limit: `{ctx.guild.emoji_limit}`\nbitrate limit: `{bit}kbps`")
        heathen = int(time.mktime(ctx.guild.created_at.timetuple()))
        count = ctx.guild.member_count
        members = ctx.guild.members
        bot_count = 0
        for i in members:
            member = i.bot
            if member == True:
                bot_count += 1
        human = count - bot_count
        percent = int((bot_count/count)*100)
        gay = "human"
        if human > 1:
            gay += "s"
        sex = "bot"
        if bot_count > 1:
            sex += "s"
        embed.add_field(name="membership", value=f"{count} members \n{human} {gay} / {bot_count} {sex} ({percent}%)\n:crown: <@{ctx.guild.owner_id}>")
        embed.add_field(name="created on", value=f"<t:{heathen}:D> (<t:{heathen}:R>)", inline=False)
        if ctx.guild.icon_url:
            embed.set_thumbnail(url=str(ctx.guild.icon_url) + "&quality=lossless")
        if ctx.guild.is_icon_animated():
            embed.set_thumbnail(url=ctx.guild.icon_url_as(format="gif"))
        embed.set_footer(text=f"dates are in UTC time \nID: {ctx.guild.id}")
        if ctx.guild.splash:
            if ctx.guild.banner is None:
                embed.add_field(name="\u200b", value="**invite splash**")
                embed.set_image(url=ctx.guild.splash_url)
                await ctx.send(embed=embed)
            else:
                menu = ReactionMenu(ctx, back_button='◀️', next_button='▶️', show_page_director=False, config=ReactionMenu.STATIC)
                embed.add_field(name="\u200b", value="**banner**")
                embed.set_image(url=ctx.guild.banner_url)
                embed2 = discord.Embed(title="invite splash", color=await ctx.embed_color())
                embed2.set_image(url=ctx.guild.splash_url)
                menu.add_page(embed)
                menu.add_page(embed2)
                await menu.start(send_to = ctx.channel)
        elif ctx.guild.banner:
            if ctx.guild.splash is None:
                embed.add_field(name="\u200b", value="**banner**")
                embed.set_image(url=ctx.guild.banner_url)
                await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.command()
    async def whois(self, ctx, user: discord.User):
        """Get info on a Discord user using their ID.
        A username with/without a discriminator can be used for a member of this server."""
        embed = discord.Embed(title=user, color=await ctx.embed_color())
        thing = str(user.avatar_url)
        if requests.get(thing).headers['content-type'] == "image/webp":
            thing += "&quality=lossless"
        if user.is_avatar_animated():
            thing = user.avatar_url_as(format="gif", size=2048)
        embed.set_thumbnail(url=thing)
        heathen = int(time.mktime(user.created_at.timetuple()))
        embed.add_field(name="account created:", value=f"<t:{heathen}:D> (<t:{heathen}:R>)")
        if user.public_flags.staff is False:
            value="❌"
        else:
            value="✅"
        embed.add_field(name="discord staff?", value=value, inline=False)
        embed.set_footer(text=f"dates are in UTC time \nID: {user.id}")
        if ctx.guild:
            try:
                thing_req = await self.bot.http.request(discord.http.Route("GET", "/guilds/{gid}/members/{uid}", gid=ctx.guild.id, uid=user.id))
                thing_av = thing_req["avatar"]
            except:
                thing_av = None
            if thing_av is not None:
                embed.add_field(name="note", value="use the arrows to cycle between their avatars\n(global avatar currently displayed)", inline=False)
                menu = ReactionMenu(ctx, back_button='◀️', next_button='▶️', show_page_director=False, config=ReactionMenu.STATIC)
                menu.add_page(embed)
                embed2 = discord.Embed(title=user, color=await ctx.embed_color())
                embed2.add_field(name="account created:", value=f"<t:{heathen}:D> (<t:{heathen}:R>)")
                embed2.add_field(name="discord staff?", value=value, inline=False)
                maid_url = f"https://cdn.discordapp.com/guilds/{ctx.guild.id}/users/{user.id}/avatars/{thing_av}"
                thing = maid_url + ".webp?size=2048&quality=lossless"
                if requests.get(maid_url).headers['content-type'] == "image/gif":
                    thing = maid_url + ".gif?size=2048"
                embed2.set_thumbnail(url=thing)
                embed2.set_footer(text=f"dates are in UTC time \nID: {user.id}")
                embed2.add_field(name="note", value="use the arrows to cycle between their avatars \n(server avatar currently displayed)", inline=False)
                menu.add_page(embed2)
                await menu.start(send_to = ctx.channel)
            else:
                await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def cstatus(self, ctx, member: discord.Member=None):
        """Get a server member's custom status."""
        # Your code will go here
        if member is None:
            member = ctx.author
        stat = [h for h in member.activities if isinstance(h, discord.CustomActivity)]
        if stat:
            for s in member.activities:
                if isinstance(s, discord.CustomActivity):
                    embed = discord.Embed(title="", color=await ctx.embed_color())
                    if s.emoji and s.name:
                        if s.emoji.id:
                            embed.set_author(name=s.name, icon_url=s.emoji.url)
                        else:
                            embed.set_author(name=s)
                    elif s.emoji and s.name is None:
                        if s.emoji.id:
                            embed.set_author(name="\u200b", icon_url=s.emoji.url)
                        else:
                            embed.set_author(name=s)
                    else:
                        embed.set_author(name=s)
                    await ctx.send(embed=embed)
        else:
            if member is ctx.author:
                await ctx.send("you don't have a custom status!")
            elif member is ctx.me:
                await ctx.send("i don't have a custom status!")
            else:
                await ctx.send("this member hasn't set a custom status!")

    @commands.command()
    async def activity(self, ctx, member: discord.Member=None):
        """Get the activities a server member is doing."""
        # Your code will go here
        if member is None:
            member = ctx.author
        act = [i for i in member.activities if isinstance(i, discord.Activity)]
        if act:
            if len(act) >= 2:
                menu = ReactionMenu(ctx, back_button='◀️', next_button='▶️', style='Activity $/&', config=ReactionMenu.STATIC)
                if len(act) >= 3:
                    gtpb = Button(emoji='🔢', linked_to=ButtonType.GO_TO_PAGE)
                    menu.add_button(gtpb)
                num = 0
                while num < len(act):
                    g = act[num]
                    embed = await self.build_embed(g, ctx, member)
                    menu.add_page(embed)
                    num += 1
                await menu.start(send_to = ctx.channel)
            else:
                g = act[0]
                embed1 = await self.build_embed(g, ctx, member)
                await ctx.send(embed=embed1)
        else:
            if member is ctx.author:
                await ctx.send("you aren't doing anything (check your profile to make sure it's public!)")
            elif member is ctx.me:
                await ctx.send("i'm not doing anything! (i lack arms)")
            else:
                await ctx.send("this member isn't doing anything (check the profile to make sure it's public!)")

    @commands.command()
    async def emojiinfo(self, ctx, emoji: discord.Emoji):
        """Get info on a custom emoji."""
        # Your code will go here
        embed = discord.Embed(title=emoji.name, color=await ctx.embed_color())
        heathen = int(time.mktime(emoji.created_at.timetuple()))
        embed.add_field(name="emoji created:", value=f"<t:{heathen}:D> (<t:{heathen}:R>)")
        if emoji.animated:
            value="✅"
        else:
            value="❌"
        embed.add_field(name="animated?", value=value, inline=False)
        embed.set_thumbnail(url=str(emoji.url_as(format="webp")) + "?quality=lossless")
        if emoji.animated:
            embed.set_thumbnail(url=emoji.url)
        embed.set_footer(text=f"dates are in UTC time \nID: {emoji.id}")
        await ctx.send(embed=embed)