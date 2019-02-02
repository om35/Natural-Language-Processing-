#!/usr/bin/python3
# M1 informatique
#Projet Traitement Automatique des Langues (TAL2019) - TP04
import sys
import math

def getTableFromFile(path):
	"""Retourne une table de traduction

	la table de traduction est un dictionnaire dont les clés sont les mots en français et les valeurs sont le couple (traduction anglaise, probabilité de la traduction)
	"""
	f = open(path, 'r')
	table = {}
	line = f.readline()
	while line != "":
		splittedLine = line.split()
		if splittedLine[0] in table:
			table[splittedLine[0]].append((splittedLine[1], -(math.log(float(splittedLine[2]), 10))))
		else:
			table[splittedLine[0]] = [(splittedLine[1], -(math.log(float(splittedLine[2]), 10)))]
		line = f.readline()
	return table

def translate_unigrams(words, table_fr_en, probs_unigrams_en, codeToMot_en):
	"""
	Traduction mot à mot

	:param words:
	:param table_fr_en:
	:param probs_unigrams_en:
	:return:
	"""
	translationList = []
	for word in words:
		if word in table_fr_en:
			if word > 0:
				translationScoreMax = float('inf')
				for possible_translation in table_fr_en[word]:
					try:
						translationScore = possible_translation[1] * probs_unigrams_en[possible_translation[0]]
						if translationScore < translationScoreMax:
							translationScoreMax = translationScore
							bestTranslation = possible_translation[0]
					except KeyError:
						continue
				if translationScoreMax == float('inf'):
					bestTranslation = table_fr_en[word][0][0]
				translationList.append(bestTranslation)
			else:
				translationList.append(word)
	return translationList

def translate_digrams(words, table_fr_en, probs_digrams_en, probs_unigrams_en, codeToMot_en={}):
	"""
	Traduction mot à mot

	:param words:
	:param table_fr_en:
	:param probs_unigrams_en:
	:return:
	"""
	translationList = ['START']
	unrecognized_words = {}
	iword = 1
	while iword < len(words) - 1:
		if words[iword] in table_fr_en: # si le mot français est dans la table de traduction
			translationScoreMax = float('inf')
			for possible_translation in table_fr_en[words[iword]]: # pour toutes les traductions possibles de ce mot
				try:
					translationScore = possible_translation[1] * probs_digrams_en[(possible_translation[0], translationList[iword-1])]

					if translationScore < translationScoreMax:
						translationScoreMax = translationScore
						bestTranslation = possible_translation[0]
				except KeyError:
						continue # le digramme est peut-être inconnu

			if translationScoreMax == float('inf'):
				for possible_translation in table_fr_en[words[iword]]:
					try:
						translationScore = possible_translation[1] * probs_unigrams_en[possible_translation[0]]

						if translationScore < translationScoreMax:
							translationScoreMax = translationScore
							bestTranslation = possible_translation[0]
					except KeyError:
						continue # l'unigramme est peut-être inconnu

			if translationScoreMax == float('inf'):
				for possible_translation in table_fr_en[words[iword]]:
					translationScore = possible_translation[1]
					if translationScore < translationScoreMax:
						translationScoreMax = translationScore
						bestTranslation = possible_translation[0]
			translationList.append(bestTranslation)
		else:
			unrecognized_words[-iword] = words[iword]
			translationList.append(-iword)
		iword += 1
	translationList.append('STOP')
	return (translationList, unrecognized_words)

def changeToIdTable(table, codeToMot_fr, codeToMot_en):
	"""modify a word to word translation table to code to code translation table
	"""
	table_translated = {}
	for word in table:
		id_word_fr = getKeyByValue(codeToMot_fr, word.strip())
		if id_word_fr > 0: # le mot français doit être connu
			for possible_translation in table[word]:
				id_word_en = getKeyByValue(codeToMot_en, possible_translation[0].strip()) # le mot anglais doit être connu
				if id_word_en > 0:
					prob_trad = float(possible_translation[1])
					if id_word_fr in table_translated:
						table_translated[id_word_fr].append((id_word_en, prob_trad)) # chaque mot français a une traduction anglaise avec une certaine probabilité
					else:
						table_translated[id_word_fr] = [(id_word_en, prob_trad)]
	return table_translated

def display_translating_table(table):
	"""display the translation table
	"""
	for word in table:
		for possible_translation in table[word]:
			print(str(word) + " -> " + str(possible_translation[0]) + " with probability: " + str(possible_translation[1]))

def getKeyByValue(dictio, searched):
	"""
	return the key of a given value in a dict
	"""
	for key, value in dictio.items():
		if value == searched:
			return key
	return -1

def displayWordsOfCorpus(words_from_corpus, codeToMot1, unknown={}, codeToMot2={}, unrecognized={}):
	for word in words_from_corpus:
		try:
			if word == 'START' or word == 'STOP':
				print(word)
			elif word > 0: # si le mot a trouvé une traduction
				print(str(word) + " -> " + codeToMot1[word])
			elif (word in unknown and unrecognized == {}): # cas de mot inconnu du corpus
				print(str(word) + " -> " + unknown[word])
			elif (word in unrecognized and unrecognized[word] > 0): # si le mot existait en français mais pas en anglais
				print(str(word) + " -> " + codeToMot2[unrecognized[word]])
			elif (word in unrecognized and unrecognized[word] < 0): # si le mot n'existait pas non plus en français
				print(str(word) + " -> " + unknown[unrecognized[word]])
		except KeyError:
			print("Erreur de récupération: " + str(word))
			continue


if __name__ == "__main__":

	help = """traductor.py - Auteur: Mohamed OUERFELLI

  Programme qui prend en entrée une table de traduction français-anglais et une phrase en français (tokenizé+code) puis qui représente la phrase sous la forme d'un treillis où à chaque mot français w_f correspond les mots anglais w_e possibles dans la table de traduction, avec leur probabilité P(w_f|w_e).
  Dans cette version la traduction est la séquence de mots de probabilité maximale utilisant uniquement les probabilités P(w_f|w_e)

Utilisation:

  python3 traductor.py <texte tokenizé path> | --sequence=<sequence>  <table de traduction> <table d'encodage des mots français> <table d'encodage des mots anglais> <unigrammes> <digrammes>[-option]

  Attention: sys.argv est utilisé pour parser les arguments. Les arguments doivent être dans le bon ordre. De plus, les options prenant un argument doivent être utilisées avec le symbole "=" et sans espace.
  La séquence doit être formatée comme [1,2,3] et non pas [1, 2, 3]. (Sinon, utiliser des guillemets)

Options:
  -h                    Affiche ce message d'aide
  -dtrm                 Affiche la table de traduction
  -dtrc                 Affiche la table de traduction
  -dcode                Affiche le code de la séquence avec ses mots suivant une table du code

  --loadunknownsfr=<path> Charge le fichier des mots inconnus français

"""

	possible_flags = ["-h", "-dtrm", "-dtrc", "-dcode"]
	possible_options = ["--loadunknownsfr"]

	if ("-h" in sys.argv or len(sys.argv) < 7):
		exit(help)

	sequencePath = None
	sequence = None
	if len(sys.argv[1].split('=')) == 1:
		sequencePath = sys.argv[1]
	else:
		try:
			sequence = eval(sys.argv[1].split('=')[1])
		except SyntaxError:
			exit("Format de séquence invalide: " + sys.argv[1].split('=')[1])

	translation_table_path = sys.argv[2]
	codeToMot_fr_path = sys.argv[3]
	codeToMot_en_path = sys.argv[4]
	unigrams_en_path = sys.argv[5]
	digrams_en_path = sys.argv[6]

	flags = {}
	if (len(sys.argv) > 7):
		for flag in sys.argv[7:]:
			flag = flag.split('=')
			if flag[0] in possible_flags:
				flags[flag[0]] = True
			elif flag[0] in possible_options:
				try:
					flags[flag[0]] = flag[1]
				except:
					flags[flag[0]] = ""
			else:
				exit("\n\t/_\\ /_\\ /_\\ ERREUR: " + flag[0] + " est inconnu! /_\\ /_\\ /_\\\n\n" + help )

	print("Récupération de la table de traduction:", end = " ")
	table_fr_en = getTableFromFile(translation_table_path)
	if ("-dtrm" in flags):
		display_translating_table(table_fr_en)
	print("Table de traduction récupérée")

	print("Encodage de la table de traduction:", end = " ")
	codeToMot_fr = {}
	try:
		f = open(codeToMot_fr_path, 'r')
		codeToMot_fr = eval(f.read())
		f.close()
	except SyntaxError:
		exit("Le fichier " + codeToMot_fr_path + " est invalide!")
	except FileNotFoundError:
		exit("Le fichier " + codeToMot_fr_path + " est introuvable!")

	codeToMot_en = {}
	try:
		f = open(codeToMot_en_path, 'r')
		codeToMot_en = eval(f.read())
		f.close()
	except SyntaxError:
		exit("Le fichier " + codeToMot_en_path + " est invalide!")
	except FileNotFoundError:
		exit("Le fichier " + codeToMot_en_path + " est introuvable!")

	table_idfr_iden = changeToIdTable(table_fr_en, codeToMot_fr, codeToMot_en)
	if ("-dtrc" in flags):
		display_translating_table(table_idfr_iden)
	print("Encodage de la table de traduction terminé")


	probs_unigram_en = {}
	try:
		f = open(unigrams_en_path, 'r')
		probs_unigram_en = eval(f.read())
		f.close()
	except SyntaxError:
		exit("Le fichier " + unigrams_en_path + " est invalide!")
	except FileNotFoundError:
		exit("Le fichier " + unigrams_en_path + " est introuvable!")

	probs_digram_en = {}
	try:
		f = open(digrams_en_path, 'r')
		probs_digram_en = eval(f.read())
		f.close()
	except SyntaxError:
		exit("Le fichier " + digrams_en_path + " est invalide!")
	except FileNotFoundError:
		exit("Le fichier " + digrams_en_path + " est introuvable!")


	if sequence is None:
		print("Récupération de la séquence à traduire:", end = " ")
		sequence = []
		print("Chargement de la séquence:", end = " ")
		try:
			f = open(sequencePath, 'r')
			try:
				sequence = eval(f.read())
			except:
				exit("Le fichier " + sequencePath + " est invalide et ne peut pas être utilisé comme texte.")
			f.close()
		except FileNotFoundError:
			exit("Le fichier " + sequencePath + " n'existe pas!")
		print("Séquence à traduire récupérée.")

	unknowns_fr = {}
	if ("-dcode" in flags):
		if ("--loadunknownsfr" in flags):
			print("Récupération des mots français inconnus:", end = " ")
			try:
				f = open(flags["--loadunknownsfr"], 'r')
				unknowns_fr = eval(f.read())
				f.close()
				print("Mots français inconnus récupérés")
			except FileNotFoundError:
				exit("Le fichier " + flags["--loadunknownsfr"] + " n'existe pas!")
			print("Décodage de la séquence en français:")
			displayWordsOfCorpus(sequence, codeToMot_fr, unknowns_fr)
			print("Décodage terminé")

		else:
			print("Décodage de la séquence en français:")
			displayWordsOfCorpus(sequence, codeToMot_fr)
			print("Décodage terminé")

	(best_translations, unrecognizeds) = translate_digrams(sequence, table_idfr_iden, probs_digram_en, probs_unigram_en, codeToMot_en)

	if ("-dcode" in flags):
		print("Décodage de la séquence en anglais:")
		displayWordsOfCorpus(best_translations, codeToMot_en, unknowns_fr, codeToMot_fr, unrecognizeds)
		print("Décodage terminé")
