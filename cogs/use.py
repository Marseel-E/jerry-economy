import discord, random, asyncio, json
from discord.ext import commands, tasks
from backend.database import *
from backend.tools import *
from datetime import datetime, timedelta
from typing import Optional, Union


with open('backend/items.txt') as f:
	items_data = json.loads(f.read())


class Use(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.items_handler.start()


	def cog_unload(self):
		self.items_handler.cancel()

	@tasks.loop(seconds=1.0)
	async def items_handler(self):
		for _id, data in Database().users.items():
			# lock
			if data['can_be_robbed'] == False and Convert(data['lock_end_time']).datetime <= datetime.utcnow():
				user = User(await self.bot.fetch_user(int(_id)))
				user.update('can_be_robbed', True)
				await user.discord.send(f"Your :lock: has expired! People now can rob you.")

	@items_handler.before_loop
	async def before_items_handler(self):
		await self.bot.wait_until_ready()


	USE = Command('use')
	@commands.group(invoke_without_command=False, help=USE.help, aliases=USE.aliases)
	async def use(self, ctx): pass


	LOCK = Command('lock')
	@use.command(help=LOCK.help, aliases=LOCK.aliases)
	async def lock(self, ctx):
		user = User(ctx.author)

		if not (user.get('can_be_robbed')):
			await ctx.send(f"{ctx.author.mention}, Your wallet is locked already dude chill.", delete_after=15)

			return

		if 'lock' not in list(user.inventory.keys()):
			await ctx.send(f"{ctx.author.mention}, You don't have a :lock: silly.", delete_after=15)

			return

		user.remove('inventory/lock', 1)

		user.update('can_be_robbed', False)
		user.update('lock_end_time', str(datetime.utcnow() + timedelta(hours=12)))

		embed = discord.Embed(title="Used :lock:", description="Your wallet will be secure for the next 12 hours!", color=int(Static().color_green, 16))
		embed.set_footer(text=Static().footer, icon_url=ctx.author.avatar.url)

		await ctx.send(embed=embed)


	LP = Command('lockpicker')
	@use.command(help=LP.help, aliases=LP.aliases)
	async def lockpicker(self, ctx, member : discord.User):
		user, member = User(ctx.author), User(member)

		if (member.get('can_be_robbed')):
			await ctx.send(f"{ctx.author.mention}, This guy's wallet ain't secured bruh", delete_after=15)

			return

		if 'lockpicker' not in list(user.inventory.keys()):
			await ctx.send(f"{ctx.author.mention}, You don't have a :safety_pin: silly.", delete_after=15)

			return

		user.remove('inventory/lockpicker', 1)

		member.update('can_be_robbed', True)

		embed = discord.Embed(title="Used :safety_pin:", description="You can now rob this dumbass.", color=int(Static().color_green, 16))
		embed.set_footer(text=Static().footer, icon_url=ctx.author.avatar.url)

		await ctx.send(embed=embed)


	PRT = Command('printer')
	@use.command(help=PRT.help, aliases=PRT.aliases)
	async def printer(self, ctx, amount : Optional[int] = None):
		user = User(ctx.author)

		if 'printer' not in list(user.inventory.keys()):
			await ctx.send(f"{ctx.author.mention}, You don't have a :printer: silly.", delete_after=15)

			return

		if not (amount):
			msg = await ctx.send(f"How much {Static().cash} do you want to print?")

			def check(m):
				return m.guild.id == ctx.guild.id and m.channel.id == ctx.channel.id and m.author.id == ctx.author.id

			try:
				message = await self.bot.wait_for('message', check=check, timeout=PRT.timeouts['get_amount'])
			except asyncio.TimeoutError:
				await msg.delete()

				return
			else:
				if not (message.content.strip().isnumeric()):
					await msg.delete()
					await ctx.send(f"{message.content.strip()} ain't a number bruh who taught you math?", delete_after=15)

					return

				await msg.delete()

				amount = int(message.content.strip())

		if amount > user.get('cash'):
				await ctx.send(f"How will you print {Static().cash} {amount} if you don't have it?????", delete_after=15)

				return

		if random.randint(1,2) == 2:
			user.remove('inventory/printer', 1)
			
			await ctx.send(f"Your :printer: broke lmfao")

		if random.randint(1,2) == 2:
			user.remove('cash', amount)

			await ctx.send(f"You were caught lol. oh btw they took your {Static().cash} {amount} :laughing:")

			return

		amount = random.randint(amount, amount * 2) - amount

		user.add('cash', amount)

		embed = discord.Embed(title="Used :printer:", description=f"You managed to print {Static().cash} {amount} somehow.", color=int(Static().color_green, 16))
		embed.set_footer(text=Static().footer, icon_url=ctx.author.avatar.url)

		await ctx.send(embed=embed)


	MP = Command('mystery package')
	@use.command(help=MP.help, aliases=MP.aliases)
	async def mystery_package(self, ctx, amount : Optional[int] = 1):
		user = User(ctx.author)

		if 'mystery package' not in list(user.inventory.keys()):
			await ctx.send(f"{ctx.author.mention}, You don't have a :package: silly.", delete_after=15)

			return

		if amount > user.inventory['mystery package']: amount = int(user.inventory['mystery package'])

		items_with_prices = {}
		for key, value in items_data.items():
			items_with_prices[key] = value['price'] * 0.1

		package_items = random.choices(list(items_with_prices.keys()), weights = list(items_with_prices.values()), k = amount)

		embed = discord.Embed(description=Style("Used :package:!").bold, color=int(Static().color_green, 16))
		embed.set_footer(text=Static().footer, icon_url=ctx.author.avatar.url)

		for item in package_items:
			user.add(item, 1)
			embed.add_field(name=items_data[item]['icon'] + " " + Style(item.capitalize()).bold, value=Static().cash + " " + items_data[item]['price'], inline=False)

		await ctx.send(embed=embed)


	@use.command(aliases=['explosives', 'ancient scroll', 'laptop', 'flashlight', 'charger', 'magnet', 'cigarrete', 'mouse trap', 'antibiotics', 'books', 'map', 'helicopter', 'rocket', 'car', 'bycicle', 'racing car', 'pallete', 'parachute', 'beer', 'milk', 'donut', 'fortune cookie', 'glasses', 'gloves', 'sandals', 'bone', 'metal hand', 'brain'])
	async def aint_done(self, ctx):
		await ctx.send(f"Ain't done")


def setup(bot):
	bot.add_cog(Use(bot))