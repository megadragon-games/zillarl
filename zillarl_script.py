########################################################################################################
# zillarl_script.py
#    by Bluey
# Text and script module for Bigger is Better (ZillaRL), containing script strings and functions.
# http://www.forcastia.com | http://gaingirls.tumblr.com
#    Last updated on August 12, 2014
#    (c) 2014 Studio Draconis
########################################################################################################

import libtcodpy as libtcod

#Descriptions
DESC_DEFAULT = "This object has no description."
DESC_ZILLA = "One of our finest test subjects. She was granted extraordinary strength and shapeshifting abilities by our genetic experimentation."

#NOISES are short strings used as verbs. They provide variation to Zilla's actions.
attackNoises = ["bumps", "bashes", "whacks", "thumps", "squishes", "squashes", "smacks"]
shrinkNoises = ["shrinks", "dwindles", "shrivels", "melts"]
eatNoises = ["eats", "munches", "chomps", "swallows"]
drinkNoises = ["drinks", "gulps", "chugs", "guzzles"]
eatAdverbs = ["messily", "noisily", "quickly", "slowly"]

#HARMLESS ATTACK strings are used whenever an actor makes an attack that does not deal damage.
zillaHarmlessAttackStrings = ["bounces off harmlessly!",
	"only manages to make herself belch!",
	"only manages to make herself gurgle!"]
monsterHarmlessAttackStrings = ["bounces harmlessly off her belly!",
	"only tickles her!"]

#ROARS are lines Zilla says in response to positive situations.

#WHINES are lines Zilla says in response to negative situations.
tinyWhines = ["I'm feeling rather small...", "Everything's so big!"]
damageWhines = ["Mmph! You're a big one, aren't you?",
	"Hehe... not so rough, big boy!"]

#TASTES are lines Zilla says in response to given flavors.
tastesGeneric = ["Delicious!", "Yum!", "That hit the spot!", "More! More!"]
tastesSweet = ["Ooh, sweet!"]
tastesJuicy = ["Juicy!"]
tastesCarbonated = ["*burp!*", "*uurp!*", "*hic!*", "Uuuuuurrrrp!", "*belch!*", "HUUUURRRRP!!"]

#This function returns a random entry from a given list, and is used for the base of the other functions
#which select from assigned lists.
def selectFromList(list):
	max = len(list) - 1
	selection = libtcod.random_get_int(0, 0, max)

	return list[selection]

#This function returns a message for when Zilla attacks a monster. The damage amount is not explicitly
#stated when Zilla attacks, so the damage amount is not passed to this function.
def zillaAttacksMonster(targetName):
	line = "Zilla " + selectFromList(attackNoises) + " the " + targetName + " with her belly!"
	return line

#This function returns a message for when Zilla is attacked by a monster. Unlike the above, the damage
#amount is explicitly stated when Zilla is attacked, so the damage amount must be passed.
def zillaAttackedByMonster(monsterName, damageAmount):
	line = "The " + monsterName + " attacks Zilla! She " + selectFromList(shrinkNoises)
	if damageAmount == 1:
		line += " an inch smaller."
	else:
		line += " " + str(damageAmount) + " inches smaller."

	return line

def zillaAttacksButMisses(targetName):
	line = "Zilla " + selectFromList(attackNoises) + " the " + targetName + " with her belly, but "
	line += selectFromList(zillaHarmlessAttackStrings)
	return line

def zillaAttackedButMissed(monsterName):
	line = "The " + monsterName + " attacks Zilla, but " + selectFromList(monsterHarmlessAttackStrings)
	return line

def zillaWhineTiny():
	return selectFromList(tinyWhines)

#This function returns a message for when Zilla eats or drinks.
def zillaEats(eatOrDrink, eatenItem, addedWeight):
	choice = libtcod.random_get_int(0, 1, 4)

	#The eatOrDrink string states whether Zilla should be using her eating strings, or her
	#drinking strings.
	if eatOrDrink == "eat":
		line = "Zilla " + selectFromList(eatNoises) + " the " + eatenItem

		#The adverb that describes how Zilla eats or drinks is omitted if choice is equal to 4.
		if choice != 4:
			line += " " + selectFromList(eatAdverbs) + " and gains "
		else:
			line += " and gains "

		#Pound is singular if addedWeight is equal to one, and plural otherwise.
		if addedWeight == 1:
			line += str(addedWeight) + " pound."
		else:
			line += str(addedWeight) + " pounds."

	else:
		line = "Zilla " + selectFromList(drinkNoises) + " the " + eatenItem

		#The adverb that describes how Zilla eats or drinks is omitted if choice is equal to 4.
		if choice != 4:
			line += " " + selectFromList(eatAdverbs) + " and gains "
		else:
			line += " and gains "

		#Pound is singular if addedWeight is equal to one, and plural otherwise.
		if addedWeight == 1:
			line += str(addedWeight) + " pound."
		else:
			line += str(addedWeight) + " pounds."

	return line
