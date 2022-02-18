import discord, random
from discord.ext import commands
from backend.database import *
from backend.tools import *


ROB = Command('rob')

class Rob(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@commands.command(help=ROB.help, aliases=ROB.aliases)
	@commands.cooldown(1, ROB.cooldown, commands.BucketType.user)
	async def rob(self, ctx, member : discord.User):
		user, member = User(ctx.author), User(member)

		if member.get('can_be_robbed') == False:
			await ctx.send(f"{user.discord.mention}, This nerd has a shield he can't be robbed.", delete_after=15)

			return

		if user.get('cash') < 5000:
			await ctx.send(f"{user.discord.mention}, You need atleast {Static().cash} 5000 to rob someone.", delete_after=15)

			return

		if member.get('cash') < 5000:
			await ctx.send(f"{user.discord.mention}, This guy is too poor man why are you doing this. find someone your size :angry:", delete_after=15)

			return

		chance = random.randint(1,2)

		if chance == 2:
			user.remove('cash', 5000)
			
			await ctx.send(f"Get rekt noob {Static().cash} -5000")

			return

		amount = random.randint(round(member.get('cash') / 4), member.get('cash'))

		user.add('cash', amount)
		member.remove('cash', amount)

		await ctx.send(f"You stolen {Static().cash} {amount}!")

		return

def setup(bot):
	bot.add_cog(Rob(bot))