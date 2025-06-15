from datetime import datetime, timezone
from reactionmenu import ViewMenu, ViewButton 
from redbot.core import commands
from redbot.core.utils.chat_formatting import pagify
import discord
import lyricsgenius
import random

class Spotify(commands.Cog):
    """Spotify commands."""

    def __init__(self, bot):
        self.bot = bot
        global fuck_you
        fuck_you = [115238234778370049, 416268491197513738, 598277022787043370, 644027020023693312, 651975050114891779, 778802790843678740, 792842038332358656, 855292122017169420, 1191423677397475428]

    async def lyric_scraping(self, ctx, artist, song):
        rapgenius = await self.bot.get_shared_api_tokens("genius")
        if rapgenius.get("access_token") is None:
            if ctx.author is ctx.guild.owner:
                return await ctx.send(f"you haven't set a genius api key! get one at https://genius.com/api-clients, then use {ctx.prefix}set api genius access_token,<your access token>")
            else:
                return await ctx.send(f"the bot owner hasn't set a genius api key; contact them to get spotify lyrics")
        genius = lyricsgenius.Genius(rapgenius["access_token"])
        song = genius.search_song(song, artist[0])
        if song:
            try:
                for singer in artist:
                    if singer in song.artist:
                        lyrics = song.lyrics
                        for substring in ["Read More", "Lyrics"]:
                            if substring in lyrics:
                                lyrics = song.lyrics.split(substring, 1)[1]
                        
                    else:
                        lyrics = ""
            except AttributeError:
                lyrics = ""
        else:
            lyrics = ""
        return lyrics
    
    @commands.group()
    @commands.guild_only()
    async def spotify(self, ctx):
        """Spotify commands."""
        
    @spotify.command()
    async def playing(self, ctx, member: discord.Member=None):
        """
        Returns the song playing on a member's Spotify.
        User arguments - Mention/ID
        """   
        if member is None:
            member = ctx.author
        if member.id in fuck_you:
            return await ctx.send("no 💖")
        spot = next((activity for activity in member.activities if isinstance(activity, discord.Spotify)), None)
        if spot is None:
            await ctx.send(f"{member.name} is not listening to Spotify")
            return
        artist = spot.artist.replace(";", ",")
        variable = spot.end - datetime.now(timezone.utc)
        start = spot.duration - variable
        variable1 = start.seconds//60
        variable2 = spot.duration.seconds//60
        variable3 = start.seconds-variable1 * 60
        variable4 = spot.duration.seconds-variable2 * 60
        human_start = f"{variable1:02d}:{variable3:02d}"
        human_end = f"{variable2:02d}:{variable4:02d}"
        numero = 0
        bar = int((start.seconds/spot.duration.seconds)*10)
        the_bar = ""
        while numero in range(bar):
            the_bar += "▓"
            numero += 1
        while numero <= 9:
            the_bar += "░"
            numero += 1
        space = " "
        embed = discord.Embed(title=spot.title, description=f"{artist}\n`{human_start}`{space}{the_bar}{space}`{human_end}`", color=0x1db954, url=f"https://open.spotify.com/track/{spot.track_id}")
        if member.avatar is None:
            url = member.default_avatar
        else:
            url = str(member.display_avatar.replace(size=2048, static_format="webp"))
            if member.display_avatar.is_animated() is False:
                url += "&quality=lossless"
        embed.set_author(name=f"{member.name}'s Spotify", icon_url="https://cdn.discordapp.com/emojis/850498251663736872.webp?size=128&quality=lossless")
        embed.set_thumbnail(url=spot.album_cover_url)
        if ctx.author.avatar is None:
            thing = ctx.author.default_avatar
        else:
            thing = str(ctx.author.avatar.replace(size=2048, static_format="webp"))
            if ctx.author.avatar.is_animated() is False:
                thing += "&quality=lossless"
        embed.set_footer(text = f"executed by {ctx.author} for {member}", icon_url=thing)
        if member == ctx.author:
            embed.set_footer(text = f"executed by {ctx.author}", icon_url=thing)        
        await ctx.send(embed=embed)

    @spotify.command()
    async def lyrics(self, ctx, member: discord.Member=None):
        """Returns lyrics for a song being played by a member on Spotify"""
        if member is None:
            member = ctx.author
        if member.id in fuck_you:
            return await ctx.send("no 💖")
        spot = next((activity for activity in member.activities if isinstance(activity, discord.Spotify)), None)
        if spot is None:
            return await ctx.send(f"{member.name} is not listening to Spotify")
        async with ctx.typing():
            exceptions = {"Blur":" - 2012 Remaster", 
            "Blur (Special Edition)":" - 2012 Remaster", 
            "Definitely Maybe (Deluxe Edition Remastered)":" - Remastered", 
            "Definitely Maybe (30th Anniversary Deluxe Edition)":" - Remastered", 
            "(What's The Story) Morning Glory? (Deluxe Remastered Edition)":" - Remastered",
            "Be Here Now (Deluxe Remastered Edition)":" - Remastered",
            "Back the Way We Came: Vol. 1 (2011 - 2021)":" - Remastered",
            "Hopes And Fears 20":" - Remastered 2024",
            "Little Creatures (Deluxe Version)":" - 2005 Remaster",
            "The Best of Talking Heads":" - 2003 Remaster",
            "Un Día Normal (20th Anniversary Remastered)":" - Remastered 2022",
            "Whenever You Need Somebody (Deluxe Edition - 2022 Remaster)":" (2022 Remaster)"}
            artist_exceptions = {"Noel Gallagher's High Flying Birds":"Noel Gallagher", 
            "Liam Gallagher & John Squire":"Liam Gallagher"}
            try:
                title = spot.title.replace(exceptions[spot.album], "")
            except KeyError:
                title = spot.title
            artists = []
            for artist in spot.artists:
                try:
                    if artist_exceptions[artist]:
                        artists.append(artist_exceptions[artist])
                except KeyError:
                    artists.append(artist)
            lyrics = await self.lyric_scraping(ctx, artists, title)
        if lyrics == "":
            return await ctx.send("could not find the lyrics to this song.")
        else:
            paged_embeds = []
            paged_content = [p for p in pagify(lyrics, page_length=1024)]
            for index, page in enumerate(paged_content):
                embed = discord.Embed(color = await ctx.embed_color(), description=page, title=spot.title)
                embed.set_author(name="song lyrics", icon_url="https://willamette.is-a-cool-femboy.xyz/79_MjqSCH.webp")
                if "Eminem" in spot.artists and random.choice(99) == 69:
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/745509182559748237/1279949791098568746/file-67.gif")
                else:
                    embed.set_thumbnail(url=spot.album_cover_url)
                embed.set_footer(text=f"\nsearched genius for \"{spot.artists[0]} {spot.title}\"", icon_url="https://willamette.is-a-cool-femboy.xyz/79_MjqSCI.webp")
                paged_embeds.append(embed)
            if len(paged_embeds) >= 2:
                time = spot.end - datetime.now(timezone.utc)
                if time.seconds < 60:
                    time = 60
                else:
                    time = time.seconds
                menu = ViewMenu(ctx, style='page $/&', menu_type=ViewMenu.TypeEmbed, timeout=time)
                back_button = ViewButton(style=discord.ButtonStyle.primary, emoji='◀️', label='Back', custom_id=ViewButton.ID_PREVIOUS_PAGE)
                menu.add_button(back_button)
                if len(paged_embeds) >= 3:
                    gtpb = ViewButton(style=discord.ButtonStyle.primary, emoji='🔢', label='Menu' ,custom_id=ViewButton.ID_GO_TO_PAGE)
                    menu.add_button(gtpb)
                next_button = ViewButton(style=discord.ButtonStyle.secondary, emoji='▶️', label='Next', custom_id=ViewButton.ID_NEXT_PAGE)
                menu.add_button(next_button)
                for embed in paged_embeds:
                    menu.add_page(embed)
                await menu.start(send_to=ctx.channel)
            else:
                await ctx.send(embed=paged_embeds[0])