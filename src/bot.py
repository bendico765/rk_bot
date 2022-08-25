import os
import discord
import asyncio
import json
import rk_api
import utils

from io import BytesIO
from base64 import b64decode
from discord.ext import commands
from dotenv import load_dotenv

# caricamento delle variabili di ambiente
load_dotenv()
API_URL = os.getenv('API_URL')
TOKEN = os.getenv('DISCORD_TOKEN')
HELP_FILE_PATH = os.getenv('HELP_FILE_PATH')
# ERROR_LOGFILE_PATH = os.getenv('ERROR_LOGFILE_PATH')

command_prefix = '.'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=command_prefix, help_command=None, intents=intents)


# EVENTS
@bot.event
async def on_ready():
	global help_dictionary  # dizionario di help
	with open(HELP_FILE_PATH) as file:
		help_dictionary = json.load(file)
	await bot.change_presence(activity=discord.Game(name=f'{command_prefix}help'))
	print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_error(event, *args, **kwargs):
	"""
	line = "="*10
	with open(ERROR_LOGFILE_PATH, 'a') as f:
		f.write(line)
		f.write('\n')
		print(event)
		print(args)
		print(kwargs)
		f.write(f'Errore: {args[0]}\n')
		f.write(line)
		f.write('\n')
	if event == 'on_message':
		f.write(f'Unhandled message: {args[0]}\n')
	else:
		raise
	"""


# COMMANDS
@bot.command(name='help')
async def help(ctx, command: str = None):
	if command is None:  # menu generico
		embedded_message = discord.Embed(title='Help')
		for commandName in help_dictionary:
			embedded_message.add_field(
				name=f"{command_prefix}{commandName}",
				value=help_dictionary[commandName]["brief"],
				inline=False
			)
		embedded_message.set_thumbnail(url=bot.user.avatar_url)
		footer_text = f"Usare {command_prefix}help nome_comando per avere una descrizione più accurata di un comando.\nBot proprietà del Casato De Leyva."
		embedded_message.set_footer(text=footer_text)
		await ctx.send(embed=embedded_message)
	else:  # stampa il menu di un comando specifico
		# tollero anche il caso in cui qualcuno scriva un
		# comando preceduto dal prefisso
		if command[0] == command_prefix:
			command = command[1:]  # rimuovo il prefisso
		if command not in help_dictionary:
			await ctx.channel.send("Non esiste alcuna voce associata a questo comando")
			return
		if 'help' not in help_dictionary[command]:
			await ctx.channel.send("Il comando non dispone di una descrizione più approfondita")
			return
		signature = None
		for commandEntry in bot.commands:
			if commandEntry.name == command:
				signature = commandEntry.signature
				break
		embedded_message = discord.Embed(
			title=f"{command_prefix}{command} {signature}",
			description=help_dictionary[command]['help'])
		await ctx.channel.send(embed=embedded_message)


@help.error
async def helpErrorHandler(ctx, error):
	await ctx.channel.send("Si è verificato un errore durante il caricamento del menu di aiuto")


@bot.command(name='profilo')
async def profilo(ctx, username: str = None):
	"""
		!profilo username

		Reperisce le statistiche e l'immagine profilo
		del pg associato all'username.
	"""
	if username is None:
		await ctx.channel.send("Specificare l'username")
		return
	stats_list, canvas_img_str = await asyncio.gather(
		rk_api.get_player_stats(API_URL, username),
		rk_api.get_player_img(API_URL, username)
	)
	# traduzione in italiano di alcune voci
	translated_date = utils.translate_date(stats_list["last_connection"])
	translated_status = utils.translate_status(stats_list["status"])
	# parametri del messaggio embed
	description = """
	Clan: {0[clan_name]}
	Status: {1}
	Livello: {0[level]}
	Carisma: {0[charism]}
	Forza: {0[strenght]}
	Reputazione: {0[reputation]}
	Intelligenza: {0[intelligence]}
	Residenza: {0[residency]}
	\n
	Sponsor: {0[sponsor]}
	Sposo/a: {0[married]}
	Ultime persona ad avergli dato la fiducia: {2}
	Dichiarati: {3}
	""".format(
		stats_list,
		translated_status,
		", ".join(stats_list["trusted_by_users"]),
		", ".join(stats_list["declared_users"])
	)
	description = description.replace('\t', '').replace('_', '\_')
	footer_text = f"Ultima connessione: {translated_date}"
	# creazione del messaggio embed
	embedded_message = discord.Embed(
		title=stats_list["complete_name"],
		url=stats_list["profile_link"],
		description=description
	)
	embedded_message.set_thumbnail(url=stats_list["blason_image"])
	embedded_message.set_footer(text=footer_text)
	# aggiunta dell'immagine profilo
	canvas_img = b64decode(canvas_img_str)
	file_img = discord.File(BytesIO(canvas_img), filename="canvas.png")
	embedded_message.set_image(url="attachment://canvas.png")
	await ctx.channel.send(embed=embedded_message, file=file_img)


@profilo.error
async def profilo_error_handler(ctx, error):
	if isinstance(error.original, KeyError):  # pg inesistente
		await ctx.channel.send('Il giocatore cercato non esiste')
		return
	await ctx.channel.send("Si è verificato un errore durante il caricamento delle informazioni")


@bot.command(name='posizione')
async def posizione(ctx, username: str, number_of_sightings: int = 1):
	"""
		!posizione username [numero_avvistamenti]

		Reperisce gli ultimi avvistamenti associati all'username.
	"""
	# controllo validità parametri
	if username is None:
		raise discord.ext.commands.BadArgument
	if number_of_sightings <= 0:
		await ctx.channel.send("Numero non valido, cerco l'ultimo avvistamento registrato.")
		number_of_sightings = 1
	# richiesta API
	username = username[0].capitalize() + username[1:]  # viene capitalizzata la prima lettera dell'username
	result = await rk_api.get_player_sightings(API_URL, username, number_of_sightings)
	# invio messaggio risposta
	profile_link = result["profile_link"]
	sighting_list = result["sighting_list"]
	if sighting_list == []:
		await ctx.channel.send("Non esistono avvistamenti registrati")
		return
	# creazione del messaggio embed
	embedded_message = discord.Embed(
		title=username,
		url=profile_link
	)
	# aggiunta dei campi con le posizioni
	for sightData in sighting_list:
		string = "{0[town]}, {0[province]}, {0[kingdom]}".format(sightData)
		embedded_message.add_field(name=sightData["date"], value=string, inline=False)
	embedded_message.set_footer(
		text="Le informazioni mostate da questo comando sono prelevate da un tool esterno e potrebbero essere inesatte o incomplete.")
	await ctx.channel.send(embed=embedded_message)


@posizione.error
async def posizione_error_handler(ctx, error):
	if isinstance(error, discord.ext.commands.BadArgument):  # parametri invalidi
		await ctx.channel.send("Parametri invalidi")
		return
	if isinstance(error.original, KeyError):  # pg inesistente
		await ctx.channel.send(
			"Non ho trovato nessuna informazione legata a questo username (attenzione alle maiuscole/minuscole)")
		return
	await ctx.channel.send("Si è verificato un errore durante il caricamento delle informazioni")


bot.run(TOKEN)
