import random as rand
from fuzzywuzzy import fuzz
import discord
import random
import csv
import os
from dotenv import load_dotenv

os.chdir(os.getcwd())


def strip_str(text):		#function to remove punctuations, spaces from string and make it lowercase,
	punctuations = ''' !-;:`'".,/_?'''
	text2 = ""
	for char in text.lower():
		if char not in punctuations:
			text2 = text2 + char
	return text2

class QuizObj():
	def __init__(self, question, questionType, answers, answerType, secondaryAnswers = [], questionImage = None):
		self.question = question
		#1 : regular question | 2 : image question
		self.questionType = questionType
		if self.questionType == 2:
			self.questionImage = discord.File(f"./questionbank/quizimages/{questionImage}")
		self.answers = answers
		#1 : one correct | 2 : one correct with multiple types | 3 : many correct
		self.answerType = answerType
		if self.answerType != 1:
			self.secondaryAnswers = secondaryAnswers

	def get_question(self):
		if self.questionType == 1:
			return self.question
		return (self.question, self.questionImage)

	def get_answer(self):
		if self.answerType == 1:
			return self.answers
		return rand.choice(self.answers)

	def check_answer(self, answ, hasMKB):
		striptext = strip_str(answ)	#first we use strip_str on both strings which removes spaces, "the" and unwanted symbols
		if self.answerType == 1:
			stripanswer = strip_str(self.answers)
			ratio = fuzz.ratio(striptext, stripanswer)
		else:				#if there are multiple answers we pick out the answer that is most similar to the input
			stripanswers = [strip_str(x) for x in self.answers+self.secondaryAnswers]
			ratios = []
			for i in stripanswers:			#fill a list with levenshtein ratios
				ratios.append(fuzz.ratio(striptext, i))
			ratio = max(ratios)				#take the max value, its index and the actual string by the index
		return ratio > (86 + 11*hasMKB) #if user has monkey king bar they get away with more mistakes

	#Function to calculate time for each question according to its size(for blitz)
	def get_time(self):
		queslen = len(self.question)
		if self.answerType == 1:			#takes the length of the raw answer
			answlen = len(self.answers)
		else:				#takes the average length of all answers
			allanswers = self.answers + self.secondaryAnswers
			answlen = sum(map(len, allanswers))/len(allanswers)
		seconds = queslen/12 + answlen/5
		return seconds


questlist = []

#question, questionType, answers, answerType, secondaryAnswers = [], questionImage = None
with open("./questionbank/quizquestions.tsv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
    	answertype = int(row['AnswerTypeId'])
    	if answertype == 1:
    		answer = row['Answer']
    	else:
    		answer = row['Answer'].split(', ')

    	questlist.append(QuizObj(row['Question'], int(row['QuestionTypeId']), answer, answertype, row['SecondaryAnswers'].split(', '), row['QuestionImage']))


class ScrambleObj():
	def __init__(self, word):
		self.word = word
		self.value = min(12, len(word))*8

	def get_word(self):
		return self.word

	def get_scramble(self):
		scrambledworde = []			#empty list to .join() emojies onto
		charlist = list(self.word.lower().replace("'", ""))			#converting string to list
		for char in random.sample(charlist, len(charlist)):		#shuffling the word list and looping through it
			scrambledworde.append(charemojies[char])		#picking up values of charemojies of the lowercase characters
		output = " ".join(scrambledworde)					#joining them to form a string of all emojies to output
		return output

	def check_answer(self, answ, hasMKB):
		striptext = strip_str(answ)	#first we use strip_str on both strings which removes spaces, "the" and unwanted symbols
		stripanswer = strip_str(self.word)
		ratio = fuzz.ratio(striptext, stripanswer)
		#if user has monkey king bar they get away with more mistakes
		return ratio > (86 + 11*hasMKB)

#The list of words to scramble using 322 scramble
scrambleheroes = [
    'Abaddon', 'Alchemist', 'Axe', 'Beastmaster', 'Brewmaster', 'Bristleback', 'Centaur Warrunner', 'Chaos Knight', 'Clockwerk', 'Doom', 'Dragon Knight',
    'Earth Spirit', 'Earthshaker', 'Elder Titan', 'Huskar', 'Io', 'Kunkka', 'Legion Commander', 'Lifestealer', 'Lycan', 'Magnus', 'Mars', 'Night Stalker',
    'Omniknight', 'Phoenix', 'Pudge', 'Sand King', 'Slardar', 'Snapfire', 'Spirit Breaker', 'Sven', 'Tidehunter', 'Timbersaw', 'Tiny', 'Treant Protector',
    'Tusk', 'Underlord', 'Undying', 'Wraith King', 'Anti Mage', 'Arc Warden', 'Bloodseeker', 'Bounty Hunter', 'Broodmother', 'Clinkz', 'Drow Ranger',
    'Ember Spirit', 'Faceless Void', 'Gyrocopter', 'Juggernaut', 'Lone Druid', 'Luna', 'Medusa', 'Meepo', 'Mirana', 'Monkey King', 'Morphling', 'Naga Siren',
    'Nyx Assassin', 'Pangolier', 'Phantom Assassin', 'Phantom Lancer', 'Razor', 'Riki', 'Shadow Fiend', 'Slark', 'Sniper', 'Spectre', 'Templar Assassin',
    'Terrorblade', 'Troll Warlord', 'Ursa', 'Vengeful Spirit', 'Venomancer', 'Viper', 'Weaver', 'Ancient Apparition', 'Bane', 'Batrider', 'Chen',
    'Crystal Maiden', 'Dark Seer', 'Dark Willow', 'Dazzle', 'Death Prophet', 'Disruptor', 'Enchantress', 'Enigma', 'Grimstroke', 'Invoker', 'Jakiro',
    'Keeper of the Light', 'Leshrac', 'Lich', 'Lina', 'Lion', "Nature's Prophet", 'Necrophos', 'Ogre Magi', 'Oracle', 'Outworld Destroyer', 'Puck', 'Pugna',
    'Queen of Pain', 'Rubick', 'Shadow Demon', 'Shadow Shaman', 'Silencer', 'Skywrath Mage', 'Storm Spirit', 'Techies', 'Tinker', 'Visage', 'Void Spirit',
    'Warlock', 'Windranger', 'Winter Wyvern', 'Witch Doctor', 'Zeus', 'Hoodwink', 'Dawnbreaker', 'Marci', 'Primal Beast', 'Muerta', 'Kez', 'Ringmaster'
]

scramblelist = []
for name in scrambleheroes:
    scramblelist.append(ScrambleObj(name))

alphabet = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')
#The dictioanry to call emojies, only used for 322 scramble for now
charemojies = {'a': ':regional_indicator_a:', 'b': ':regional_indicator_b:', 'c': ':regional_indicator_c:', 'd': ':regional_indicator_d:', 'e': ':regional_indicator_e:', 'f': ':regional_indicator_f:', 'g': ':regional_indicator_g:', 'h': ':regional_indicator_h:', 'i': ':regional_indicator_i:', 'j':
':regional_indicator_j:', 'k': ':regional_indicator_k:', 'l': ':regional_indicator_l:', 'm': ':regional_indicator_m:', 'n': ':regional_indicator_n:', 'o': ':regional_indicator_o:', 'p': ':regional_indicator_p:', 'q': ':regional_indicator_q:', 'r': ':regional_indicator_r:', 's': ':regional_indicator_s:',
't': ':regional_indicator_t:', 'u': ':regional_indicator_u:', 'v': ':regional_indicator_v:', 'w': ':regional_indicator_w:', 'x': ':regional_indicator_x:', 'y': ':regional_indicator_y:', 'z': ':regional_indicator_z:', ' ': ':blue_square:'}

class ShopItem:
	def __init__(self, name, image, items, hasRecipe=0):
		self.name = name
		self.image = image
		self.items = items
		self.hasRecipe = hasRecipe

		try:
			self.itemimage = discord.File(f"./questionbank/shopkeepimages/{self.image}", filename=self.image)
		except Exception as e:
			self.image = None
			print(image)

		self.shuffled = []

	def get_answer(self): #creates a highlighted string of correct items
		items = "``, ``".join(self.items)
		if self.hasRecipe:
			items += " and a Recipe"
		return items

	def create_embed(self):
		itemembed = discord.Embed(title=f"Assemble {self.name}:", colour=0x9b59b6)
		itemembed.set_thumbnail(url=f"attachment://{self.image}")
		possibleansws = self.items.copy()		#all the possible answers, starts with the correct ones
		while len(possibleansws) < 11:		#adds random items
			possibleansws.append(random.choice(ingredients))
		self.shuffled = random.sample(possibleansws, k=11)		#shuffled list of random and correct items
		self.shuffled.append("Recipe")
		result = ""		#result to display with proper spacing and all
		for i in range(12):
			result += f"**{alphabet[i]})** {self.shuffled[i]}"
			if i%2:
				result += "\n"
			else:
				result += " **||** "
		itemembed.add_field(name="Possible answers:", value=result+"*Type in the letters of the items you consider correct.*", inline=True)

		return self.itemimage, itemembed

	def check_answer(self, answ):
		answ = strip_str(answ).upper()
		itemstoremove = self.items.copy()
		if self.hasRecipe:
			if alphabet[11] not in answ:
				return False
			itemstoremove.append("Recipe")
		for letter in answ:
			try:
				letterindex = alphabet.index(letter)
				itemstoremove.remove(self.shuffled[letterindex])
			except ValueError:
				return False
		return not itemstoremove


shopkeeplist = []

#All the items that are used in at least one recipe.
ingredients = []

#itemname, image, ingredients, hasRecipe
with open("./questionbank/shopquizquestions.tsv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
	    ingreds = row['Ingredients'].split(', ')

	    shopkeeplist.append(ShopItem(row['ItemName'], row['ItemImage'], ingreds, row['HasRecipe']))

	    #Filling the list of all possible ingredients
	    for ing in ingreds:
    		if ing not in ingredients:
    			ingredients.append(ing)

class IconObj:
	def __init__(self, image, answer, answerType = 1, secondaryAnswers = []):
		try:
			self.image = discord.File(f"./questionbank/iconquizimages/{image}")
		except Exception as e:
			self.image = None
			print(image)
		self.answer = answer
		#1 : one correct | 2 : one correct with multiple types
		self.answerType = answerType
		if self.answerType != 1:
			self.secondaryAnswers = secondaryAnswers

	def get_image(self):
		return self.image

	def get_answer(self):
		return self.answer

	def check_answer(self, answ, hasMKB):
		striptext = strip_str(answ)	#first we use strip_str on both strings which removes spaces, "the" and unwanted symbols
		if self.answerType == 1:
			stripanswer = strip_str(self.answer)
			ratio = fuzz.ratio(striptext, stripanswer)
		else:				#if there are multiple answers we pick out the answer that is most similar to the input
			allanswers = self.secondaryAnswers
			allanswers.append(self.answer)
			stripanswers = [strip_str(x) for x in allanswers]
			ratios = []
			for i in stripanswers:			#fill a list with levenshtein ratios
				ratios.append(fuzz.ratio(striptext, i))
			ratio = max(ratios)				#take the max value, its index and the actual string by the index
		return ratio > (86 + 11*hasMKB) #if user has monkey king bar they get away with more mistakes


iconquizlist = []

#Just the names
iconnames = []

#image, answer, answerType, secondaryAnswers
with open("./questionbank/iconquizquestions.tsv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
	    iconquizlist.append(IconObj(row['IconImage'], row['Answer'], int(row['AnswerTypeId']), row['SecondaryAnswers'].split(', ')))

	    #Filling the list of all icon names
	    iconnames.append(row['Answer'])

#The dictionary of item and spell sound effects, some abilities and spells can be named in multiple different ways which are put in tuples, some sound effects can be linked to multiple spells or items so they're put in lists
# audioquizdict = {'Abyssal_Blade.mp3.mpeg': ('Abyssal Blade', "superbasher"), 'Adaptive_Strike.mp3.mpeg': 'Adaptive Strike', 'Aeon_Disk.mp3.mpeg': 'Aeon Disk', 'Aether_Remnant.mpeg': 'Aether Remnant.mpeg', 'Alacrity.mp3.mpeg': 'Alacrity', 'Amplify_Damage.mp3.mpeg': ("Corrosive Haze", 'amplify damage'),
# 'Anchor_Smash.mp3.mpeg': 'Anchor Smash', 'Ancient_Seal.mp3.mpeg': 'Ancient Seal', 'Aphotic_Shield.mp3.mpeg': 'Aphotic Shield', 'Arcane_Bolt.mp3.mpeg': 'Arcane Bolt', 'Arcane_Orb.mp3.mpeg': 'Arcane Orb', 'Arctic_Burn.mp3.mpeg': 'Arctic Burn', 'Arc_Lightning.mp3.mpeg': 'Arc Lightning',
# 'Arena_of_Blood.mp3.mpeg': 'Arena of Blood', 'Assassinate.mp3.mpeg': 'Assassinate', 'Astral_Imprisonment.mp3.mpeg': 'Astral Imprisonment', 'Avalanche.mp3.mpeg': 'Avalanche', 'Ball_Lightning.mp3.mpeg': 'Ball Lightning', 'Battery_Assault.mp3.mpeg': 'Battery Assault',
# 'Battle_Hunger.mp3.mpeg': 'Battle Hunger', 'Battle_Trance.mp3.mpeg': 'Battle Trance', 'Bedlam.mp3.mpeg': 'Bedlam', 'Black_Hole.mp3.mpeg': 'Black Hole', 'Black_King_Bar.mp3.mpeg': ('Black King Bar', "bkb"), 'Blade_Fury.mp3.mpeg': 'Blade Fury', 'Blade_Mail.mp3.mpeg': 'Blade Mail',
# 'Blast_Off!.mp3.mpeg': 'Blast Off!', 'Blinding_Light.mp3.mpeg': 'Blinding Light', 'Blink_Dagger.mp3.mpeg': ['Blink Dagger', "Blink", "Flicker"], 'Blink_Strike.mp3.mpeg': 'Blink Strike', 'Bloodlust.mp3.mpeg': 'Bloodlust', 'Bloodrage.mp3.mpeg': 'Bloodrage', 'Blood_Rite.mp3.mpeg': 'Blood Rite',
# 'Borrowed_Time.mp3.mpeg': 'Borrowed Time', 'Boundless_Strike.mp3.mpeg': 'Boundless Strike', 'Brain_Sap.mp3.mpeg': 'Brain Sap', 'Bramble_Maze.mp3.mpeg': 'Bramble Maze', 'Breathe_Fire.mp3.mpeg': 'Breathe Fire', 'Burning_Spear.mp3.mpeg': 'Burning Spear', 'Burrow.mp3.mpeg': 'Burrow',
# 'Burrowstrike.mp3.mpeg': 'Burrowstrike', 'Call_Down.mp3.mpeg': 'Call Down', 'Call_of_the_Wild_Boar.mp3.mpeg': 'Call of the Wild Boar', 'Call_of_the_Wild_Hawk.mp3.mpeg': 'Call of the Wild Hawk', 'Caustic_Finale.mp3.mpeg': 'Caustic Finale', 'Chain_Frost.mp3.mpeg': 'Chain Frost',
# 'Chakram.mp3.mpeg': 'Chakram', 'Chakra_Magic.mp3.mpeg': 'Chakra Magic', 'Chaos_Bolt.mp3.mpeg': 'Chaos Bolt', 'Chaos_Meteor.mp3.mpeg': ('Chaos Meteor', "meatball"), 'Chaotic_Offering.mp3.mpeg': 'Chaotic Offering', 'Charge_of_Darkness.mp3.mpeg': 'Charge of Darkness', 'Cheese.mp3.mpeg': 'Cheese',
# 'Chemical_Rage.mp3.mpeg': 'Chemical Rage', 'Chilling_Touch.mp3.mpeg': 'Chilling Touch', 'Chronosphere.mp3.mpeg': 'Chronosphere', 'Cold_Embrace.mp3.mpeg': 'Cold Embrace', 'Cold_Feet.mp3.mpeg': 'Cold Feet', 'Cold_Snap.mp3.mpeg': 'Cold Snap', 'Concussive_Shot.mp3.mpeg': 'Concussive Shot',
# 'Counter_Helix.mp3.mpeg': 'Counter Helix', 'Coup_de_Grace.mp3.mpeg': 'Coup de Grace', 'Crimson_Guard.mp3.mpeg': 'Crimson Guard', 'Crippling_Fear.mp3.mpeg': 'Crippling Fear', 'Crypt_Swarm.mp3.mpeg': 'Crypt Swarm', 'Crystal_Nova.mp3.mpeg': 'Crystal Nova', 'Culling_Blade.mp3.mpeg': 'Culling Blade',
# 'Dagon.mp3.mpeg': 'Dagon', 'Darkness.mp3.mpeg': 'Darkness', 'Dark_Pact.mp3.mpeg': 'Dark Pact', 'Dark_Rift.mp3.mpeg': 'Dark Rift', 'Deafening_Blast.mp3.mpeg': 'Deafening Blast', 'Death_Pact.mp3.mpeg': 'Death Pact', 'Death_Pulse.mp3.mpeg': 'Death Pulse', 'Death_Ward.mp3.mpeg': 'Death Ward',
# 'Decay.mp3.mpeg': 'Decay', 'Demonic_Conversion.mp3.mpeg': 'Demonic Conversion', 'Demonic_Purge.mp3.mpeg': 'Demonic Purge', 'Devour.mp3.mpeg': 'Devour', 'Diffusal_Blade.mp3.mpeg': ('Diffusal Blade', "diffusal"), 'Dismember.mp3.mpeg': 'Dismember', 'Disruption.mp3.mpeg': 'Disruption', 'Doom.mp3.mpeg': 'Doom',
# 'Doppelganger.mp3.mpeg': 'Doppelganger', 'Double_Edge.mp3.mpeg': 'Double Edge', 'Dragon_Slave.mp3.mpeg': 'Dragon Slave', 'Dragon_Tail.mp3.mpeg': 'Dragon Tail', 'Dream_Coil.mp3.mpeg': 'Dream Coil', 'Drum_of_Endurance.mp3.mpeg': ('Drum of Endurance', "drums"), 'Drunken_Haze.mp3.mpeg': 'Drunken Haze',
# 'Dual_Breath.mp3.mpeg': 'Dual Breath', 'Duel.mp3.mpeg': 'Duel', 'Earthbind.mp3.mpeg': 'Earthbind', 'Earthshock.mp3.mpeg': 'Earthshock', 'Earth_Spike.mp3.mpeg': 'Earth Spike', 'Earth_Splitter.mp3.mpeg': 'Earth Splitter', 'Echo_Slam.mp3.mpeg': ('Echo Slam', "chaos dunk"), 'Echo_Stomp.mp3.mpeg': 'Echo Stomp',
# 'Elder_Dragon_Form.mp3.mpeg': 'Elder Dragon Form', 'Electric_Vortex.mp3.mpeg': 'Electric Vortex', 'EMP.mp3.mpeg': 'EMP', 'Empower.mp3.mpeg': 'Empower', 'Enchant.mp3.mpeg': 'Enchant', 'Enchant_Totem.mp3.mpeg': 'Enchant Totem', 'Enrage.mp3.mpeg': 'Enrage', 'Ensnare.mp3.mpeg': 'Ensnare',
# 'Epicenter.mp3.mpeg': 'Epicenter', 'Ethereal_Blade.mp3.mpeg': ('Ethereal Blade', "eblade", "ethereal"), 'Ethereal_Jaunt.mp3.mpeg': 'Ethereal Jaunt', 'Ether_Shock.mp3.mpeg': 'Ether Shock', "Eul's_Scepter_of_Divinity.mp3.mpeg": ("Eul's Scepter of Divinity", "euls"), 'Exorcism.mp3.mpeg': 'Exorcism',
# 'Eye_of_the_Storm.mp3.mpeg': 'Eye of the Storm', 'Fade_Bolt.mp3.mpeg': 'Fade Bolt', 'Faerie_Fire.mp3.mpeg': 'Faerie Fire', 'False_Promise.mp3.mpeg': 'False Promise', 'Fatal_Bonds.mp3.mpeg': 'Fatal Bonds', "Fate's_Edict.mp3.mpeg": "Fate's Edict", 'Finger_of_Death.mp3.mpeg': ('Finger of Death', "finger"),
# 'Fireblast.mp3.mpeg': 'Fireblast', 'Firestorm.mp3.mpeg': 'Firestorm', 'Fissure.mp3.mpeg': 'Fissure', 'Flak_Cannon.mp3.mpeg': 'Flak Cannon', 'Flamebreak.mp3.mpeg': 'Flamebreak', 'Flame_Guard.mp3.mpeg': 'Flame Guard', 'Flaming_Lasso.mp3.mpeg': 'Flaming Lasso', 'Flesh_Golem.mp3.mpeg': 'Flesh Golem',
# 'Flux.mp3.mpeg': 'Flux', 'Focus_Fire.mp3.mpeg': 'Focus Fire', 'Force_Staff.mp3.mpeg': 'Force Staff', 'Forge_Spirit.mp3.mpeg': 'Forge Spirit', "Fortune's_End.mp3.mpeg": "Fortune's End", 'Frostbite.mp3.mpeg': 'Frostbite', 'Frost_Blast.mp3.mpeg': 'Frost Blast', 'Ghost_Ship.mp3.mpeg': 'Ghost Ship',
# 'Ghost_Shroud.mp3.mpeg': 'Ghost Shroud', 'Glaives_of_Wisdom.mp3.mpeg': 'Glaives of Wisdom', 'Glimmer_Cape.mp3.mpeg': ('Glimmer Cape', "glimmer"), 'Glimpse.mp3.mpeg': 'Glimpse', 'Global_Silence.mp3.mpeg': 'Global Silence', "God's_Rebuke.mpeg": "God's Rebuke", "God's_Strength.mp3.mpeg": "God's Strength",
# 'Grave_Chill.mp3.mpeg': 'Grave Chill', 'Greater_Bash.mp3.mpeg': 'Greater Bash', 'Guardian_Angel.mp3.mpeg': 'Guardian Angel', 'Guardian_Greaves.mp3.mpeg': ('Guardian Greaves', "greaves"), 'Gush.mp3.mpeg': 'Gush', 'Gust.mpeg': 'Gust', 'Hand_of_Midas.mp3.mpeg': ('Hand of Midas', "midas"), 'Haunt.mp3.mpeg': 'Haunt',
# 'Heat-Seeking_Missile.mp3.mpeg': 'Heat-Seeking Missile', "Heaven's_Halberd.mp3.mpeg": ("Heaven's Halberd", "halberd"), 'Hex_(Lion).mp3.mpeg': 'Hex', 'Hex_(Shadow_Shaman).mp3.mpeg': 'Hex', 'Holy_Persuasion.mp3.mpeg': 'Holy Persuasion', 'Hoof_Stomp.mp3.mpeg': 'Hoof Stomp', 'Hookshot.mp3.mpeg': 'Hookshot',
# 'Howl.mp3.mpeg': 'Howl', 'Hurricane_Pike.mp3.mpeg': 'Hurricane Pike', 'Icarus_Dive.mp3.mpeg': 'Icarus Dive', 'Ice_Armor.mp3.mpeg': 'Ice Armor', 'Ice_Blast.mp3.mpeg': 'Ice Blast', 'Ice_Path.mp3.mpeg': 'Ice Path', 'Ice_Shards.mp3.mpeg': 'Ice Shards', 'Ignite.mp3.mpeg': 'Ignite',
# 'Illuminate.mp3.mpeg': 'Illuminate', 'Illusory_Orb.mp3.mpeg': 'Illusory Orb', 'Impale.mp3.mpeg': 'Impale', 'Impetus.mp3.mpeg': 'Impetus', 'Infest.mp3.mpeg': 'Infest', 'Infused_Raindrop.mp3.mpeg': 'Infused Raindrop', 'Ink_Swell.mp3.mpeg': 'Ink Swell', 'Insatiable_Hunger.mp3.mpeg': 'Insatiable Hunger',
# 'Invoke.mp3.mpeg': 'Invoke', 'Ion_Shell.mp3.mpeg': 'Ion Shell', 'Iron_Talon.mp3.mpeg': 'Iron Talon', 'Kinetic_Field.mp3.mpeg': 'Kinetic Field', 'Laguna_Blade.mp3.mpeg': ('Laguna Blade', "laguna"), 'Land_Mines.mp3.mpeg': 'Land Mines', 'Laser.mp3.mpeg': 'Laser', 'Last_Word.mp3.mpeg': 'Last Word', 'Leap.mp3.mpeg': 'Leap',
# 'Leech_Seed.mp3.mpeg': 'Leech Seed', 'Life_Break.mp3.mpeg': 'Life Break', 'Life_Drain.mp3.mpeg': 'Life Drain', 'Lightning_Bolt.mp3.mpeg': 'Lightning Bolt', 'Lightning_Storm.mp3.mpeg': 'Lightning Storm', 'Light_Strike_Array.mp3.mpeg': 'Light Strike Array', "Lil'_Shredder.mp3.mpeg": "Lil' Shredder",
# 'Liquid_Fire.mp3.mpeg': 'Liquid Fire', 'Living_Armor.mp3.mpeg': 'Living Armor', 'Lotus_Orb.mp3.mpeg': 'Lotus Orb', 'Lucent_Beam.mp3.mpeg': 'Lucent Beam', 'Macropyre.mp3.mpeg': 'Macropyre', 'Magic_Missile.mp3.mpeg': 'Magic Missile', 'Magnetic_Field.mp3.mpeg': 'Magnetic Field',
# 'Magnetize.mp3.mpeg': 'Magnetize', 'Maledict.mp3.mpeg': 'Maledict', 'Malefice.mp3.mpeg': 'Malefice', 'Mana_Break.mp3.mpeg': 'Mana Break', 'Mana_Burn.mp3.mpeg': 'Mana Burn', 'Mana_Drain.mp3.mpeg': 'Mana Drain', 'Mana_Void.mp3.mpeg': 'Mana Void', 'Manta_Style.mp3.mpeg': ('Manta Style', "manta"),
# 'Mask_of_Madness.mp3.mpeg': 'Mask of Madness', 'Mass_Serpent_Ward.mp3.mpeg': 'Mass Serpent Ward', 'Meat_Hook.mp3.mpeg': 'Meat Hook', 'Medallion_of_Courage.mp3.mpeg': ('Medallion of Courage', "medallion"), 'Meld.mp3.mpeg': 'Meld',
# 'Meteor_Hammer.mp3.mpeg': ['Meteor Hammer', "meme hammer", "Fallen Sky"], 'Mirror_Image.mp3.mpeg': 'Mirror Image', 'Mist_Coil.mp3.mpeg': 'Mist Coil', 'Moonlight_Shadow.mp3.mpeg': 'Moonlight Shadow', 'Moon_Shard.mp3.mpeg': 'Moon Shard', 'Mystic_Flare.mp3.mpeg': 'Mystic Flare', 'Mystic_Snake.mp3.mpeg': 'Mystic Snake',
# "Nature's_Call.mp3.mpeg": "Nature's Call", 'Necronomicon.mp3.mpeg': ('Book of the Dead', 'Necronomicon', "necrobook"), 'Nethertoxin.mp3.mpeg': 'Nethertoxin', 'Nether_Blast.mp3.mpeg': 'Nether Blast', 'Nether_Strike.mp3.mpeg': 'Nether Strike', 'Nether_Swap.mp3.mpeg': 'Nether Swap', 'Nether_Ward.mp3.mpeg': 'Nether Ward',
# 'Nightmare.mp3.mpeg': 'Nightmare', 'Nullifier.mp3.mpeg': 'Nullifier', 'Omnislash.mp3.mpeg': 'Omnislash', 'Open_Wounds.mp3.mpeg': 'Open Wounds', 'Orchid_Malevolence.mp3.mpeg': ('Orchid Malevolence', "orchid"), 'Overgrowth.mp3.mpeg': 'Overgrowth', 'Overpower.mp3.mpeg': 'Overpower',
# 'Overwhelming_Odds.mp3.mpeg': 'Overwhelming Odds', 'Paralyzing_Cask.mp3.mpeg': 'Paralyzing Cask', 'Penitence.mp3.mpeg': 'Penitence', 'Phantasm.mp3.mpeg': 'Phantasm', 'Phase_Shift.mp3.mpeg': 'Phase Shift', 'Pit_of_Malice.mp3.mpeg': 'Pit of Malice', 'Plague_Ward.mp3.mpeg': 'Plague Ward',
# 'Plasma_Field.mp3.mpeg': 'Plasma Field', 'Poison_Nova.mp3.mpeg': 'Poison Nova', 'Poison_Touch.mp3.mpeg': 'Poison Touch', 'Poof.mp3.mpeg': 'Poof', 'Pounce.mp3.mpeg': 'Pounce', 'Powershot.mp3.mpeg': 'Powershot', 'Power_Cogs.mp3.mpeg': 'Power Cogs', 'Press_the_Attack.mp3.mpeg': 'Press the Attack',
# 'Primal_Roar.mp3.mpeg': 'Primal Roar', 'Primal_Split.mp3.mpeg': 'Primal Split', 'Primal_Spring.mp3.mpeg': 'Primal Spring', 'Psionic_Trap.mp3.mpeg': 'Psionic Trap', 'Psi_Blades.mp3.mpeg': 'Psi Blades', 'Purification.mp3.mpeg': 'Purification', 'Purifying_Flames.mp3.mpeg': 'Purifying Flames',
# 'Quill_Spray.mp3.mpeg': 'Quill Spray', 'Rage.mp3.mpeg': 'Rage', 'Ravage.mp3.mpeg': 'Ravage', 'Reality_Rift.mp3.mpeg': 'Reality Rift', "Reaper's_Scythe.mp3.mpeg": "Reaper's Scythe", 'Rearm.mp3.mpeg': 'Rearm', 'Refraction.mp3.mpeg': 'Refraction', 'Refresher_Orb.mp3.mpeg': ['Refresher Orb', "refresher", "Refresher Shard"],
# 'Relocate.mp3.mpeg': 'Relocate', 'Remote_Mines.mp3.mpeg': 'Remote Mines', 'Requiem_of_Souls.mp3.mpeg': 'Requiem of Souls', 'Astral_Spirit.mp3.mpeg': 'Astral Spirit', 'Reverse_Polarity.mp3.mpeg': ('Reverse Polarity', "rp"), 'Rip_Tide.mp3.mpeg': 'Rip Tide', 'Rocket_Barrage.mp3.mpeg': 'Rocket Barrage',
# 'Rocket_Flare.mp3.mpeg': 'Rocket Flare', 'Rod_of_Atos.mp3.mpeg': ('Rod of Atos', "atos"), 'Rolling_Boulder.mp3.mpeg': 'Rolling Boulder', 'Rupture.mp3.mpeg': 'Rupture', 'Sacred_Arrow.mp3.mpeg': 'Sacred Arrow', 'Sacrifice.mp3.mpeg': ("Sinister Gaze", 'sacrifice'), 'Sand_Storm.mp3.mpeg': 'Sand Storm',
# "Sanity's_Eclipse.mp3.mpeg": "Sanity's Eclipse", 'Satanic.mp3.mpeg': 'Satanic', 'Savage_Roar.mp3.mpeg': 'Savage Roar', 'Scatterblast.mp3.mpeg': 'Scatterblast', 'Scream_of_Pain.mp3.mpeg': 'Scream of Pain', 'Searing_Arrows.mp3.mpeg': 'Searing Arrows', 'Searing_Chains.mp3.mpeg': 'Searing Chains',
# 'Shackles.mp3.mpeg': 'Shackles', 'Shackleshot.mp3.mpeg': 'Shackleshot', 'Shadowraze.mp3.mpeg': 'Shadowraze', 'Shadow_Poison.mp3.mpeg': 'Shadow Poison', 'Shadow_Realm.mp3.mpeg': 'Shadow Realm', 'Shadow_Strike.mp3.mpeg': 'Shadow Strike', 'Shadow_Walk.mp3.mpeg': 'Shadow Walk',
# 'Shadow_Wave.mp3.mpeg': 'Shadow Wave', 'Shallow_Grave.mp3.mpeg': 'Shallow Grave', 'Shapeshift.mp3.mpeg': 'Shapeshift', 'Shield_Crash.mp3.mpeg': 'Shield Crash', "Shiva's_Guard.mp3.mpeg": ("Shiva's Guard", "shiva"), 'Shockwave.mp3.mpeg': 'Shockwave', 'Shrapnel.mp3.mpeg': 'Shrapnel',
# 'Shuriken_Toss.mp3.mpeg': 'Shuriken Toss', 'Silence.mp3.mpeg': 'Silence', 'Silver_Edge.mp3.mpeg': 'Silver Edge', 'Skeleton_Walk.mp3.mpeg': 'Skeleton Walk', 'Skewer.mp3.mpeg': 'Skewer', 'Slithereen_Crush.mp3.mpeg': 'Slithereen Crush', 'Smoke_Screen.mp3.mpeg': 'Smoke Screen', 'Snowball.mp3.mpeg': 'Snowball',
# 'Solar_Crest.mp3.mpeg': 'Solar Crest', 'Song_of_the_Siren.mp3.mpeg': 'Song of the Siren', 'Sonic_Wave.mp3.mpeg': 'Sonic Wave', 'Soulbind.mp3.mpeg': 'Soulbind', 'Soul_Assumption.mp3.mpeg': 'Soul Assumption', 'Soul_Catcher.mp3.mpeg': 'Soul Catcher', 'Soul_Rip.mp3.mpeg': 'Soul Rip',
# 'Spawn_Spiderlings.mp3.mpeg': 'Spawn Spiderlings', 'Spectral_Dagger.mp3.mpeg': 'Spectral Dagger', 'Spell_Shield.mp3.mpeg': 'Spell Shield', 'Spell_Steal.mp3.mpeg': 'Spell Steal', 'Spiked_Carapace.mp3.mpeg': ('Spiked Carapace', "carapace"), 'Spin_Web.mp3.mpeg': 'Spin Web', 'Spirits.mp3.mpeg': 'Spirits',
# 'Spirit_Lance.mp3.mpeg': 'Spirit Lance', 'Spirit_Siphon.mp3.mpeg': 'Spirit Siphon', 'Splinter_Blast.mp3.mpeg': 'Splinter Blast', 'Split_Earth.mp3.mpeg': 'Split Earth', 'Sprint.mp3.mpeg': 'Sprint', 'Sprout.mp3.mpeg': 'Sprout', 'Stampede.mp3.mpeg': 'Stampede', 'Starstorm.mp3.mpeg': 'Starstorm',
# 'Static_Link.mp3.mpeg': 'Static Link', 'Static_Remnant.mp3.mpeg': 'Static Remnant', 'Stifling_Dagger.mp3.mpeg': 'Stifling Dagger', 'Stone_Gaze.mp3.mpeg': 'Stone Gaze', 'Storm_Hammer.mp3.mpeg': ('Storm Hammer', "storm bolt"), 'Strafe.mp3.mpeg': 'Strafe',
# 'Stroke_of_Fate.mp3.mpeg': 'Stroke of Fate', 'Summon_Familiars.mp3.mpeg': 'Summon Familiars', 'Summon_Spirit_Bear.mp3.mpeg': 'Summon Spirit Bear', 'Summon_Wolves.mp3.mpeg': 'Summon Wolves', 'Sunder.mp3.mpeg': 'Sunder', 'Sun_Ray.mp3.mpeg': 'Sun Ray', 'Sun_Strike.mp3.mpeg': 'Sun Strike',
# 'Supernova.mp3.mpeg': 'Supernova', 'Surge.mp3.mpeg': 'Surge', 'Swashbuckle.mp3.mpeg': 'Swashbuckle', 'Telekinesis.mp3.mpeg': 'Telekinesis', 'Teleportation.mp3.mpeg': 'Teleportation', 'Tempest_Double.mp3.mpeg': 'Tempest Double', 'Terrorize.mp3.mpeg': 'Terrorize', 'Test_of_Faith.mp3.mpeg': 'Test of Faith',
# 'Tether.mp3.mpeg': 'Tether', 'The_Swarm.mp3.mpeg': 'The Swarm', "Thundergod's_Wrath.mp3.mpeg": "Thundergod's Wrath", 'Thunder_Clap.mp3.mpeg': 'Thunder Clap', 'Thunder_Strike.mp3.mpeg': 'Thunder Strike', 'Tidebringer.mp3.mpeg': 'Tidebringer', 'Timber_Chain.mp3.mpeg': 'Timber Chain',
# 'Time_Dilation.mp3.mpeg': 'Time Dilation', 'Time_Lapse.mp3.mpeg': 'Time Lapse', 'Time_Walk.mp3.mpeg': 'Time Walk', 'Tornado.mp3.mpeg': 'Tornado', 'Torrent.mp3.mpeg': 'Torrent', 'Toss.mp3.mpeg': 'Toss', 'Track.mp3.mpeg': 'Track', 'Tree_Throw.mp3.mpeg': 'Tree Throw',
# 'Tricks_of_the_Trade.mp3.mpeg': 'Tricks of the Trade', 'True_Form.mp3.mpeg': 'True Form', 'Vacuum.mp3.mpeg': 'Vacuum', 'Veil_of_Discord.mp3.mpeg': ('Veil of Discord', "veil"), 'Vendetta.mp3.mpeg': 'Vendetta', 'Venomous_Gale.mp3.mpeg': 'Venomous Gale', 'Viper_Strike.mp3.mpeg': 'Viper Strike',
# 'Viscous_Nasal_Goo.mp3.mpeg': ('Viscous Nasal Goo', "nasal goo"), 'Void.mp3.mpeg': 'Void', 'Wall_of_Replica.mp3.mpeg': 'Wall of Replica', 'Walrus_Punch.mp3.mpeg': 'Walrus Punch', 'Waning_Rift.mp3.mpeg': 'Waning Rift', 'Warcry.mp3.mpeg': 'Warcry', 'Waveform.mp3.mpeg': 'Waveform',
# 'Wave_of_Terror.mp3.mpeg': 'Wave of Terror', 'Whirling_Axes_(Melee).mp3.mpeg': 'Whirling Axes', 'Whirling_Axes_(Ranged).mp3.mpeg': 'Whirling Axes', 'Whirling_Death.mp3.mpeg': 'Whirling Death', 'Wild_Axes.mp3.mpeg': 'Wild Axes', 'Windrun.mp3.mpeg': 'Windrun',
# "Winter's_Curse.mp3.mpeg": "Winter's Curse", 'Wraithfire_Blast.mp3.mpeg': 'Wraithfire Blast', 'Wrath_of_Nature.mp3.mpeg': 'Wrath of Nature', "Wukong's_Command.mp3.mpeg": "Wukong's Command", 'X_Marks_the_Spot.mp3.mpeg': 'X Marks the Spot'}

#lists of Replies in case of right, wrong or no/late answers
rightansw = ("That is correct!", "That's correct.", "Correct answer!", "You're right!", "Your answer is correct!", "Nice one.", "That answer is correct!", "Spot on!", "Right on!", "Nicely done.", "Well done.", "Good job!", "Correct!", "That's true!", "Right answer!", "Clever")
wrongansw = ("That's not quite right.", "That's not right...", "Your answer isn't correct.", "Not correct...", "Not quite it...", "From the Ghastly Eyrie I can see to the ends of the world, and from this vantage point I declare with utter certainty that your answer is wrong.", "YOU GET NOTHING, GOOD DAY SIR!", "At least you tried...")
lateansw = ("You ran out of time.", "Too late.", "You didn't answer in time.", "Be quicker next time...", "You're out of time.", "Out of time.", "Time grinds even questions to dust.", "You took too much time.", "Time is the cruelest cut.", "Time's up.", "Don't wait too long...")
#Gives a random response 'R' for right answer, 'W' for wrong answer, 'L' for late answer
def get_answ(answtype):
	tup = ()
	if answtype == 'R':
		tup = rightansw
	elif answtype == 'W':
		tup = wrongansw
	elif answtype == 'L':
		tup = lateansw
	return rand.choice(tup)


#Detailed command infos for 322 help command
command_dinfos = {"quiz":"A single question which gives 24 gold with 22 seconds of time to answer.",
"blitz":"""50 seconds of rapid questions which start after a short delay, each question also has a limited time to answer which depends on the size of the question. Blitz is high-risk high-reward in terms of gold, you get more gold according to how many correct answers you have, wrong answers and late answers take away gold but you can skip a question by typing "skip" in chat during the blitz to lose less time and gold.""",
"shopquiz":"""Endlessly sends icons of a DotA2 items and possible components to assemble, you have to type in the letters of the items you think are correct at once, you have 21 seconds to do so. The order of the letters doesn't matter and you can reuse a letter if two of the same item is needed for the recipe. You earn more gold the more correct answers you have in a row.""",
"endless":"""Endlessly sends questions, items to assemble, ability icons and d hero names randomly, you are given 5 lives. Gives bonus gold according to the amount of current correct answers in a row. You can type in "skip" to skip a question and lose half a life instead and "stop" to stop the quiz entirely any time. Aghanim's Scepter is required to use this command.""",
"iconquiz":"""Endlessly sends DotA2 ability icons that must be named, you are given 3 lives, you earn more gold the more icons you name correctly. You type "skip" to jump to the next icon to lose half a life only and type stop to "stop" the quiz entirely. Each correct answer is more rewarding the more correct answers you have in a row. For an easier version try 322 easyiconquiz|easyicon""",
"duel":"Both duellers must have enough gold to start a duel. After a short delay, sends 15 questions(one by one) which can be answered by both duel participants, first to answer gets +1 point, if the first answer to be sent is incorrect the challenger will lose 1 point. After all 15 questions are answered the winner will get 200 less gold than the wager while the loser loses the full amount of gold. Minimum wager is 300 gold while the maximum is 10000(20000 if initatior has Pirate Hat).",
"audioquiz":"""You must be in an accesible voice channel to use this command. Plays sound effects from the game that must be answered in the chat by typing in the name of the item or spell that makes the sound. You can use "replay" or "re" to replay the sound effect or "skip" to skip it or "stop" to disconnect the bot entirely. Each correct answer gives additional 3.5 seconds and every next answer gives more gold.""",
"freeforall":"Asks 25(35 if initiator has a Necronomicon) questions(could be icons) in a channel which anyone can answer. The prize pool multiplies according to the amount of participants who gave at least one correct answer and how many questions were answered correctly in total, each question allows for 3 tries. Players get points for correct answers and lose a point for a wrong answer. The prize pool is then distributed among the top 5 players as 60%, 20%, 10%, 5%, 5% of the total prize pool.",
"scramble":"Sends a scrambled/shuffled DotA2 hero name and you must guess which hero it is. Spaces are displayed as empty blue squares.", "buy":"Buy one of the items from the store to improve some stats for the quiz commands.",
"sell":"Sell an item you already own for half its price(or 75% if you're selling cheese).", "store":"Check available items, their prices and what they do.",
"inventory":"Check which items you have in your inventory.",
"gold":"Check the amount of gold you currently have.",
"copypasta":"Get a copy of a DotA related text of your choice.",
"hohoohahaa":"The Shifting Snow.", "newpatch":"Icefrog releases a new patch.",
"givecheese":"Give another user any amount of cheese.",
"cheeseboard":"Check the top 10 users who have the most cheese. Users in different servers have their names hidden but the cheese amount is visible.",
"missedhook":"Check why you missed your hook.",
"serverinvite":"Get a server invite to our discord server!",
"easyiconquiz":"Easier iconquiz with multiple choice answers, gives only 5 gold per correct answer. Better for learning/playing calm."}

#The store system:
store_items = {"Hand of Midas":6000, "Helm of Dominator":2350, "Armlet of Mordiggian":3000, "Aeon Disk":3000, "Aghanim's Scepter":4200, "Necronomicon":4550, "Linken's Sphere":4800,
"Shiva's Guard":5175, "Monkey King Bar":4700, "Octarine Core":4800, "Pirate Hat":7000, "Aegis":10000, "Cheese":20000, "Cursed Rapier":100000}
store_descriptions = {"Hand of Midas":"Earn 20% bonus gold.", "Cheese":"Alternate, tradable currency.", "Octarine Core":"Lower cooldowns for commands by 25%.",
"Cursed Rapier":"Weird flex.", "Shiva's Guard":"Add 30% duration to time limits.", "Aegis":"One extra life for certain commands.", "Aghanim's Scepter":"Allows you to use 322 endless.",
"Pirate Hat":"Increases the max wager of duel by 10k.", "Monkey King Bar":"Improves typo recognition for answers.", "Necronomicon":"Increases number of questions on 322 freeforall.",
"Helm of Dominator":"Gives 5% discount on all items.", "Aeon Disk":"Saves half of your answer streak.", "Armlet of Mordiggian":"10% less time for 5% more gold.", "Linken's Sphere":"Saves your answer streak once."}

#Copypastas for 322 copypasta
copypastas = {"diretide":"༼ つ ◕_◕ ༽つ GIVE DIRETIDE",
"oversight":"The biggest oversight with Dark Willow is that she's unbelievably sexy. I can't go on a hour of my day without thinking about plowing that tight wooden ass. I'd kill a man in cold blood just to spend a minute with her crotch grinding against my throbbing manhood as she whispers terribly dirty things to me in her geographically ambiguous accent.",
"heyrtz":"ＨＥＹ　ＲＴＺ，　Ｉ’Ｍ　ＴＲＹＩＮＧ　ＴＯ　ＬＥＡＲＮ　ＴＯ　ＰＬＡＹ　ＲＩＫＩ．　Ｉ　ＪＵＳＴ　ＨＡＶＥ　Ａ　ＱＵＥＳＴＩＯＮ　ＡＢＯＵＴ　ＴＨＥ　ＳＫＩＬＬ　ＢＵＩＬＤ：　ＳＨＯＵＬＤ　Ｉ　ＭＡＸ　ＢＡＣＫＳＴＡＢ　ＬＩＫＥ　ＹＯＵ　ＢＡＣＫＳＴＡＢＢＥＤ　ＥＧ，　ＳＭＯＫＥＳＣＲＥＥＮ　ＳＯ　ＴＨＥＲＥ＇Ｓ    ３２５  ＡＯＥ  ＤＲＡＭＡ  ＡＲＯＵＮＤ  ＹＯＵ， \
　ＯＲ  ＢＬＩＮＫ  ＳＴＲＩＫＥ  ＬＩＫＥ  ＴＨＥ  ＷＡＹ  ＹＯＵ  ＢＬＩＮＫＥＤ  ＢＡＣＫ  ＴＯ  ＥＧ  ＡＦＴＥＲ  ＴＨＥＹ  ＨＡＤ  ＷＯＮ  ＴＩ",
"artour":"""My name Artour Babaev. Sorry bad englandsky. I grow up in small farm to have make potatoes. Father say "Arthour, potato harvest is bad. Need you to have play professional DOTO2 in Amerikanski for make money for head-scarf for babushka." I bring honor to komrade and babushka. Plz no copy pasteschniko.""",
"puppey":"The scariest moment in my time with secret was during our practices, when Puppey would walk around with a machete and talk about how he always wanted to see what the inside of a human looked like. He said he had experimented on animals before and he wanted to go for the real thing. I believed him.",
"averageplay":"ＥＨ， ＡＶＥＲＡＧＥ ＰＬＡＹ． ＯＢＶＩＯＵＳ ＱＯＰ ＷＯＵＬＤ ＢＬＩＮＫ， ＳＯ ＩＴ ＷＯＵＬＤ ＢＥ ＳＴＵＰＩＤ ＴＯ ＮＯＴ ＢＬＩＮＫ ＴＯ ＴＨＡＴ ＥＸＡＣＴ ＳＰＯＴ ＡＮＤ ＥＶＥＮ ＦＡＫＥ ＹＯＵＲ ＵＬＴ Ａ ＬＩＴＴＬＥ ＦＩＲＳＴ ＴＯ ＭＡＫＥ ＨＥＲ ＴＨＩＮＫ ＹＯＵ ＷＥＲＥＮ＇Ｔ ＧＯＩＮＧ ＴＯ ＤＯ ＩＴ！， ５／１０",
"report":"Good Jokes mate real funny see u at FUCK YOUJ", "sodium":"""Sodium, atomic number 11, was first isolated by Peter "ppd" Dager in 1807. A chemical component of salt, he named it Na in honor of the saltiest region on earth, North America.""",
"juggernaut":"I'M THE JUGGERNAUT, BITCH!", "flower":"SPAM 🌻 THIS 🌻 FLOWER 🌻 TO 🌻 GIVE 🌻 NOTAIL 🌻 POWER 🌻", "inthebag":"From the Ghastly Eyrie I can see to the ends of the world, and from this vantage point I declare with utter certainty that this one is in the bag!",
"timbersaw":"Someone once told me I needed to face fear to get over it, and I thought well why not take a step further and cut my fear into little pieces then set my fear on fire then throw the hot ash of my fear into a lake and then poison the lake. Simple!"}

copypastainfo = {"diretide":"Give diretide volvo.", "oversight":"The biggest oversight.", "heyrtz":"Riki skillbuild.", "artour":"Story of Artour Babaev.",
"puppey":"Fight me.", "averageplay":"Miracle-'s average play.", "report":"Nice jokes mate.", "sodium":"Information about Sodium - Na.", "juggernaut":"A famous quote of the hero.",
"flower":"Give N0tail power.", "inthebag":"It's in the bag.", "timbersaw":"How to face fear."}
