import discord, random
from discord.ext import commands
from backend.database import *
from backend.tools import *


class BJ_view(discord.ui.View):
	def __init__(self, author):
		super().__init__()
		self.value = None
		self.author = author

	async def interaction_check(self, interaction: discord.Interaction):
		return interaction.user.id == self.author.id
	
	@discord.ui.button(label="hit", style=discord.ButtonStyle.red)
	async def hit(self, button : discord.ui.Button, interaction : discord.Interaction):
		self.value = "hit"
		await interaction.response.edit_message(view=self)
		self.stop()        

	@discord.ui.button(label="stand", style=discord.ButtonStyle.green)
	async def stand(self, button : discord.ui.Button, interaction : discord.Interaction):
		self.value = "stand"
		await interaction.response.edit_message(view=self)
		self.stop()

	@discord.ui.button(label="give up", style=discord.ButtonStyle.red)
	async def give_up(self, button : discord.ui.Button, interaction : discord.Interaction):
		self.value = "give up"
		await interaction.response.edit_message(view=self)
		self.stop()


BJ = Command('blackjack')

class Gamble(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@commands.command(help=BJ.help, aliases=BJ.aliases)
	@commands.cooldown(1, BJ.cooldown)
	async def blackjack(self, ctx, amount : int):
		user = User(ctx.author)

		if user.get('cash') < amount:
			await ctx.send(f"{ctx.author.mention}, You don't have {Static().cash} {amount}.", delete_after=15)

			return

		def get_card():
			return random.randint(1,13)

		player = [get_card()]
		dealer = [get_card()]
		
		desc = ""
		color = Static().color_green
		won = False
		stop = False

		user.remove('cash', amount)

		print('\n\n', "removing betting amount")

		while True:
			await ctx.send(f"player: {sum(player)}, {player}\ndealer: {sum(dealer)}, {dealer}")

			if sum(player) > 21:
				title = f"You went over 21 and lost {Static().cash} {amount}"
				color = Static().color_red
				win = True

				print('\n\n', "over 21")

				break

			if sum(dealer) > 21:
				title = f"The dealer went over 21 and you won {Static().cash} {amount * 2}"
				win = True

				user.add('cash', amount * 2)

				print('\n\n', "dealer over 21")

				break

			if sum(player) == 21:
				title = f"You got a solid 21 and won {Static().cash} {amount * 2}"
				win = True

				user.add('cash', amount * 2)

				print('\n\n', "21")

				break

			if sum(dealer) == 21:
				title = f"The leader won with a solid 21! You lost {Static().cash} {amount}"
				color = Static().color_red
				win = True 

				print('\n\n', "dealer 21")

				break

			if (stop): print('\n\n', "stop true"); break

			embed = discord.Embed(title="Blackjack", color=int(Static().color_default, 16))
			embed.set_footer(text=Static().footer, icon_url=ctx.author.avatar.url)

			embed.add_field(name=f"{ctx.author}: {Style(f'({sum(player)})').highlight}", value=', '.join([str(card) for card in player]), inline=False)
			embed.add_field(name=f"Dealer: {Style(f'({sum(dealer)})').highlight}", value=', '.join([str(card) for card in dealer]), inline=False)

			view = BJ_view(ctx.author)

			await ctx.send(embed=embed, view=view)
			await view.wait()

			if view.value == "hit":
				player.append(get_card())

				print('\n\n', "hit")

				continue
			
			if view.value == "stand":
				if sum(dealer) > 16:
					if sum(player) > sum(dealer):
						dealer.append(get_card())

						print('\n\n', "dealer desperate hit")

				else:
					if sum(dealer) > sum(player) and sum(dealer) < 21:
						stop = True

						print('\n\n', "dealer higher than player")

						continue

					dealer.append(get_card())

					print('\n\n', "dealer hit")

				stop = True

				continue

			if view.value == "give up":
				title = f"You gave up and lost {Static().cash} {amount}"
				color = Static().color_red
				win = True

				print('\n\n', "give up")

				break

		if not (won):
			if sum(player) > sum(dealer) and sum(player) <= 21:
				title = f"You won with a {sum(player)} and got {Static().cash} {amount * 2}"
				user.add('cash', amount * 2)
				won = True

				print('\n\n', "higher than dealer and less than 21")
			
			elif sum(dealer) > 21 and sum(player) > 21:
				user.add('cash', amount)
				title = f"You both went over 21. Its a draw!"
				color = Static().color_default
				won = True

				print('\n\n', "dealer over 21")
			
			else:
				color = Static().color_red
				won = True
				
				if sum(player) > 21:
					title = f"You went over 21 and the dealer won! You lost {Static().cash} {amount}"

					print('\n\n', "player over 21 in win false")
				
				else:
					title = f"The dealer won with a {sum(dealer)}! You lost {Static().cash} {amount}"

					print('\n\n', "dealer less than player in win false")

		embed = discord.Embed(title=title, description=desc, color=int(color, 16))
		embed.set_footer(text=Static().footer, icon_url=ctx.author.avatar.url)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Gamble(bot))