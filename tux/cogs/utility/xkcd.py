import discord
import requests
import xkcd_wrapper
from discord import app_commands
from discord.ext import commands
from loguru import logger

from tux.utils.embeds import EmbedCreator


class XKCD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = xkcd_wrapper.Client()

    group = app_commands.Group(name="xkcd", description="xkcd commands")

    @group.command(name="newest", description="Get the latest xkcd comic")
    async def newest(self, interaction: discord.Interaction) -> None:
        try:
            latest_comic = self.client.latest(raw_comic_image=True)
            embed = EmbedCreator.create_success_embed(
                title="Latest xkcd Comic", description=latest_comic.title, interaction=interaction
            )
            embed.set_image(url=latest_comic.image_url)
            embed.add_field(
                name="Explainxkcd URL", value=latest_comic.explanation_url, inline=False
            )
            embed.add_field(name="Webpage URL", value=latest_comic.comic_url, inline=False)
            logger.info(f"{interaction.user} got the latest xkcd comic in {interaction.channel}")
            await interaction.response.send_message(embed=embed)
        except requests.HTTPError:
            embed = EmbedCreator.create_error_embed(
                title="Error",
                description="An HTTP error occurred, please try again.",
                interaction=interaction,
            )
            await interaction.response.send_message(embed=embed)
        except requests.Timeout:
            embed = EmbedCreator.create_error_embed(
                title="Error",
                description="A timeout has occoured, please try again.",
                interaction=interaction,
            )
            await interaction.response.send_message(embed=embed)

    @group.command(name="random", description="Get a random xkcd comic")
    async def random(self, interaction: discord.Interaction) -> None:
        try:
            random_comic = self.client.random(raw_comic_image=True)
            embed = EmbedCreator.create_success_embed(
                title="Random xkcd Comic", description=random_comic.title, interaction=interaction
            )
            embed.set_image(url=random_comic.image_url)
            embed.add_field(
                name="Explainxkcd URL", value=random_comic.explanation_url, inline=False
            )
            embed.add_field(name="Webpage URL", value=random_comic.comic_url, inline=False)
            await interaction.response.send_message(embed=embed)
        except requests.HTTPError:
            embed = EmbedCreator.create_error_embed(
                title="Error",
                description="An HTTP error occurred, please try again.",
                interaction=interaction,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except requests.Timeout:
            embed = EmbedCreator.create_error_embed(
                title="Error",
                description="A timeout has occurred, please try again.",
                interaction=interaction,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @group.command(name="specific", description="Search for a specific xkcd comic")
    async def specific(self, interaction: discord.Interaction, comic_id: int) -> None:
        try:
            specific_comic = self.client.get(comic_id=comic_id, raw_comic_image=True)
            embed = EmbedCreator.create_success_embed(
                title=f"xkcd comic {comic_id}",
                description=specific_comic.title,
                interaction=interaction,
            )
            embed.set_image(url=specific_comic.image_url)
            embed.add_field(
                name="Explainxkcd URL", value=specific_comic.explanation_url, inline=False
            )
            embed.add_field(name="Webpage URL", value=specific_comic.comic_url, inline=False)
            await interaction.response.send_message(embed=embed)
        except requests.HTTPError:
            embed = EmbedCreator.create_error_embed(
                title="Error",
                description="An HTTP error occurred, please try again.",
                interaction=interaction,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except requests.Timeout:
            embed = EmbedCreator.create_error_embed(
                title="Error",
                description="A timeout has occoured, please try again.",
                interaction=interaction,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(XKCD(bot))


""" Sets up the actual XKCD cog for the bot."""
