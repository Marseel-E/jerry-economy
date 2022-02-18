import discord, json
from discord.ext import commands
from backend.database import *
from backend.tools import *
from typing import Optional, Union


class Inv_view(discord.ui.View):
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


INV = Command('inventory')

with open('backend/items.txt') as f:
	items = json.loads(f.read())


class Inv(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@commands.command(help=INV.help, aliases=INV.aliases)
	async def inventory(self, ctx, member : Optional[discord.User] = None, page : Optional[int] = None):
		try: await ctx.message.delete()
		except: pass

		user = User(ctx.author) if not (member) else User(member)

		if not (user.inventory):
			await ctx.send(f"{user.discord.name}'s inventory is empty.", delete_after=15) if (member) else await ctx.send(f"Your inventory is empty.", delete_after=15)

			return

		embed = discord.Embed(title=f"{user.discord.name}'s inventory", color=int(Static().color_default, 16))

		i = int(page * 5) - 5 if (page) else 0

		while True:
			if i + 1 == len(user.inventory):
				embed.set_footer(text=f"Page: {round(i / 5)} / {round(len(user.inventory) / 5)} | {Static().footer}", icon_url=ctx.author.avatar.url)

				view = Inv_view(ctx.author)

				view.previous.disabled = True if len(user.inventory) / 5 <= 1 else False
				view.next.disabled = True

				msg = await ctx.send(embed=embed, view=view)
				await view.wait()

				if view.value == None:
					await msg.delete()

					for button in view.children: button.disabled = True

					return

				if view.value == "previous":
					i -= len(embed.fields) + 5
					
					await msg.delete()
					embed = discord.Embed(title=f"{user.discord.name}'s inventory", color=int(Static().color_default, 16))

					i += 1

					embed.add_field(name=f"{items[list(user.inventory.keys())[i]]['icon']} {list(user.inventory.keys())[i].capitalize()}", value=list(user.inventory.values())[i], inline=False)

					continue

			if i in [n for n in range(1, len(user.inventory)) if n % 5 == 0]:
				if len(embed.fields) < 5 and i != len(items):
					for _i in range(len(embed.fields), 5):
						i += _i

						embed.add_field(name=f"{items[list(user.inventory.keys())[i]]['icon']} {list(user.inventory.keys())[i].capitalize()}", value=list(user.inventory.values())[i], inline=False)

				embed.set_footer(text=f"Page: {round(i / 5)} / {round(len(user.inventory) / 5)} | {Static().footer}", icon_url=ctx.author.avatar.url)

				view = Inv_view(ctx.author)

				view.previous.disabled = True if round(i / 5) <= 1 else False
				view.next.disabled = True if len(embed.fields) < 5 or i + 1 == len(items) else False

				msg = await ctx.send(embed=embed, view=view)
				await view.wait()

				if view.value == None:
					await msg.delete()

					for button in view.children: button.disabled = True

					return

				if view.value == "previous":
					i -= len(embed.fields) + 5
					
					await msg.delete()
					embed = discord.Embed(title=f"{user.discord.name}'s inventory", color=int(Static().color_default, 16))

					i += 1

					embed.add_field(name=f"{items[list(user.inventory.keys())[i]]['icon']} {list(user.inventory.keys())[i].capitalize()}", value=list(user.inventory.values())[i], inline=False)

					continue

				if view.value == "next":
					await msg.delete()
					embed = discord.Embed(title=f"{user.discord.name}'s inventory", color=int(Static().color_default, 16))

					i += 1

					embed.add_field(name=f"{items[list(user.inventory.keys())[i]]['icon']} {list(user.inventory.keys())[i].capitalize()}", value=list(user.inventory.values())[i], inline=False)

					continue

			i += 1

			embed.add_field(name=f"{items[list(user.inventory.keys())[i]]['icon']} {list(user.inventory.keys())[i]}", value=f"{Style(list(user.inventory.values())[i]).highlight}", inline=False)


def setup(bot):
	bot.add_cog(Inv(bot))