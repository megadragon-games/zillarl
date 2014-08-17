########################################################################################################
# zillarl_parse.py
#    by Bluey
# Python script containing functions for the libtcod parser, used in Bigger is Better (ZillaRL).
# http://www.forcastia.com | http://the-gain-girl.tumblr.com
#    Last updated on August 16, 2014
#    2014 Studio Draconis
########################################################################################################

import libtcodpy as libtcod
import os

#Data Dictionaries
rawItemData = {}
rawNameSets = None

itemsFood = []
itemsPotions = []
itemsSuits = []

#Object Loading Function
def loadObjectData():
	parser = libtcod.parser_new()
	
	#Use the parser to read data for items.
	itemStruct = libtcod.parser_new_struct(parser, "item")
	libtcod.struct_add_property(itemStruct, "name", libtcod.TYPE_STRING, True)
	libtcod.struct_add_property(itemStruct, "kind", libtcod.TYPE_STRING, True)
	libtcod.struct_add_property(itemStruct, "col", libtcod.TYPE_COLOR, True)
	libtcod.struct_add_property(itemStruct, "dsc", libtcod.TYPE_STRING, True)
	libtcod.struct_add_property(itemStruct, "bloat", libtcod.TYPE_INT, False)
	libtcod.struct_add_property(itemStruct, "useEffect", libtcod.TYPE_STRING, False)
	#libtcod.struct_add_property(itemStruct, "slot", libtcod.TYPE_STRING, False)
	
	libtcod.parser_run(parser, os.path.join('data', 'item.cfg'), ItemReader())
	print "The current contents of rawItemData, outside of the parsing operation, are..."
	print rawItemData.items()
		
	#Load the name generation data.
	for file in os.listdir('data/name'):
		if file.find('.cfg') > 0:
			libtcod.namegen_parse(os.path.join('data', 'name', file))
	rawNameSets = libtcod.namegen_get_sets()
	
# Data Parser Listeners
class ItemReader:
	def new_struct(self, struct, name):
		global rawItemData
		self.currentItem = name
		rawItemData[name] = {}
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
			itemsSuits.append(self.currentItem)
		
		print "New property read for " + self.currentItem + ": " + name
		print str(rawItemData[self.currentItem][name]) + " with ID " + str(id(value))
		return True

	def end_struct(self, struct, name):
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
