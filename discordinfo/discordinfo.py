import discord

from reactionmenu import ViewMenu, ViewButton
from redbot.core import commands

class DiscordInfo(commands.Cog):
    """Get info on users, servers, and other things on Discord."""

    def __init__(self, bot):
        self.bot = bot

    async def build_embed(self, g, ctx, member: discord.Member=None):
        embed = discord.Embed(title=g.name, color=await ctx.embed_color()) if g.details is None else discord.Embed(title=g.name, description=f"{g.state}\n{g.details}", color=await ctx.embed_color())
        embed.set_thumbnail(url=g.small_image_url if g.large_image_url is None else g.large_image_url)
        thing = ctx.author.default_avatar if ctx.author.avatar is None else ctx.author.display_avatar if ctx.author.display_avatar.is_animated() is True else str(ctx.author.display_avatar.replace(size=2048, static_format="webp")) + "&quality=lossless"
        if member.nick:
            embed.set_author(name=f"{member.nick}'s Activities", icon_url=thing)
        else:
            embed.set_author(name=f"{member.name}'s Activities", icon_url=thing)
        return embed

    @commands.command()
    async def avatar(self, ctx, user: discord.User=None):
        """Get a user's avatar."""
        if user is None:
            user = ctx.author
        if ctx.guild:
            guild = self.bot.get_guild(ctx.guild.id)
            try:
                member = guild.get_member(user.id)
            except AttributeError:
                member = None
        else:
            member = None
        color = await ctx.embed_color() if not member else member.color
        embed = discord.Embed(title=f"{user.name}'s avatar", color=color)
        if user.avatar is None:
            url = user.default_avatar
        else:
            if user.avatar.is_animated():
                url = user.avatar.replace(size=2048)
            else:
                url = str(user.avatar.replace(size=2048, format="webp")) + "&quality=lossless"
                png = user.avatar.replace(size=2048, format="png")
                jpg = user.avatar.replace(size=2048, format="jpeg")
                embed.add_field(name="also available as", value=f"[png]({png}), [jpeg]({jpg})")
        if ctx.author.avatar is None:
            thing = ctx.author.default_avatar
        else:
            thing = str(ctx.author.avatar.replace(size=2048, static_format="webp"))
            if ctx.author.avatar.is_animated() is False:
                thing += "&quality=lossless"
        embed.set_image(url=url)
        embed.set_footer(text = f"executed by {ctx.author} for {user}", icon_url=thing)
        if user == ctx.author:
            embed.set_footer(text = f"executed by {ctx.author}", icon_url=thing)
        if member:
            if member.guild_avatar:
                menu = ViewMenu(ctx, menu_type=ViewMenu.TypeEmbed, show_page_director=False, all_can_click=False)
                main = ViewButton(style=discord.ButtonStyle.primary, label = "cycle avatar displayed", custom_id=ViewButton.ID_NEXT_PAGE)
                menu.add_button(main)
                embed2 = discord.Embed(title=f"{member.name}'s server avatar", color=color)
                if member.guild_avatar.is_animated():
                    url = member.guild_avatar.replace(size=2048)
                else:
                    url = str(member.guild_avatar.replace(size=2048, format="webp")) + "&quality=lossless"
                    png = member.guild_avatar.replace(size=2048, format="png")
                    jpg = member.guild_avatar.replace(size=2048, format="jpeg")
                    embed2.add_field(name="also available as", value=f"[png]({png}), [jpeg]({jpg})")
                if ctx.author.guild_avatar:
                    thing = str(ctx.author.guild_avatar.replace(size=2048, static_format="webp"))
                    if ctx.author.guild_avatar.is_animated() is False:
                        thing += "&quality=lossless"
                embed2.set_image(url=url)
                embed2.set_footer(text = f"executed by {ctx.author} for {member}", icon_url=thing)
                if user == ctx.author:
                    embed2.set_footer(text = f"executed by {ctx.author}", icon_url=thing)
                menu.add_page(embed)
                menu.add_page(embed2)
                await menu.start(send_to = ctx.channel)
            else:
                await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.command()
    async def banner(self, ctx, user: discord.User=None):
        """Get a user's banner."""
        if user is None:
            user = ctx.author
        user = await self.bot.fetch_user(user.id)
        if user.banner is None:
            if user is ctx.author:
                await ctx.send("you haven't set a custom banner image!")
            elif user.id == ctx.me.id:
                await ctx.send("i don't have a custom banner image!") 
            else:
                await ctx.send("this user hasn't set a custom banner image!")
            return
        else:
            if ctx.guild:
                guild = self.bot.get_guild(ctx.guild.id)
                try:
                    member = guild.get_member(user.id)
                except AttributeError:
                    member = None
            else:
                member = None
            color = await ctx.embed_color() if not member else member.color
            embed = discord.Embed(title=f"{user.name}'s banner", color=color)
            if user.banner.is_animated():
                url = user.banner.replace(size=2048)
            else:
                url = str(user.banner.replace(size=2048, format="webp")) + "&quality=lossless"
                png = user.banner.replace(size=2048, format="png")
                jpg = user.banner.replace(size=2048, format="jpeg")
                embed.add_field(name="also available as", value=f"[png]({png}), [jpeg]({jpg})")
            embed.set_image(url=url)
            if ctx.author.avatar is None:
                thing = ctx.author.default_avatar
            else:
                thing = str(ctx.author.display_avatar.replace(size=2048, static_format="webp"))
                if ctx.author.display_avatar.is_animated() is False:
                    thing += "&quality=lossless"
            embed.set_footer(text = f"executed by {ctx.author} for {user}", icon_url=thing)
            if user == ctx.author:
                embed.set_footer(text = f"executed by {ctx.author}", icon_url=thing)
            await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def serverinfo(self, ctx):
        """Get info on the current server."""
        embed = discord.Embed(title=ctx.guild.name, description=ctx.guild.description, color=await ctx.embed_color())
        bit = int(ctx.guild.bitrate_limit//1000)
        embed.add_field(name="perks", value=f"file limit: `{ctx.guild.filesize_limit//1048576}MB`\nemoji limit: `{ctx.guild.emoji_limit}`\nbitrate limit: `{bit}kbps`")
        heathen = int(ctx.guild.created_at.timestamp())
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
        sex = "bot"
        if human > 1:
            gay += "s"
        if bot_count > 1:
            sex += "s"
        embed.add_field(name="membership", value=f"{count} members \n{human} {gay} / {bot_count} {sex} ({percent}%)\n:crown: <@{ctx.guild.owner_id}>")
        embed.add_field(name="created on", value=f"<t:{heathen}:D> (<t:{heathen}:R>)", inline=False)
        embed.set_thumbnail(url=None if ctx.guild.icon is None else ctx.guild.icon if ctx.guild.icon.is_animated() else str(ctx.guild.icon.replace(size=1024, format="webp")) + "&quality=lossless")
        embed.set_footer(text=f"ID: {ctx.guild.id}")
        if ctx.guild.splash:
            if ctx.guild.banner is None:
                embed.add_field(name="\u200b", value="**invite splash**")
                embed.set_image(url=ctx.guild.splash)
                await ctx.send(embed=embed)
            else:
                menu = ViewMenu(ctx, menu_type=ViewMenu.TypeEmbed, show_page_director=False, all_can_click=False)
                embed.add_field(name="\u200b", value="**banner**")
                embed.set_image(url=ctx.guild.banner)
                embed2 = discord.Embed(title="invite splash", color=await ctx.embed_color())
                embed2.set_image(url=ctx.guild.splash)
                main = ViewButton(style=discord.ButtonStyle.primary, emoji="🖼️", label = "banner/info", custom_id=ViewButton.ID_GO_TO_FIRST_PAGE)
                menu.add_button(main)
                splash = ViewButton(style=discord.ButtonStyle.secondary, emoji="🌊", label = "invite splash", custom_id=ViewButton.ID_GO_TO_LAST_PAGE)
                menu.add_button(splash)
                menu.add_page(embed)
                menu.add_page(embed2)
                await menu.start(send_to = ctx.channel)
        elif ctx.guild.banner:
            if ctx.guild.splash is None:
                embed.add_field(name="\u200b", value="**banner**")
                embed.set_image(url=ctx.guild.banner)
                await ctx.send(embed=embed)
        else:
            if ctx.guild.icon != None:
                if ctx.guild.icon.is_animated() is False:
                    png = ctx.guild.icon.replace(size=1024, format="png")
                    jpg = ctx.guild.icon.replace(size=1024, format="jpeg")
                    embed.add_field(name="icon also available as", value=f"[png]({png}), [jpeg]({jpg})")
            await ctx.send(embed=embed)

    @commands.command()
    async def whois(self, ctx, user: discord.User):
        """Get info on a user."""
        if ctx.guild:
            guild = self.bot.get_guild(ctx.guild.id)
            try:
                member = guild.get_member(user.id)
            except:
                member = None
        else:
            member = None
        color = await ctx.embed_color() if not member else member.color
        embed = discord.Embed(title=user, color=color)
        if user.avatar is None:
            thing = user.default_avatar
        else:
            thing = str(user.avatar.replace(size=2048, static_format="webp"))
            if user.avatar.is_animated() is False:
                thing += "&quality=lossless"
        embed.set_thumbnail(url=thing)
        heathen = int(user.created_at.timestamp())
        embed.add_field(name="account created:", value=f"<t:{heathen}:D> (<t:{heathen}:R>)")
        value="❌" if user.system is False else "✅"
        embed.add_field(name="represents discord officially?", value=value, inline=False)
        value="❌" if user.public_flags.spammer is False else "✅"
        embed.add_field(name="known spammer?", value=value, inline=False)
        embed.set_footer(text=f"ID: {user.id}")
        if member:
            if member.guild_avatar:
                embed.add_field(name="note", value="global avatar currently displayed", inline=False)
                menu = ViewMenu(ctx, menu_type=ViewMenu.TypeEmbed, show_page_director=False)
                main = ViewButton(style=discord.ButtonStyle.primary, label = "cycle avatar displayed", custom_id=ViewButton.ID_NEXT_PAGE)
                menu.add_button(main)
                menu.add_page(embed)
                embed2 = discord.Embed(title=user, color=await ctx.embed_color())
                embed2.add_field(name="account created:", value=f"<t:{heathen}:D> (<t:{heathen}:R>)")
                embed2.add_field(name="represents discord officially?", value=value, inline=False)
                embed2.add_field(name="known spammer?", value=value, inline=False)
                embed2.add_field(name="note", value="server avatar currently displayed", inline=False)
                embed2.set_footer(text=f"ID: {user.id}")
                thing = str(member.guild_avatar.replace(size=2048, static_format="webp"))
                if member.guild_avatar.is_animated() is False:
                    thing += "&quality=lossless"
                embed2.set_thumbnail(url=thing)
                menu.add_page(embed2)
                await menu.start(send_to = ctx.channel)
            else:
                await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.guild_only()      
    @commands.command()
    async def cstatus(self, ctx, member: discord.Member=None):
        """Get a user's custom status."""
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
        """Get the activities a user is doing."""
        if member is None:
            member = ctx.author
        act = [i for i in member.activities if isinstance(i, discord.Activity)]
        if act:
            if len(act) >= 2:
                menu = ViewMenu(ctx, style='activity $/&', menu_type=ViewMenu.TypeEmbed)
                back_button = ViewButton(style=discord.ButtonStyle.primary, emoji='◀️', label='Back', custom_id=ViewButton.ID_PREVIOUS_PAGE)
                menu.add_button(back_button)
                next_button = ViewButton(style=discord.ButtonStyle.secondary, emoji='▶️', label='Next', custom_id=ViewButton.ID_NEXT_PAGE)
                menu.add_button(next_button)
                if len(act) >= 3:
                    gtpb = ViewButton(style=discord.ButtonStyle.primary, emoji='🔢', label='Menu' ,custom_id=ViewButton.ID_GO_TO_PAGE)
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
                embed = await self.build_embed(g, ctx, member)
                await ctx.send(embed=embed)
        else:
            if member is ctx.author:
                await ctx.send("you aren't doing anything (check your profile to make sure it's public!)")
            elif member is ctx.me:
                await ctx.send("i'm not doing anything! (i lack arms)")
            else:
                await ctx.send("this member isn't doing anything (check the profile to make sure it's public!)")