import deepl
import discord
import json

from pathlib import Path
from redbot.core import commands

class Translate(commands.Cog):
    """Translates text using DeepL."""

    def __init__(self, bot):
        self.bot = bot
        with open(Path(__file__).parent / "languages.json", encoding="utf-8") as a:
            self.languages = json.load(a)

    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        pass

    @commands.command()
    async def translate(self, ctx, language: str, *, text: str):
        """
        Translates the given text using DeepL.
        Visit https://developers.deepl.com/docs/getting-started/supported-languages for language codes.
        """
        auth_key = await self.bot.get_shared_api_tokens("deepl")
        language = language.upper()
        if auth_key.get("api_key") is None:
            if ctx.author is ctx.guild.owner:
                return await ctx.send(f"you haven't set a deepl api key! get one at https://www.deepl.com/en/pro#api, then use {ctx.prefix}set api, using `deepl` as the service and `api_key <your api key>` in the keys and tokens section.")
            else:
                return await ctx.send(f"the bot owner hasn't set a deepl api key.")
        async with ctx.typing():
            deepl_client = deepl.DeepLClient(auth_key["api_key"])
            if language in self.languages.keys():
                pass
            elif language.lower() in self.languages.values(): # fallback only
                keys = [key for key, value in self.languages.items() if value == language.lower()]
                if keys:
                    language = keys[0]                      
            else:
                return await ctx.send(f"i couldn't understand the language code provided; please visit the DeepL documentation to find valid codes (available through  `{ctx.prefix}help translate`).")
            result = deepl_client.translate_text(text, target_lang=language, preserve_formatting=True)
            embed = discord.Embed(description=result.text, color=await ctx.embed_color())
            embed.set_footer(text=f"translated from {self.languages[result.detected_source_lang]} to {self.languages[language]}")
            await ctx.send(embed=embed)