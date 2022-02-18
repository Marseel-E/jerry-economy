import discord
from discord.ext import commands
from backend.database import *
from backend.tools import *
from datetime import datetime, timedelta


class Activity(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.activity_roles = {
			910671623852527648: 100,
			910671696535617577: 1000,
			910671759789920306: 10000,
			910671796230029333: 100000,
		}


	@commands.Cog.listener(name='on_message')
	async def on_message(self, message):
		if (message.author.bot): return

		if str(message.author.id) in list(Database().users.keys()):
			user = User(message.author)

			if 'last_message' not in list(user.data.keys()) or datetime.utcnow() >= Convert(user.get('last_message')).datetime:
				user.add('messages', 1)
				user.update('last_message', str(datetime.utcnow() + timedelta(seconds=5)))

			for role_id, required_messages in self.activity_roles.items():
				if user.get('messages') >= required_messages:
					role = message.guild.get_role(role_id)

					if role in user.discord.roles: continue

					await user.discord.add_roles(role)

					embed = discord.Embed(description=Style(f"Congratulations you're now {role.mention}").bold, color=int(Static().color_green, 16))
					embed.set_footer(text=Static().footer, icon_url=user.discord.avatar.url)

					await message.channel.send(embed=embed)

					return

		await self.bot.process_commands(message)


def setup(bot):
	bot.add_cog(Activity(bot))