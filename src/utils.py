def translate_date(date: str):
	"""
		Funzione per tradurre il mese di una data
		da inglese ad italiano
	"""
	month_translation_dict = {
		'January': 'Gennaio',
		'February': 'Febbraio',
		'March': 'Marzo',
		'April': 'Aprile',
		'May': 'Maggio',
		'June': 'Giugno',
		'July': 'Luglio',
		'August': 'Agosto',
		'September': 'Settembre',
		'October': 'Ottobre',
		'November': 'Novembre',
		'December': 'Dicembre'
	}
	for key in month_translation_dict:
		if key in date:
			return date.replace(key, month_translation_dict[key])
	return None


def translate_status(status: str):
	"""
		Funzione per traduttore lo stato di un utente
		in italiano
	"""
	status_translation_dict = {
		"Dead": "Morto",
		"Retreat": "Ritiro spirituale",
		"Jail": "Prigione",
		"Set aside": "Inattivo",
		"Active": "Attivo"
	}
	for key in status_translation_dict:
		if key in status:
			return status.replace(key, status_translation_dict[key])
	return None
