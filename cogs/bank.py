import discord, asyncio, humanize
from discord.ext import commands
from backend.database import *
from backend.tools import *
from typing import Optional, Union


class Bank_view(discord.ui.View):
	def __init__(self, author):
		super().__init__()
		self.value = None
		self.author = author

	async def interaction_check(self, interaction: discord.Interaction):
		return interaction.user.id == self.author.id
	
	@discord.ui.button(label="with", style=discord.ButtonStyle.green)
	async def withdraw(self, button : discord.ui.Button, interaction : discord.Interaction):
		self.value = "withdraw"
		await interaction.response.edit_message(view=self)
		self.stop()        

	@discord.ui.button(label="dep", style=discord.ButtonStyle.red)
	async def deposit(self, button : discord.ui.Button, interaction : discord.Interaction):
		self.value = "deposit"
		await interaction.response.edit_message(view=self)
		self.stop()

	@discord.ui.button(label="give", style=discord.ButtonStyle.blurple)
	async def give(self, button : discord.ui.Button, interaction : discord.Interaction):
		self.value = "give"
		await interaction.response.edit_message(view=self)
		self.stop()


BAL = Command('balance')
WITH = Command('withdraw')
DEP = Command('deposit')
GIVE = Command('give')


class Bank(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@commands.command(help=BAL.help, aliases=BAL.aliases)
	async def balance(self, ctx, member : Optional[discord.User] = None):
		try: await ctx.message.delete()
		except: pass

		user = User(ctx.author) if not (member) else User(member)

		embed = discord.Embed(title=f"{user.discord.name}'s bank", color=int(Static().color_default, 16))
		embed.set_footer(text=Static().footer, icon_url=ctx.author.avatar.url)

		embed.add_field(name=f"{Static().cash} Cash:", value=f"{user.get('cash')} {Style('(' + humanize.intword(user.get('cash')) + ')').highlight}", inline=False)
		embed.add_field(name=":bank: Bank:", value=f"{user.get('bank')} {Style('(' + humanize.intword(user.get('bank')) + ')').highlight}", inline=False)

		view = Bank_view(ctx.author)

		view.withdraw.disabled = True if user.get('bank') <= 0 else False
		view.deposit.disabled = True if user.get('cash') <= 0 else False
		view.give.disabled = True if user.get('cash') <= 0 else False

		msg = await ctx.send(embed=embed, view=view) if not (member) else await ctx.send(embed=embed)
		await view.wait()

		if view.value == None:
			await msg.delete()

			for button in view.children: button.disabled = True

		if view.value == "withdraw":
			await msg.delete()
			await self.withdraw(ctx)
		
		if view.value == "deposit":
			await msg.delete()
			await self.deposit(ctx)
		
		if view.value == "give":
			await msg.delete()
			await self.give(ctx)


	@commands.command(help=WITH.help, aliases=WITH.aliases)
	async def withdraw(self, ctx, amount : Union[int, str] = None):
		try: await ctx.message.delete()
		except: pass

		if amount == None: amount = await self.get_amount(ctx)

		user = User(ctx.author)

		if type(amount) is str and amount.strip().lower() == "all" and user.get('bank') >= 1:
			amount = user.get('bank')

		if amount <= 0:
			await ctx.send(f"{ctx.author.mention}, Minimum withdraw is {Static().cash} 1.", delete_after=15)

			return

		if amount > user.get('bank'):
			await ctx.send(f"{ctx.author.mention}, You don't have {Static().cash} {amount} in your bank.", delete_after=15)

			return

		user.add('cash', amount)
		user.remove('bank', amount)

		embed = discord.Embed(title=f"Withdrawn {Static().cash} {amount}", color=int(Static().color_green, 16))
		embed.set_footer(text=Static().footer, icon_url=ctx.author.avatar.url)

		await ctx.send(embed=embed)	

	@commands.command(help=DEP.help, aliases=DEP.aliases)
	async def deposit(self, ctx, amount : Union[int, str] = None):
		try: await ctx.message.delete()
		except: pass

		if amount == None: amount = await self.get_amount(ctx)

		user = User(ctx.author)

		if type(amount) is str and amount.strip().lower() == "all" and user.get('cash') >= 1:
			amount = user.get('cash')

		if amount <= 0:
			await ctx.send(f"{ctx.author.mention}, Minimum deposit is {Static().cash} 1.", delete_after=15)

			return

		if amount > user.get('cash'):
			await ctx.send(f"{ctx.author.mention}, You don't have {Static().cash} {amount}.", delete_after=15)

			return

		user.add('bank', amount)
		user.remove('cash', amount)

		embed = discord.Embed(title=f"Deposited {Static().cash} {amount}", color=int(Static().color_green, 16))
		embed.set_footer(text=Static().footer, icon_url=ctx.author.avatar.url)

		await ctx.send(embed=embed)


	@commands.command(help=GIVE.help, aliases=GIVE.aliases)
	async def give(self, ctx, member : discord.User = None, amount : Union[int, str] = None):
		try: await ctx.message.delete()
		except: pass

		if amount == None: amount = await self.get_amount(ctx)


	async def get_amount(self, ctx):
		while True:
			msg = await ctx.send(f"{ctx.author.mention}, Amount?")

			def check(m):
				return m.guild.id == ctx.guild.id and m.channel.id == ctx.channel.id and m.author.id == ctx.author.id

			try:
				message = await self.bot.wait_for('message', check=check, timeout=60.0)
			except asyncio.TimeoutError:
				await msg.delete()

				return
			else:
				if message.content.isnumeric(): return int(message.content)

				if message.content.strip().lower() == "all": return "all"
				
				continue


def setup(bot):
	bot.add_cog(Bank(bot))