import asyncio
import discord

from discord.ext import tasks
if discord.__version__[0] == "2":
    from reactionmenu import ViewMenu, ViewButton
else:
    from reactionmenu import ReactionMenu, Button, ButtonType
from redbot.core import Config, checks, commands

class Vcstats(commands.Cog):
    """Tracks various stats in a voice channel."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=8086, force_registration=True)
        self.config.register_global(guilds=[])
        self.config.register_guild(vcstats=[])
        self.setting.start()
        
    async def name_gen(self, guild, stat_val):
        # 1 = members
        # 2 = boosters
        # 3 = roles
        # 4 = text channels
        # 5 = voice channels
        # 6 = guild owner
        # 7 = banned users
        # 8 = emojis
        # 9 = guildid
        # 10 = guildname
        # 11 = # of servers bot is in
        # 12 = # of bots
        #(might restart at 0 to make things simpler)
        if stat_val == 0:
            new_name = f"Members: {guild.member_count}"
        if stat_val == 1:
            new_name = f"Boosters: {len(guild.premium_subscribers)}"
        if stat_val == 2:
            new_name = f"Roles: {(len(guild.roles) - 1)}"
        if stat_val == 3:
            new_name = f"Text Channels: {len(guild.text_channels)}"
        if stat_val == 4:
            new_name = f"Voice Channels: {len(guild.voice_channels)}"
        if stat_val == 5:
            new_name = f"Owner: {guild.owner.name}"
            if guild.owner.name != guild.owner.display_name:
                new_name += f" ({guild.owner.display_name})"
        if stat_val == 6:
            bans = [entry async for entry in guild.bans()]
            new_name = f"Banned Users: {len(bans)}"
        if stat_val == 7:
            new_name = f"Emojis: {len(guild.emojis)}"
        if stat_val == 8:
            new_name = f"Guild ID: {guild.id}"
        if stat_val == 9:
            new_name = f"Guild Name: {guild.name}"
        if stat_val == 10:
            new_name = f"Bot Servers: {len(self.bot.guilds)}"
        if stat_val == 11:
            members = 0
            for server in self.bot.guilds:
                members += len(server.members)
            new_name = f"Bot Users: {members}"
        return new_name

    async def menu_gen(self, ctx, test_list, numero):
        start = 0
        end = 40
        channels_list = []
        if discord.__version__[0] == "2":
            menu = ViewMenu(ctx, style='page $/&', menu_type=ViewMenu.TypeEmbed)
            back_button = ViewButton(style=discord.ButtonStyle.primary, emoji='◀️', label='Back', custom_id=ViewButton.ID_PREVIOUS_PAGE)
            menu.add_button(back_button)
            next_button = ViewButton(style=discord.ButtonStyle.secondary, emoji='▶️', label='Next', custom_id=ViewButton.ID_NEXT_PAGE)
            menu.add_button(next_button)
        else:
            menu = ReactionMenu(ctx, back_button='◀️', next_button='▶️', style='page $/&', config=ReactionMenu.STATIC)
        if len(test_list) > 80:
            if discord.__version__[0] == "2":
                gtpb = ViewButton(style=discord.ButtonStyle.primary, emoji='🔢', label='Menu' ,custom_id=ViewButton.ID_GO_TO_PAGE)
            else:
                gtpb = Button(emoji='🔢', linked_to=ButtonType.GO_TO_PAGE)
            menu.add_button(gtpb)
        while start <= len(test_list):
            splits = test_list[start:end]
            channels_list.append(splits)
            start += 40
            end += 40
        for fragment in channels_list:
            voice_channels = ""
            for voice_channel in fragment:
                voice_channels += f"{numero}. {voice_channel.id}\n"
                numero += 1
            embed = discord.Embed(color=await ctx.embed_color())
            embed.add_field(name="voice channels", value=voice_channels)
            menu.add_page(embed, content="please respond with the number of the voice channel you would like to select for VCStats")
        return menu, numero

    @checks.admin()
    @commands.guild_only()
    @commands.group()
    async def vcstats(self, ctx):
        """Tracks a stat in a voice channel."""

    @vcstats.command()
    async def add(self, ctx, stat, channel: discord.VoiceChannel = None):
        """Adds a stat to be tracked."""
        if channel is None:
            vc_ids = []
            numero = 1
            if len(ctx.guild.voice_channels) <= 40:
                voice_channels = ""
                for vc in ctx.guild.voice_channels:
                    numero_str = str(numero)
                    voice_channels += f"{numero_str}. <#{vc.id}>\n"
                    vc_ids.append(vc.id)
                    numero += 1
                embed = discord.Embed(color=await ctx.embed_color())
                embed.add_field(name="voice channels", value=voice_channels)
                await ctx.send("please respond with the number of the voice channel you would like to select for VCStats", embed=embed)
            else:
                test_list = ctx.guild.voice_channels
                menu = await self.menu_gen(ctx, test_list, numero)
                await menu.start(send_to = ctx.channel)
        def check(m):
            return m.content.isdigit() is True and m.channel == ctx.channel and ctx.author == m.author
        try:
            msg = await self.bot.wait_for('message', check=check, timeout = 60.0)
        except asyncio.TimeoutError:
            return await ctx.send("timeout reached; please try again")
        msg = int(msg.content)
        if msg in range(1, numero + 1):
            channel = self.bot.get_channel(vc_ids[msg - 1])
        else:
            return await ctx.send("an invalid input was sent; please try again")
        stat = stat.lower()
        stats = ["members", "boosters", "roles", "textchannels", "voicechannels", "guildowner", "bannedusers", "emojis", "guildid", "guildname", "botservers", "botusers"]
        if stat in stats:
            stat_val = stats.index(stat.lower())
            guilds = await self.config.guilds()
            if ctx.guild.id not in guilds:
                guilds.append(ctx.guild.id)
            the_list = await self.config.guild(ctx.guild).vcstats()
            if [channel.id, stat_val] in the_list:
                return await ctx.send("that stat is already being tracked in that channel")
            else:
                for block in the_list:
                    if block[0] == channel.id:
                        await ctx.send(f"another stat is being tracked in that channel; are you sure you want to replace it with `{stat}`? (yes/no)")
                        def check(m):
                            return m.content != "" and m.channel == ctx.channel and ctx.author == m.author
                        try:
                            msg = await self.bot.wait_for('message', check=check, timeout = 60.0)
                        except asyncio.TimeoutError:
                            return await ctx.send("timeout reached; please try again")
                        if msg.content.lower() == "yes":
                            the_list.remove(block)
                        else:
                            return await ctx.send(f"`{stat}` will not be tracked in <#{channel.id}>")
            the_list.append([channel.id, stat_val])
            guild = ctx.guild
            new_name = await self.name_gen(guild, stat_val)
            if new_name != channel.name:
                try:
                    await channel.edit(name=new_name)
                except discord.Forbidden:
                    return await ctx.send("i was unable to edit this channel's name; please ensure that i have the `View Channel`, `Manage Channel`, and `Connect` permissions")
            await self.config.guilds.set(guilds)
            await self.config.guild(ctx.guild).vcstats.set(the_list)
            await ctx.message.add_reaction("✅")
        else:
            await ctx.send(f"invalid stat was requested; please use a stat listed by `{ctx.prefix}vcstats stats`")
            
    @vcstats.command()
    async def remove(self, ctx, stat, channel: discord.VoiceChannel = None):
        """Removes a stat to be tracked"""
        the_list = await self.config.guild(ctx.guild).vcstats()
        stats = ["members", "boosters", "roles", "textchannels", "voicechannels", "guildowner", "bannedusers", "emojis", "guildid", "guildname", "botservers", "botusers"]
        stat = stat.lower()
        if stat in stats:
            stat_val = stats.index(stat.lower())
        else:
            return await ctx.send(f"invalid stat was requested; please use a stat listed by `{ctx.prefix}vcstats stats`")
        if channel is None:
            vc_ids = []
            tracked_channels = []
            for vc in ctx.guild.voice_channels:
                vc_ids.append(vc.id)
            for block in the_list:
                if block[0] in vc_ids and stat_val == block[1]:
                    tracked = self.bot.get_channel(block[0])
                    tracked_channels.append(tracked)
            if len(tracked_channels) == 0:
                return await ctx.send("that stat is not currently being tracked in any channel in this server")
            elif len(tracked_channels) == 1:
                channel = tracked_channels[0]
            else:
                numero = 1
                if len(tracked_channels) > 1 and len(tracked_channels) <= 40:
                    voice_channels = ""
                    for vc in tracked_channels:
                        numero_str = str(numero)
                        voice_channels += f"{numero_str}. <#{vc.id}>\n"
                        numero += 1
                    embed = discord.Embed(color=await ctx.embed_color())
                    embed.add_field(name="voice channels", value=voice_channels)
                    await ctx.send("please respond with the number of the voice channel you would like to select for VCStats", embed=embed)
                if len(tracked_channels) > 40:
                    menu, numero = await self.menu_gen(ctx, tracked_channels, numero)
                    await menu.start(send_to = ctx.channel)
                def check(m):
                    return m.content.isdigit() is True and m.channel == ctx.channel and ctx.author == m.author
                try:
                    msg = await self.bot.wait_for('message', check=check, timeout = 60.0)
                except asyncio.TimeoutError:
                    return await ctx.send("timeout reached; please try again")
                msg = int(msg.content)
                if msg in range(1, numero + 1):
                    channel = tracked_channels[msg - 1]
                else:
                    return await ctx.send("an invalid input was sent; please try again")
        if [channel.id, stat_val] in the_list:
            the_list.remove([channel.id, stat_val])
            await self.config.guild(ctx.guild).vcstats.set(the_list)
            await ctx.send(f"stat `{stat}` is no longer being tracked in <#{channel.id}>")
        
    @vcstats.command()
    async def stats(self, ctx):
        """Lists the stats which can be tracked."""
        the_dollar = ""
        stats = ["members", "boosters", "roles", "textchannels", "voicechannels", "guildowner", "bannedusers", "emojis", "guildid", "guildname", "botservers", "botusers"]
        for stat in stats:
            the_dollar += f"- {stat}\n"
        embed = discord.Embed(color=await ctx.embed_color())
        embed.add_field(name="valid options:", value=the_dollar)
        await ctx.send(embed=embed)


    @tasks.loop(minutes=9.0)
    async def setting(self):
        await asyncio.sleep(60) # things WILL break if this isn't here
        guilds = await self.config.guilds()
        for guild_id in guilds:
            guild = self.bot.get_guild(guild_id)
            the_list = await self.config.guild(guild).vcstats()
            for channels in the_list:
                channel = self.bot.get_channel(channels[0])
                stat_val = channels[1]
                new_name = await self.name_gen(guild, stat_val)
                if channel.name != new_name:
                    await channel.edit(name=new_name)