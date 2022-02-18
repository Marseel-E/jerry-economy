import discord, asyncio, json
from discord.ext import commands
from backend.database import *
from backend.tools import *
from typing import Optional, Union


class Shop_view(discord.ui.View):
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

	@discord.ui.button(label="🛒", style=discord.ButtonStyle.green)
	async def buy(self, button : discord.ui.Button, interaction : discord.Interaction):
		self.value = "buy"
		await interaction.response.edit_message(view=self)
		self.stop()

	@discord.ui.button(label="▶", style=discord.ButtonStyle.gray)
	async def next(self, button : discord.ui.Button, interaction : discord.Interaction):
		self.value = "next"
		await interaction.response.edit_message(view=self)
		self.stop()


with open('backend/items.txt') as f:
	items = json.loads(f.read())

SHOP = Command('shop')
BUY = Command('buy')


class Shop(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@commands.command(help=SHOP.help, aliases=SHOP.aliases)
	async def shop(self, ctx, page : Optional[int] = None):
		try: await ctx.message.delete()
		except: pass

		user = User(ctx.author)

		embed = discord.Embed(title="Shop", color=int(Static().color_default, 16))

		i = int(page * 5) - 5 if (page) else 0

		while True:
			if i + 1 == len(items):

				embed.set_footer(text=f"Page: {round(i / 5)} / {round(len(items) / 5)} | {Static().footer}", icon_url=user.discord.avatar.url)

				view = Shop_view(user.discord)

				view.previous.disabled = True if len(items) / 5 <= 1 else False
				view.buy.disabled = True if user.get('cash') <= 0 else False
				view.next.disabled = True

				msg = await ctx.send(embed=embed, view=view)
				await view.wait()

				if view.value == None:
					await msg.delete()

					for button in view.children: button.disabled = True

					break

				if view.value == "previous":
					i -= len(embed.fields) + 5
					
					await msg.delete()
					embed = discord.Embed(title="Shop", color=int(Static().color_default, 16))

					i += 1

					name = f"{list(items.values())[i]['icon']} {list(items.keys())[i].capitalize()} "

					try: name += Style(f"({user.inventory[list(items.keys())[i]]})").highlight
					except: pass

					price = f"{Static().cash} {Style(list(items.values())[i]['price']).highlight}\n{Style(list(items.values())[i]['info']).italic}"

					embed.add_field(name=name, value=price, inline=False)

					continue

				if view.value == "buy":
					await msg.delete()
					await self.buy(ctx)

					break

			if i in [n for n in range(1, len(items)) if n % 5 == 0]:
				if len(embed.fields) < 5 and i != len(items):
					for _i in range(len(embed.fields), 5):
						i += _i

						name = f"{list(items.values())[i]['icon']} {list(items.keys())[i].capitalize()} "

						try: name += Style(f"({user.inventory[list(items.keys())[i]]})").highlight
						except: pass

						price = f"{Static().cash} {Style(list(items.values())[i]['price']).highlight}\n{Style(list(items.values())[i]['info']).italic}"

						embed.add_field(name=name, value=price, inline=False)

				embed.set_footer(text=f"Page: {round(i / 5)} / {round(len(items) / 5)} | {Static().footer}", icon_url=user.discord.avatar.url)

				view = Shop_view(user.discord)

				view.previous.disabled = True if round(i / 5) <= 1 else False
				view.buy.disabled = True if user.get('cash') <= 0 else False
				view.next.disabled = True if len(embed.fields) < 5 or i + 1 == len(items) else False

				msg = await ctx.send(embed=embed, view=view)
				await view.wait()

				if view.value == None:
					await msg.delete()

					for button in view.children: button.disabled = True

					break

				if view.value == "previous":
					i -= len(embed.fields) + 5
					
					await msg.delete()
					embed = discord.Embed(title="Shop", color=int(Static().color_default, 16))

					i += 1

					name = f"{list(items.values())[i]['icon']} {list(items.keys())[i].capitalize()} "

					try: name += Style(f"({user.inventory[list(items.keys())[i]]})").highlight
					except: pass

					price = f"{Static().cash} {Style(list(items.values())[i]['price']).highlight}\n{Style(list(items.values())[i]['info']).italic}"

					embed.add_field(name=name, value=price, inline=False)
					continue

				if view.value == "buy":
					await msg.delete()
					await self.buy(ctx)

					break

				if view.value == "next":
					await msg.delete()
					embed = discord.Embed(title="Shop", color=int(Static().color_default, 16))

					i += 1

					name = f"{list(items.values())[i]['icon']} {list(items.keys())[i].capitalize()} "

					try: name += Style(f"({user.inventory[list(items.keys())[i]]})").highlight
					except: pass

					price = f"{Static().cash} {Style(list(items.values())[i]['price']).highlight}\n{Style(list(items.values())[i]['info']).italic}"

					embed.add_field(name=name, value=price, inline=False)

					continue

			i += 1

			name = f"{list(items.values())[i]['icon']} {list(items.keys())[i].capitalize()} "

			try: name += Style(f"({user.inventory[list(items.keys())[i]]})").highlight
			except: pass

			price = f"{Static().cash} {Style(list(items.values())[i]['price']).highlight}\n{Style(list(items.values())[i]['info']).italic}"

			embed.add_field(name=name, value=price, inline=False)

	@commands.command(help=BUY.help, aliases=BUY.aliases)
	async def buy(self, ctx, item : Optional[str] = None, amount : Union[int, str] = 1):
		try: await ctx.message.delete()
		except: pass

		if item == None:
			msg = await ctx.send(f"{ctx.author.mention}, What would you like to buy?")

			def check(m):
				return m.guild.id == ctx.guild.id and m.channel.id == ctx.channel.id and m.author.id == ctx.author.id

			try:
				message = await self.bot.wait_for('message', check=check, timeout=BUY.timeouts['choose_item'])
			except asyncio.TimeoutError:
				await msg.delete()

				return
			else:
				await msg.delete()

				if message.content.strip().lower() not in list(items.keys()):
					await ctx.send(f"{ctx.author.mention}, Theres no such item as ({message.content})", delete_after=15)

					return

				item = message.content.strip().lower()

		if item not in list(items.keys()):
			await ctx.send(f"{ctx.author.mention}, Theres no such item as ({message.content})", delete_after=15)

			return

		user = User(ctx.author)

		if type(amount) is str and not (amount.isnumeric()):
			if amount.strip().lower() == "max":
				amount = round(user.get('cash') / items[item]['price'])

			else:
				await ctx.send(f"{ctx.author.mention}, `amount` must be numbers or `max`.", delete_after=15)

				return

		if amount <= 0:
			await ctx.send(f"{ctx.author.mention}, You can't buy less than 1 item.", delete_after=15)

			return

		if items[item]['price'] * amount > user.get('cash'):
			await ctx.send(f"{ctx.author.mention}, You can't afford {Style(amount).highlight} {items[item]['icon']} {Style(item).highlight}.")

			return

		user.update(f'inventory/{item}', amount) if 'inventory' not in list(user.data.keys()) or item not in list(user.inventory.keys()) else user.add(f'inventory/{item}', amount)
		user.remove('cash', items[item]['price'] * amount)

		embed = discord.Embed(title=f"Bought {amount} {items[item]['icon']} {item.capitalize()}", color=int(Static().color_default, 16))
		embed.set_footer(text=Static().footer, icon_url=ctx.author.avatar.url)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Shop(bot))