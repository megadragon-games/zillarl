########################################################################################################
# zillarl_utils.py
#    by Bluey
# This Python script contains random number generation and other utility functions for Bigger is Better 
# (ZillaRL).
# http://www.forcastia.com | http://the-gain-girl.tumblr.com
#    Last updated on August 19, 2014
#    2014 Studio Draconis
########################################################################################################

import libtcodpy as libtcod

#This function is a more concise way of invoking the libtcod random function, for shortening
#the function call. Calling the function without parameters flips a coin (returns either 0 or 1). This
#shortened function will always default to using the zeroth random number stream, so for situations
#where a certain stream needs to be specified, the entire random_get_int call will need to be made.
def rnd(min = 0, max = 1):
	return libtcod.random_get_int(0, min, max)
	
#This function returns a value that depends on the current game level. Since this function is now split
#from the main script file, the current level will need to be passed as the first argument. The table
#specifies what value occurs after each level - default is zero - 
def fromLabLevel(table):
	for (value, level) in reversed(table):
		if dungeonLevel >= level:
			return value
	return 0
	
#This function is used for displaying Zilla's health, which is measured in inches and must be
#converted to feet on the fly.
def convertHealthToSize(amount):
	return str(amount / 12) + "'" + str(amount % 12) + '"'
	
#This function is used for displaying Zilla's weight, which is measured in pounds, or tons if necessary.
def convertWeight(amount):
	convertedToTons = amount / 2000.0
	
	if amount < 2000:
		return str(amount) + " lbs"
	else:
		return str("%.2f" % round(convertedToTons, 2)) + " tons"