import random, discord
from .database import *
from datetime import datetime


class Generate:
	def __init__(self): pass
	
	def id(self, length : int): return int(''.join(map(str, [random.randint(0,9) for i in range(1, length)])))


class Style:
	def __init__(self, text, type = ""):
		self.box = f"```{type}\n{str(text)}\n```"
		self.highlight = f"`{str(text)}`"
		self.bold = f"**{str(text)}**"
		self.italic = f"*{str(text)}*"
		self.censor = f"||{str(text)}||"
		self.textToSpeach = f"/ttc {str(text)}"
		self.quote = f"> {str(text)}"
		self.underline = f"__{str(text)}__"
		self.linethrough = f"~~{str(text)}~~"


class Command:
	def __init__(self, name):
		self.db = {
			"py": {
				"help": "Help",
				"aliases": ['python', 'eval']
			},
			"load": {
				"help": "load"
			},
			"reload": {
				"help": "reload"
			},
			"unload": {
				"help": "unload"
			},
			"shop": {
				"help": "shop",
				"aliases": ['store'],
			},
			"buy": {
				"help": "buy",
				"aliases": ['b'],
				"timeouts": {
					"choose_item": 60
				}
			},
			"inventory": {
				"help": "inventory",
				"aliases": ['inv']
			},
			"balance": {
				"help": "balance",
				"aliases": ['bal']
			},
			"withdraw": {
				"help": "withdraw",
				"aliases": ['with']
			},
			"deposit": {
				"help": "deposit",
				"aliases": ['dep']
			},
			"give": {
				"help": "give",
				"aliases": ['g', 'transfer']
			},
			"leaderboard": {
				"help": "leaderboard",
				"aliases": ['lb']
			},
			"rob": {
				"help": "rob",
				"aliases": ['r', 'steal'],
				"cooldown": 300.0
			},
			"use": {
				"help": "use",
				"aliases": ['u']
			},
			"lock": {
				"help": "lock",
				"aliases": ['l']
			},
			"lockpicker": {
				"help": "lockpicker",
				"aliases": ['lp', 'picker']
			},
			"printer": {
				"help": "printer",
				"aliases": ['ptr', 'print'],
				"timeouts": {
					"get_amount": 60.0
				}
			},
			"mystery package": {
				"help": "mystery package",
				"aliases": ['mystery', 'package', 'mp']
			},
			"blackjack": {
				"help": "blackjack",
				"aliases": ['bj'],
				"cooldown": 150.0
			},
			"work": {
				"help": "work",
				"aliases": ['w'],
				"timeouts": {
					"choose_job": 120.0
				}
			}
		}
		self.help = self.db[name]['help'] if 'help' in self.db[name] else ""
		self.aliases = self.db[name]['aliases'] if 'aliases' in self.db[name] else []
		self.timeouts = self.db[name]['timeouts'] if 'timeouts' in self.db[name] else {}
		self.cooldown = self.db[name]['cooldown'] if 'cooldown' in self.db[name] else 0


class Static:
	def __init__(self):
		self.support_server = "[Support Server](https://discord.gg/JgR6XywMwZ)"
		self.bot = "[Bot](https://top.gg/bot/795099690609279006)"
		self.color_red = "c23b22"
		self.color_green = "03c03c"
		self.color_blurple = "5261f8"
		self.color_gray = "36393f"
		self.color_invisible = "2f3136"
		self.color_default = self.color_invisible
		self.color_white = "F0F0F0"
		self.color_black = "000000"
		self.color_gold = "D4AF37"
		self.error = "[:warning:]:"
		self.cash = ":coin:"
		self.bot_name = "Jerry"
		self.footer = f"{self.bot_name} © 2021"

	def profile(self, user : discord.User): return f"[{user.name}](https://discord.com/users/{user.id})"


class Convert:
	def __init__(self, before):
		self.datetime = datetime.strptime(before, "%Y-%m-%d %H:%M:%S.%f")