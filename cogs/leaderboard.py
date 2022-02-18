import discord
from discord.ext import commands
from backend.database import *
from backend.tools import *


class LB_view(discord.ui.View):
	def __init__(self, author):
		super().__init__()
		self.value = None
		self.author = author

	async def interaction_check(self, interaction: discord.Interaction):
		return interaction.user.id == self.author.id
	
	@discord.ui.button(label="◀", style=discord.ButtonStyle.gray)
	async def previous(self, button : discord.ui.Button, interaction : discord.Interaction):
		self.value = "previous"
		await interaction.response.edit_message(view=self)
		self.stop()

	@discord.ui.button(label="▶", style=discord.ButtonStyle.gray)
	async def next(self, button : discord.ui.Button, interaction : discord.Interaction):
		self.value = "next"
		await interaction.response.edit_message(view=self)
		self.stop()


LB = Command('leaderboard')

class LB(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@commands.command(help=LB.help, aliases=LB.aliases)
	async def leaderboard(self, ctx, page : int = None):
		async def get_cash(d):
			return User(await self.bot.fetch_user(int(d))).get('cash')

		users = sorted(Database().users, reverse=True, key=get_cash)
		text = ""

		for user in users:
			user = User(await self.bot.fetch_user(int(d)))
			
			text += f"{user.discord} {Style(user.get('cash')).highlight}\n"

		await ctx.send(text)



def setup(bot):
	bot.add_cog(LB(bot))