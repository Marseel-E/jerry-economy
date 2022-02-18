import discord, asyncio, random, json
from discord.ext import commands, tasks
from typing import Optional
from backend.database import *
from backend.tools import *
from datetime import datetime, timedelta
from humanize import naturaldelta


with open('backend/items.txt') as f:
	items = json.loads(f.read())

WORK = Command('work')

class Work(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.jobs = {
			"diver": {
					"tool": "diving gear",
					"min_paycheck": 100,
					"max_paycheck": 10000,
					"cooldown": 60.0
				},
			"boxer": {
					"tool": "boxing gloves",
					"min_paycheck": 100,
					"max_paycheck": 10000,
					"cooldown": 60.0
				},
			"athlete": {
					"tool": "ball",
					"min_paycheck": 100,
					"max_paycheck": 10000,
					"cooldown": 60.0
				},
			"gamer": {
					"tool": "controller",
					"min_paycheck": 100,
					"max_paycheck": 10000,
					"cooldown": 60.0
				},
			"youtuber": {
					"tool": "camera",
					"min_paycheck": 100,
					"max_paycheck": 10000,
					"cooldown": 60.0
				},
			"dancer": {
					"tool": "dancing shoes",
					"min_paycheck": 100,
					"max_paycheck": 10000,
					"cooldown": 60.0
				},
			"taxi driver": {
					"tool": "taxi",
					"min_paycheck": 1000,
					"max_paycheck": 100000,
					"cooldown": 60.0
				}
		}


	@commands.command(help=WORK.help, aliases=WORK.aliases)
	async def work(self, ctx):
		try: await ctx.message.delete()
		except: pass
		
		user = User(ctx.author)
		job = user.get('job')

		if not (job):
			await ctx.send(f"{ctx.author.mention}, It looks like you don't have a job.", delete_after=5)

			embed = discord.Embed(title="Jobs list", color=int(Static().color_default, 16))
			embed.set_footer(text=f"Reply with the job you'd like to work! | {Static().footer}", icon_url=ctx.author.avatar.url)

			for name, values in self.jobs.items():
				name = f"(:x:) {Style(name.capitalize()).linethrough}" if values['tool'] not in list(user.inventory.keys()) else f"(:white_check_mark:) {Style(name.capitalize()).bold}"

				embed.add_field(name=name, value=f"Requires: {items[values['tool']]['icon']} {Style(values['tool'].capitalize()).italic}", inline=False)

			msg = await ctx.send(embed=embed)

			def check(m):
				return m.guild.id == ctx.guild.id and m.channel.id == ctx.channel.id and m.author.id == ctx.author.id

			try:
				message = await self.bot.wait_for('message', check=check, timeout=WORK.timeouts['choose_job'])
			except asyncio.TimeoutError:
				await msg.delete()

				return
			else:
				job = message.content.strip().lower()

				if job not in self.jobs.keys():
					await ctx.send(f"{ctx.author.mention}, This is not a valid job.", delete_after=15)

					return

				job_tool = self.jobs[job]['tool']

				if job_tool not in list(user.inventory.keys()):
					await ctx.send(f"{ctx.author.mention}, This job requires {items[job_tool]['icon']} {Style(job_tool.capitalize()).highlight}.", delete_after=15)

					return

				user.update('job', job)

				embed = discord.Embed(title=f"You're now working as {items[job_tool]['icon']} {job.capitalize()}!", color=int(Static().color_green, 16))
				embed.set_footer(text=Static().footer, icon_url=ctx.author.avatar.url)

				await ctx.send(embed=embed)

		if "last_worked" in list(user.data.keys()) and datetime.utcnow() < Convert(user.get('last_worked')).datetime:
			await ctx.send(f"{ctx.author.mention}, Your shift is over.\nNext shift in {Style(naturaldelta(datetime.utcnow() - Convert(user.get('last_worked')).datetime)).highlight}", delete_after=15)

			return

		paycheck = random.randint(self.jobs[job]['min_paycheck'], self.jobs[job]['max_paycheck'])

		user.add('cash', paycheck)
		user.update('last_worked', str(datetime.utcnow() + timedelta(minutes=self.jobs[job]['cooldown'])))

		await ctx.send(f"{ctx.author.mention}, You worked very hard and got payed {Static().cash} {paycheck}")


def setup(bot):
	bot.add_cog(Work(bot))