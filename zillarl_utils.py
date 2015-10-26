########################################################################################################
# zillarl_utils.py
#    by Bluey
# This Python script contains parsing, text variation, random number generation,
# and other utility functions for Bigger is Better (ZillaRL).
# http://www.forcastia.com | http://the-gain-girl.tumblr.com
#    Last updated on October 25, 2015
#    2014-2015 Studio Draconis
########################################################################################################

import libtcodpy as libtcod
import ConfigParser, os

#Debug Mode
option_debug = False

#Data Dictionaries
rawMonsterData = {}
rawItemData = {}
rawNameSets = None
rawScript = {}

#Monster Lists
monstersTierZero = []
monstersTierOne = []

#Item Lists
itemsFood = []
itemsPotions = []
itemsSuits = []

# GENERIC UTILITY FUNCTIONS
def rnd(min = 0, max = 1):
	'''RND invokes the libtcod random function and will return an integer between
	min and max. Calling the function without parameters flips a coin (returns either
	0 or 1). This function always uses the zeroth random number stream; if a certain
	stream needs to be specified, use the entire random_get_int call.'''
	return libtcod.random_get_int(0, min, max)

def fromLabLevel(table):
	'''FROM LAB LEVEL returns a value that depends on the given game level. The
	table specifies what value occurs after each level - default is zero.'''
	for (value, level) in reversed(table):
		if dungeonLevel >= level:
			return value
	return 0

def convertHealthToSize(amount):
	'''CONVERT HEALTH TO SIZE is used in displaying Zilla's health, where each individual
	hit point represents an inch of height.'''
	return str(amount / 12) + "'" + str(amount % 12) + '"'

def convertWeight(amount):
	'''CONVERT WEIGHT is used in displaying Zilla's weight, which is measured in
	either pounds or tons.'''
	convertedToTons = amount / 2000.0

	if amount < 2000:
		return str(amount) + " lbs"
	else:
		return str("%.2f" % round(convertedToTons, 2)) + " tons"

# SCRIPT FUNCTIONS
def loadScript():
	'''LOAD SCRIPT reads script.ini and builds a dictionary of strings for use
	in the game\'s random text functions.'''
	reader = ConfigParser.ConfigParser()
	reader.read(os.path.join('data', 'script.ini'))

	for section in reader.sections():
		rawScript[section] = {}
		for key, value in reader.items(section):
			split = value.splitlines()
			if len(split) > 1:
				# if the value, split at each line, has more than one entry in
				# the resulting list, we want to enter it into the dictionary as
				# a list, not a single string. This list comprehension strips all
				# whitespace and only enters it into the dictionary if it is a
				# true-ish value - as in, no empty strings
				rawScript[section][key] = [item.strip() for item in split if item]
			else:
				rawScript[section][key] = value

def choose(list):
	'''CHOOSE returns a random entry from a given list.'''
	max = len(list) - 1
	selection = rnd(0, max)
	return list[selection]

def vary(list):
	line = choose(list)
	line = line.replace("{GRUNT}", choose(rawScript["Noises"]["grunts"]))
	line = line.replace("{BURP}", choose(rawScript["Noises"]["burps"]))
	return line

def zillaAttacksMonster(targetName):
	'''ZILLA ATTACKS MONSTER returns a message for when Zilla attacks a monster.
	The damage amount is not explicitly stated when Zilla attacks, so it does not
	need to be passed to this function.'''
	line = "Zilla " + vary(rawScript["Noises"]["attack"]) + " the " + targetName + " with her belly!"
	return line

#This function returns a message for when Zilla is attacked by a monster. Unlike the above, the damage
#amount is explicitly stated when Zilla is attacked, so the damage amount must be passed.
def zillaAttackedByMonster(monsterName, damageAmount):
	'''ZILLA ATTACKED BY MONSTER returns a message for when Zilla is attacked by
	a monster. The damage amount is explicitly stated when Zilla is attacked, so
	the damage amount must be passed as an argument.'''
	line = "The " + monsterName + " attacks Zilla! She " + vary(rawScript["Noises"]["shrink"])
	if damageAmount == 1:
		line += " an inch smaller."
	else:
		line += " " + str(damageAmount) + " inches smaller."

	return line

def zillaAttacksButMisses(targetName):
	line = "Zilla " + vary(rawScript["Noises"]["attack"]) + " the " + targetName + " with her belly, but "
	line += vary(rawScript["HarmlessAttack"]["zilla"]) + "!"
	return line

def zillaAttackedButMissed(monsterName):
	line = "The " + monsterName + " attacks Zilla, but " + vary(rawScript["HarmlessAttack"]["monster"]) + "!"
	return line

def zillaWhineTiny():
	return vary(rawScript["Whines"]["lowhealth"])

	#This function returns a message for when Zilla eats or drinks.
	def zillaEats(eatOrDrink, eatenItem, addedWeight):
		choice = libtcod.random_get_int(0, 1, 4)

		#The eatOrDrink string states whether Zilla should be using her eating strings, or her
		#drinking strings.
		if eatOrDrink == "eat":
			line = "Zilla " + vary(eatNoises) + " the " + eatenItem

			#The adverb that describes how Zilla eats or drinks is omitted if choice is equal to 4.
			if choice != 4:
				line += " " + vary(eatAdverbs) + " and gains "
			else:
				line += " and gains "

			#Pound is singular if addedWeight is equal to one, and plural otherwise.
			if addedWeight == 1:
				line += str(addedWeight) + " pound."
			else:
				line += str(addedWeight) + " pounds."

		else:
			line = "Zilla " + vary(drinkNoises) + " the " + eatenItem

			#The adverb that describes how Zilla eats or drinks is omitted if choice is equal to 4.
			if choice != 4:
				line += " " + vary(eatAdverbs) + " and gains "
			else:
				line += " and gains "

			#Pound is singular if addedWeight is equal to one, and plural otherwise.
			if addedWeight == 1:
				line += str(addedWeight) + " pound."
			else:
				line += str(addedWeight) + " pounds."

		return line

#LIBTCOD PARSER FUNCTIONS
def loadObjectData():
	'''LOAD OBJECT DATA reads the CFG files in the data folder to build dictionaries
	of monsters, items, and name generation data.'''
	parser = libtcod.parser_new()

	#Use the parser to read data for monsters.
	monsterStruct = libtcod.parser_new_struct(parser, "monster")
	libtcod.struct_add_property(monsterStruct, "name", libtcod.TYPE_STRING, True)
	libtcod.struct_add_property(monsterStruct, "glyph", libtcod.TYPE_CHAR, True)
	libtcod.struct_add_property(monsterStruct, "col", libtcod.TYPE_COLOR, True)
	libtcod.struct_add_property(monsterStruct, "dsc", libtcod.TYPE_STRING, True)
	libtcod.struct_add_property(monsterStruct, "tier", libtcod.TYPE_INT, True)
	libtcod.struct_add_property(monsterStruct, "hp", libtcod.TYPE_INT, True)
	libtcod.struct_add_property(monsterStruct, "atk", libtcod.TYPE_INT, True)
	libtcod.struct_add_property(monsterStruct, "dfn", libtcod.TYPE_INT, True)
	libtcod.struct_add_property(monsterStruct, "min", libtcod.TYPE_INT, True)
	libtcod.struct_add_property(monsterStruct, "max", libtcod.TYPE_INT, True)
	libtcod.struct_add_property(monsterStruct, "xp", libtcod.TYPE_INT, True)
	libtcod.struct_add_property(monsterStruct, "deathEffect", libtcod.TYPE_STRING, False)

	libtcod.parser_run(parser, os.path.join('data', 'monster.cfg'), MonsterReader())
	if option_debug:
		print "The current contents of rawMonsterData, outside of the parsing operation, are..."
		print rawMonsterData.items()

	#Use the parser to read data for items.
	itemStruct = libtcod.parser_new_struct(parser, "item")
	libtcod.struct_add_property(itemStruct, "name", libtcod.TYPE_STRING, True)
	libtcod.struct_add_property(itemStruct, "kind", libtcod.TYPE_STRING, True)
	libtcod.struct_add_property(itemStruct, "col", libtcod.TYPE_COLOR, True)
	libtcod.struct_add_property(itemStruct, "dsc", libtcod.TYPE_STRING, True)
	libtcod.struct_add_property(itemStruct, "bloat", libtcod.TYPE_INT, False)
	libtcod.struct_add_property(itemStruct, "rarity", libtcod.TYPE_INT, True)
	libtcod.struct_add_property(itemStruct, "useEffect", libtcod.TYPE_STRING, False)
	#libtcod.struct_add_property(itemStruct, "slot", libtcod.TYPE_STRING, False)

	libtcod.parser_run(parser, os.path.join('data', 'item.cfg'), ItemReader())
	if option_debug:
		print "The current contents of rawItemData, outside of the parsing operation, are..."
		print rawItemData.items()

	#Load the name generation data.
	for file in os.listdir('data/name'):
		if file.find('.cfg') > 0:
			libtcod.namegen_parse(os.path.join('data', 'name', file))
	rawNameSets = libtcod.namegen_get_sets()

#Monster data parser class.
class MonsterReader:
	def new_struct(self, struct, name):
		global rawMonsterData
		self.currentMonster = name
		rawMonsterData[name] = {}
		if option_debug:
			print "New struct, beginning parsing."
		return True

	def new_flag(self, name):
		global rawMonsterData
		rawMonsterData[self.currentMonster][name] = True
		return True

	def new_property(self, name, type, value):
		global rawMonsterData

		if type == libtcod.TYPE_COLOR:
			rawMonsterData[self.currentMonster][name] = libtcod.Color(value.r, value.g, value.b)
		else:
			rawMonsterData[self.currentMonster][name] = value
		if option_debug:
			print "New property read for " + self.currentMonster + ": " + name
			print str(rawMonsterData[self.currentMonster][name]) + " with ID " + str(id(value))

		if (name == "tier" and value == 0):
			monstersTierZero.append(self.currentMonster)
			if option_debug:
				print "Adding monster to Tier Zero list."
		elif (name == "tier" and value == 1):
			monstersTierOne.append(self.currentMonster)
			if option_debug:
				print "Adding monster to Tier One list."

		return True

	def end_struct(self, struct, name):
		if option_debug:
			print "The " + self.currentMonster + " struct is now complete."
		self.currentMonster = None
		return True

	def error(self, msg):
		global rawMonsterData
		print 'WARNING. There has been an error with the MONSTER data parser: ', msg
		if self.currentMonster is not None:
			del rawMonsterData[self.currentMonster]
			self.currentMonster = None
		return True

#Item data parser class.
class ItemReader:
	def new_struct(self, struct, name):
		global rawItemData
		self.currentItem = name
		rawItemData[name] = {}
		if option_debug:
			print "New struct, beginning parsing."
		return True

	def new_flag(self, name):
		global rawItemData
		rawItemData[self.currentItem][name] = True
		return True

	def new_property(self, name, type, value):
		global rawItemData

		if type == libtcod.TYPE_COLOR:
			rawItemData[self.currentItem][name] = libtcod.Color(value.r, value.g, value.b)
		else:
			rawItemData[self.currentItem][name] = value

		if (name == "kind" and value == "food"):
			itemsFood.append(self.currentItem)
		elif (name == "kind" and value == "potion"):
			itemsPotions.append(self.currentItem)
		#elif (name == "kind" and (value == "suit" or value == "rune")):
		elif (name == "kind" and value == "suit"):
			rawItemData[self.currentItem]["slot"] = value
			if self.currentItem != "zilla_bikini":
				itemsSuits.append(self.currentItem)

		if option_debug:
			print "New property read for " + self.currentItem + ": " + name
			print str(rawItemData[self.currentItem][name]) + " with ID " + str(id(value))

		return True

	def end_struct(self, struct, name):
		if option_debug:
			print "The " + self.currentItem + " struct is now complete."
		self.currentItem = None
		return True

	def error(self, msg):
		global rawItemData
		print 'WARNING. There has been an error with the ITEM data parser: ', msg
		if self.currentItem is not None:
			del rawItemData[self.currentItem]
			self.currentItem = None
		return True
