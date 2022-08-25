import aiohttp


async def get_player_sightings(api_url: str, username: str, number_of_sightings: int) -> dict:
	"""
		Restituisce gli ultimi avvistamenti riguardanti il player
		specificato dall'username.

		Parametri:
			-username: nome dell'utente da ricercare
			-number_of_sightings: numero di avvistamenti da ricercare
	"""
	url = f'{api_url}/player/{username}/position/{number_of_sightings}'
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as res:
			if res.status == 200:
				return await res.json()
			if res.status == 404:
				raise KeyError
			else:
				raise Exception(res.status)


async def get_player_stats(api_url: str, username: str) -> dict:
	"""
	Restituisce le statistiche dell'utente specificato.
	"""
	url = f'{api_url}/player/{username}/stats'
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as res:
			if res.status == 200:
				return await res.json()
			if res.status == 404:
				raise KeyError
			else:
				raise Exception(res.status)


async def get_player_img(api_url: str, username: str) -> dict:
	"""
	Restituisce l'immagine profilo del personaggio
	specificato come parametro.
	"""
	url = f'{api_url}/player/{username}/img'
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as res:
			if res.status == 200:
				return await res.text()
			if res.status == 404:
				raise KeyError
			else:
				raise Exception(res.status)
