########################################################################################################
# zillarl.py
#    by Bluey
# Main Python script for Bigger is Better (ZillaRL).
# http://www.forcastia.com | http://the-gain-girl.tumblr.com
#    Last updated on August 15, 2014
#    2014 Studio Draconis
########################################################################################################

import libtcodpy as libtcod

import zillarl_defs as defs
import zillarl_script as script
import zillarl_parse as loader

import math
import textwrap
import shelve 
import copy
	
#########################################################################################################
# [UTILITY CLASSES]                                                                                     #
#########################################################################################################

#The Object class describes a generic game object, such as the player, a monster, an item, or a
#dungeon feature. All objects have an ASCII character, or "glyph" which represents the object on
#the game screen.	
class Object:
	#INIT initializes and constructs the object with the given parameters.
	def __init__(self, x, y, glyph, name, color, desc = defs.DESC_DEFAULT, blocks = False, alwaysVisible = False, 
		fighter = None, ai = None, item = None, equipment = None):
		self.name = name
		self.blocks = blocks
		self.x = x
		self.y = y
		self.glyph = glyph
		self.color = color
		self.alwaysVisible = alwaysVisible
		
		self.desc = desc
		
		self.fighter = fighter
		if self.fighter:
			self.fighter.owner = self
				
		self.ai = ai
		if self.ai:
			self.ai.owner = self
			
		self.item = item
		if self.item:
			self.item.owner = self
			
		self.equipment = equipment
		if self.equipment:
			self.equipment.owner = self
			self.item = Item()
			self.item.owner = self
	
	#MOVE moves the character by the given amount in directionX and directionY.
	def move(self, directionX, directionY):
		if not isBlocked(self.x + directionX, self.y + directionY):
			self.x += directionX
			self.y += directionY
	
	#DRAW sets the color and draws the object's glyph at its position.
	def draw(self):
		if (libtcod.map_is_in_fov(fovMap, self.x, self.y) or (self.alwaysVisible and map[self.x][self.y].explored)):
			libtcod.console_set_default_foreground(con, self.color)
			libtcod.console_put_char(con, self.x, self.y, self.glyph, libtcod.BKGND_NONE)
		
	#CLEAR erases this object's glyph.
	def clear(self):
		libtcod.console_put_char(con, self.x, self.y, defs.gSpace, libtcod.BKGND_NONE)
		
	#MOVE TOWARDS gets a vector and distance from the object to the target, so the object can
	#move toward the target, as in a pursuit.
	def moveTowards(self, targetX, targetY):
		directionX = targetX - self.x
		directionY = targetY - self.y
		distance = math.sqrt(directionX ** 2 + directionY ** 2)
		
		#Normalize the vector to a length of 1, preserving direction, then round it and convert to
		#an integer so the movement is restricted to the map grid.
		directionX = int(round(directionX / distance))
		directionY = int(round(directionY / distance))
		self.move(directionX, directionY)
		
	#DISTANCE TO returns the distance from this object to another object.
	def distanceTo(self, other):
		directionX = other.x - self.x
		directionY = other.y - self.y
		return math.sqrt(directionX ** 2 + directionY ** 2)
		
	#SEND TO BACK makes it so that this object is drawn first, and all other objects on the same tile
	#appear above this object.
	def sendToBack(self):
		global objects
		
		objects.remove(self)
		objects.insert(0,self)
		
	#DISTANCE returns the distance between this object and a tile.
	def distance(self, x, y):
		return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

#The Fighter class describes an Object that is capable of entering into combat. Any object that can
#fight or be attacked must have this component.
class Fighter:
	#INIT initializes and constructs the fighter component.
	def __init__(self, hp, aura, atk, dfn, minDamage, maxDamage, xp, deathEffect = None):
		self.baseHits = hp
		self.cond = hp
		self.aura = aura
		self.baseSppt = aura
		self.baseAtk = atk
		self.baseDfn = dfn
		self.baseMinDamage = minDamage
		self.baseMaxDamage = maxDamage
		self.xp = xp
		self.deathEffect = deathEffect
		
	@property
	def atk(self):
		bonus = sum(equipment.atkBonus for equipment in getAllEquipped(self.owner))
		return self.baseAtk + bonus
		
	@property
	def dfn(self):
		bonus = sum(equipment.dfnBonus for equipment in getAllEquipped(self.owner))
		return self.baseDfn + bonus
	
	@property
	def minDamage(self):
		bonus = sum(equipment.minDamBonus for equipment in getAllEquipped(self.owner))
		if self.owner == player:
			return self.baseMinDamage + bonus + (player.weight / 120 - 1)
		else:
			return self.baseMinDamage + bonus
	
	@property
	def maxDamage(self):
		bonus = sum(equipment.maxDamBonus for equipment in getAllEquipped(self.owner))
		if self.owner == player:
			return self.baseMaxDamage + bonus + (player.weight / 120 - 1)
		else:
			return self.baseMaxDamage + bonus
	
	@property
	def hits(self):
		bonus = sum(equipment.hpBonus for equipment in getAllEquipped(self.owner))
		return self.baseHits + bonus
	
	@property
	def sppt(self):
		bonus = sum(equipment.spptBonus for equipment in getAllEquipped(self.owner))
		return self.baseSppt + bonus	
		
	#TAKE DAMAGE handles damage and hit point loss.
	def takeDamage(self, damage):
		if damage > 0:
			self.cond -= damage
			
			#If the damage-taker is Zilla, and she falls below 13 HP, change her glyph
			if self.owner == player and self.cond < 13:
				message(script.zillaWhineTiny(), defs.cZilla)
				player.glyph = defs.gZillaShrunk
			
			#Check for death. If there is a death function and the fighter's health is zero or lower,
			#call the death function.
			if self.cond <= 0:
				function = self.deathEffect
				if function is not None:
					function(self.owner)
					
				#Yield experience to the player.
				if self.owner != player:
					player.fighter.xp += self.xp
					message("Zilla gains " + str(self.xp) + " mutation points.", libtcod.orange)
			
	#ATTACK handles a fighter's attack against another fighter.
	def attack(self, target):
		selfAttackRating = libtcod.random_get_int(0, 1, self.atk)
		targetDefenseRating = libtcod.random_get_int(0, 1, target.fighter.dfn)
		if(selfAttackRating >= targetDefenseRating):
			#An attack succeeds if the fighter's attack roll is equal to or greater than the target's defense roll.
			#Calculate damage
			damage = libtcod.random_get_int(0, self.minDamage, self.maxDamage)
			
			if self.owner == player:
				message(script.zillaAttacksMonster(target.name), libtcod.purple)

			elif target == player:
				message(script.zillaAttackedByMonster(self.owner.name, damage), libtcod.green)
					
			target.fighter.takeDamage(damage)
		else:
			if self.owner == player:
				message(script.zillaAttacksButMisses(target.name), libtcod.light_crimson)
					
			if target == player:
				message(script.zillaAttackedButMissed(self.owner.name), libtcod.light_crimson)
			
			if self.owner != player and target != player: 
				#If neither the attacker nor the target is Zilla, a default message is used.
				message("The " + self.owner.name + " attacks the " + target.name + " but it has no effect!", libtcod.light_crimson)
		
	#HEAL increases a fighter's current hitpoints, but cannot go over the maximum.
	def heal(self, amount):
		self.cond += amount
		if self.cond > self.hits:
			self.cond = self.hits
			
		#If the object being healed is Zilla, and she rises above 12 HP, change her sprite
		if self.owner == player and self.cond > 12:
			player.glyph = defs.gZilla
			
	def recover(self, amount):
		self.aura += amount
		if self.aura > self.sppt:
			self.aura = self.sppt
	
#This BasicMonster class contains AI routines for a standard monster.	
class BasicMonster:
	#TAKE TURN processes a standard monster's turn. If you can see it, it can see you, and it will
	#move toward you.
	def takeTurn(self):
		monster = self.owner
		if libtcod.map_is_in_fov(fovMap, monster.x, monster.y):
			#If the monster is far away, it moves toward the player.
			if monster.distanceTo(player) >= 2:
				monster.moveTowards(player.x, player.y)
				
			#if the monster is close enough, and the player is alive, the monster attacks.
			elif player.fighter.cond > 0:
				monster.fighter.attack(player)

#The ConfusedMonster AI module is used for a monster afflicted with confusion.
class ConfusedMonster:
	def __init__(self, oldAI, numberOfTurns = defs.CONFUSE_NUM_TURNS):
		self.oldAI = oldAI
		self.numberOfTurns = numberOfTurns
		
	#TAKE TURN processes a confused monster's turn. If the confusion has not worn off, the monster wanders
	#randomly and does not attack.
	def takeTurn(self):
		if self.numberOfTurns > 0:
			self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
			self.numberOfTurns -= 1
			
		else:
			#When confusion wears off, the previous AI will be restored, and the confused
			#AI will be deleted due to not being referenced anymore.
			self.owner.ai = self.oldAI
			message("The " + self.owner.name + " is no longer confused.", libtcod.red)
		
#The Item class describes an object that can be picked up and used by the player.				
class Item:
	#INIT constructs the item component.
	def __init__(self, bloat = 0, useEffect = None):
		self.bloat = bloat
		self.useEffect = useEffect
	
	#PICKUP removes the item from the map and adds the item to the player's inventory.
	def pickup(self):
		#if len(inventory) >= 26:
		if len(inventory) >= defs.INVENTORY_LIMIT:
			message("Your inventory is full.", libtcod.dark_yellow)
		else:
			inventory.append(self.owner)
			objects.remove(self.owner)
			message(self.owner.name + " added to inventory.", libtcod.yellow)
			#Special case: automatically equip the picked up item if the corresponding slot is empty
			equipment = self.owner.equipment
			if equipment and getEquippedInSlot(equipment.slot) is None:
				equipment.equip()
	
	#USE evokes the item's use function.
	def use(self):
		if self.owner.equipment:
			self.owner.equipment.toggleEquip()
			return
	
		if self.useEffect is None:
			message("Zilla cannot use the " + self.owner.name + " now.")
		else:
			if self.useEffect() != "cancel":
				if self.useEffect() == "eat":
					#This means that the item was food and Zilla successfully ate it
					addedWeight = self.bloat #* (player.fighter.hits / player.fighter.cond)
					player.weight += addedWeight
					message(script.zillaEats("eat", self.owner.name, addedWeight), libtcod.purple)
							
				if self.useEffect() == "drink":
					#This means that the item was a drink and Zilla successfully drank it
					addedWeight = self.bloat #* (player.fighter.hits / player.fighter.cond)
					player.weight += addedWeight
					message(script.zillaEats("drink", self.owner.name, self.bloat), libtcod.purple)
					
				#Destroy the item after use, unless it was cancelled.
				inventory.remove(self.owner) 
	
	#DROP removes the item from the player's inventory and adds it to the map objects.
	def drop(self):
		if self.owner.equipment:
			self.owner.equipment.unequip()
		objects.append(self.owner)
		inventory.remove(self.owner)
		self.owner.x = player.x
		self.owner.y = player.y
		message("You dropped a " + self.owner.name + ".", libtcod.yellow)
	
class Equipment:
	def __init__(self, slot, atkBonus = 0, dfnBonus = 0, minDamBonus = 0, maxDamBonus = 0, hpBonus = 0, 
		spptBonus = 0):
		self.slot = slot
		self.atkBonus = atkBonus
		self.dfnBonus = dfnBonus
		self.minDamBonus = minDamBonus
		self.maxDamBonus = maxDamBonus
		self.hpBonus = hpBonus
		self.spptBonus = spptBonus
		self.isWorn = False
		
	def toggleEquip(self):
		if self.isWorn:
			self.unequip()
		else:
			self.equip()
			
	def equip(self):
		oldEquipment = getEquippedInSlot(self.slot)
		if oldEquipment is not None:
			oldEquipment.unequip()
		self.isWorn = True
		message("Zilla puts on the " + self.owner.name + ".", libtcod.pink)
		
	def unequip(self):
		if not self.isWorn:
			return
		self.isWorn = False
		message("Zilla takes off the " + self.owner.name + ".", libtcod.pink)
	
#The Tile class describes a given tile on the map and its properties.
class Tile:
	#INIT initializes and constructs the tile with the given parameters.
	def __init__(self, blocked, blockSight = None):
		self.blocked = blocked
		self.explored = False
		
		#By default, if a tile is blocked, it will also block line of sight.
		if blockSight is None: blockSight = blocked
		self.blockSight = blockSight

#The Rectangle class defines a rectangle of tiles on the map, and is used to characterize a room.
class Rectangle:
	#INIT constructs a rectangle by taking the top-left coordinates in tiles and its size, to define
	#it in terms of two points - the top-left (x1,y1) and the bottom-right (x2,y2).
	def __init__(self, x, y, width, height):
		self.x1 = x
		self.y1 = y
		self.x2 = x + width
		self.y2 = y + height
		
	#CENTER returns the center coordinates of the rectangle.
	def center(self):
		centerX = (self.x1 + self.x2) / 2
		centerY = (self.y1 + self.y2) / 2
		return (centerX, centerY)
	
	#INTERSECT returns true if this rectangle intersects with another one.
	def intersect(self, other):
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
			self.y1 <= other.y2 and self.y2 >= other.y1)
	
#########################################################################################################
# [BASIC GAME FUNCTIONS]                                                                                #
#########################################################################################################			
			
def startNewGame():
	global player, inventory, messageLog, gameState, dungeonLevel
	
	#Create an object representing the player.
	fighterComponent = Fighter(hp = 64, aura = 24, atk = 2, dfn = 2, minDamage = 2, maxDamage = 3, xp = 0, deathEffect = playerDeath)
	player = Object(0, 0, defs.gZilla, "Zilla", defs.cZilla, desc = defs.DESC_ZILLA, blocks = True, fighter = fighterComponent)
	
	player.level = 1
	player.weight = 120
	
	#Generate dungeon and FOV maps, although at this point it is not drawn to the screen.
	dungeonLevel = 1
	makeMap()
	initializeFOV()
	
	#Set up the game state and instantiate the player's inventory.
	gameState = "playing"
	inventory = []
	
	#Create the list of game messages and their colors, which begins empty.
	messageLog = []
	message("[SIMULATION COMMENCING]", libtcod.cyan)
	
	#Initial equipment. The equipment's isWorn is forced True to suppress the "puts on" message.
	startingBikini = copy.deepcopy(I_SHIFTER_SKIVVIES)
	inventory.append(startingBikini)
	startingBikini.equipment.isWorn = True
	inventory.append(copy.deepcopy(I_POTION_MINORGROWTH))
	
def initializeFOV():
	global fovNeedsToBeRecomputed, fovMap
	fovNeedsToBeRecomputed = True
	
	#Unexplored areas start black, which is the default background color.
	libtcod.console_clear(con)
	
	#Create the FOV map, according to the generated dungeon map.
	fovMap = libtcod.map_new(defs.MAP_WIDTH, defs.MAP_HEIGHT)
	for y in range(defs.MAP_HEIGHT):
		for x in range(defs.MAP_WIDTH):
			libtcod.map_set_properties(fovMap, x, y, not map[x][y].blockSight, not map[x][y].blocked)

def playGame():
	global key, mouse
	
	playerAction = None
	
	mouse = libtcod.Mouse()
	key = libtcod.Key()
	while not libtcod.console_is_window_closed():
		#Render the screen.
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
		renderAll()
		
		libtcod.console_flush()
		checkLevelup()
		
		#Erase all objects at their old locations, before they move.
		for object in objects:
			object.clear()
			
		#Handle keys and exit the game if needed.
		playerAction = handleKeys()
		if playerAction == "exit":
			saveGame()
			break
		
		#Let monsters take their turn.
		if gameState == "playing" and playerAction != "no turn taken":
			for object in objects:
				if object.ai:
					object.ai.takeTurn()
					
def mainMenu():
	#img = libtcod.image_load("menu_background1.png")
	
	while not libtcod.console_is_window_closed():
		#Show the background image, at twice the regular console resolution.
		#libtcod.image_blit_2x(img, 0, 0, 0)
		libtcod.console_clear(0)
		
		#Show the game's title.
		libtcod.console_set_default_foreground(0, defs.cZilla)
		libtcod.console_print_ex(0, defs.SCREEN_WIDTH / 2, defs.SCREEN_HEIGHT / 2 - 6, libtcod.BKGND_NONE,
			libtcod.CENTER, "BIGGER IS BETTER")
		libtcod.console_print_ex(0, defs.SCREEN_WIDTH / 2, defs.SCREEN_HEIGHT / 2 - 5, libtcod.BKGND_NONE,
			libtcod.CENTER, "the Shapeshifting Roguelike")
		libtcod.console_print_ex(0, defs.SCREEN_WIDTH / 2, defs.SCREEN_HEIGHT - 2, libtcod.BKGND_NONE,
			libtcod.CENTER, "2014 Studio Draconis")
		
		#Show options and wait for the player's choice.
		choice = menu('', ["Start a New Simulation", "Continue a Previous Experiment", "Quit"], 40)
		
		if choice == 0: #NEW GAME
			startNewGame()
			playGame()
		if choice == 1: #LOAD GAME
			try:
				loadGame()
			except:
				announce("\n No saved simulation data to load. \n", 24)
				continue
			playGame()
		elif choice == 2: #QUIT
			break

#This function saves the game by opening a new, empty Shelve - overwriting an old one if necessary -
#and writing the game data to it.			
def saveGame():
	file = shelve.open("zillagame", "n")
	file["map"] = map
	file["objects"] = objects
	file["playerIndex"] = objects.index(player)
	file["inventory"] = inventory
	file["messageLog"] = messageLog
	file["gameState"] = gameState
	file["stairsIndex"] = objects.index(stairsDown)
	file["dungeonLevel"] = dungeonLevel
	file.close()
	
#This function loads a game file by opening a saved shelve.
def loadGame():
	global map, objects, player, inventory, messageLog, gameState, stairsDown, dungeonLevel
	
	file = shelve.open("zillagame", "r")
	map = file["map"]
	objects = file["objects"]
	player = objects[file["playerIndex"]]
	inventory = file["inventory"]
	messageLog = file["messageLog"]
	gameState = file["gameState"]
	stairsDown = objects[file["stairsIndex"]]
	dungeonLevel = file["dungeonLevel"]
	file.close()
	
	initializeFOV()
	
#########################################################################################################
# [COMMANDS AND EVENT HANDLERS]                                                                         #
#########################################################################################################
	
#This function controls the player's movement and attack actions.
def zillaMove(directionX, directionY):
	global fovNeedsToBeRecomputed
	
	#The coordinates the player is moving to, or attacking toward
	x = player.x + directionX
	y = player.y + directionY
	
	#Try to find an attackable object there
	target = None
	for object in objects: 
		if object.fighter and object.x == x and object.y == y:
			target = object
			break
	
	#Attack if a target is found, move otherwise.
	if target is not None:
		player.fighter.attack(target)
	else:
		player.move(directionX, directionY)
		fovNeedsToBeRecomputed = True
			
def handleKeys():
	global fovNeedsToBeRecomputed, keys
	
	keyChar = chr(key.c)
	
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt-Enter toggles fullscreen.
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	elif key.vk == libtcod.KEY_ESCAPE:
		#Escape exits the game.
		return "exit"
	
	if gameState == "playing":
		#movement keys
		#if libtcod.console_is_key_pressed(libtcod.KEY_UP):
		if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
			zillaMove(0,-1) #North
		elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
			zillaMove(0,1) #South
		elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
			zillaMove(-1,0) #West
		elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
			zillaMove(1,0)	#East
		elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
			zillaMove(-1, -1) #Northwest
		elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
			zillaMove(1, -1) #Northeast
		elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
			zillaMove(-1, 1) #Southwest
		elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
			zillaMove(1, 1) #Southeast
		elif keyChar == "." or key.vk == libtcod.KEY_KP5:
			pass  #Do nothing this turn.
		else:
			#Test for other keys.
			if keyChar == "g":
				#(G)et picks up an item.
				for object in objects:
					if object.x == player.x and object.y == player.y and object.item:
						object.item.pickup()
						break
			if keyChar == ">":
				#Descend stairs, if the player is on them.
				if stairsDown.x == player.x and stairsDown.y == player.y:
					nextLevel()
					
			if keyChar == "1":
				if len(inventory) >= 1:
					chosenItem = itemMenu(inventory[0])
			if keyChar == "2":
				if len(inventory) >= 2:
					chosenItem = itemMenu(inventory[1])
			if keyChar == "3":
				if len(inventory) >= 3:
					chosenItem = itemMenu(inventory[2])
			if keyChar == "4":
				if len(inventory) >= 4:
					chosenItem = itemMenu(inventory[3])
			if keyChar == "5":
				if len(inventory) >= 5:
					chosenItem = itemMenu(inventory[4])
			if keyChar == "6":
				if len(inventory) >= 6:
					chosenItem = itemMenu(inventory[5])
			if keyChar == "7":
				if len(inventory) >= 7:
					chosenItem = itemMenu(inventory[6])
			if keyChar == "8":
				if len(inventory) >= 8:
					chosenItem = itemMenu(inventory[7])

			return "no turn taken"

def getNamesUnderMouse():
	global mouse
	
	#Return a string with the names of all objects under the mouse cursor.
	(x, y) = (mouse.cx, mouse.cy)
	
	#Create a list with the names of all the objects at the mouse's coordinates. These objects must
	#be within the player's FOV, however, or else they would be able to detect things through walls.
	#This uses the if variant of a list comprehension.
	names = [obj.name for obj in objects
		if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fovMap, obj.x, obj.y)]
	
	#Join the names, separated by commas, and return the list.
	names = ", ".join(names)
	return names
	
#########################################################################################################
# [RENDERING FUNCTIONS]                                                                                 #
#########################################################################################################
	
#This function displays a window with a string (header) at the top, and a list of strings (options).
#The height of the menu is implicit as it depends on the header height and number of options, but the
#width is defined in the method. A letter will be shown next to each option (A, B, etc) so the user can
#select it by pressing that key. The function returns the index of the selected option, starting with
#zero, or None if the user pressed a different key.
def menu(header, options, width):
	if len(options) > 26: raise ValueError("Cannot have a menu with more than twenty-six options.")
	
	#Calculate total height for the header (after auto-wrap) and one line per option.
	headerHeight = libtcod.console_get_height_rect(con, 0, 0, width, defs.SCREEN_HEIGHT, header)
	if header == "":
		headerHeight = 0
	height = len(options) + headerHeight
	
	#Create an off-screen console that represents the menu's window.
	window = libtcod.console_new(width, height)
	
	#Print the header, with auto-wrap.
	libtcod.console_set_default_foreground(window, libtcod.white)
	libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
	
	#Print all the options, one by one. ORD and CHR are built-in Python functions. chr(i) returns a string
	#of one character whose ASCII code is in the integer i - for example, chr(97) returns "a". ord(c) is
	#the opposite - given a string of length one, it returns an integer representing the Unicode code
	#point of the character - for example, ord("a") returns 97.
	y = headerHeight
	letterIndex = ord("a")
	for optionText in options:
		text = "(" + chr(letterIndex) + ") " + optionText
		libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
		y += 1
		letterIndex += 1
		
	#Blit the contents of window to the root console. The last two parameters passed to console_blit
	#define the foreground and background transparency, respectively.
	x = defs.SCREEN_WIDTH / 2 - width / 2
	y = defs.SCREEN_HEIGHT / 2 - height / 2
	libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
	
	#Present the root console to the player and wait for a keypress.
	libtcod.console_flush()
	key = libtcod.console_wait_for_keypress(True)
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt-Enter toggles fullscreen.
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	
	#Convert the ASCII code to an index. If it corresponds to an option, return it, otherwise return None
	index = key.c - ord("a")
	if index >= 0 and index < len(options): 
		return index
	
	return None
	
#This function announces something using the menu function as an impromptu message box.
def announce(text, width = 50):
	menu(text, [], width)
	
def itemMenu(activeItem):
	#Create an off-screen console that represents the item window.
	width = defs.ITEM_WINDOW_WIDTH
	descHeight = libtcod.console_get_height_rect(con, 0, 0, width, defs.SCREEN_HEIGHT, "\n" + activeItem.desc + "\n")
	height = descHeight + 4
	itemWindow = libtcod.console_new(width, height)
	
	libtcod.console_set_default_background(itemWindow, libtcod.darkest_flame)
	libtcod.console_clear(itemWindow)
	libtcod.console_set_default_foreground(itemWindow, libtcod.white)
	libtcod.console_print_frame(itemWindow, 0, 0, width, height, False, libtcod.BKGND_NONE, activeItem.name)
	libtcod.console_print_rect_ex(itemWindow, 1, 1, width - 2, height, libtcod.BKGND_NONE, libtcod.LEFT, activeItem.desc)
	
	textY = descHeight
	libtcod.console_print_ex(itemWindow, 1, textY, libtcod.BKGND_NONE, libtcod.LEFT, "(U)se")
	libtcod.console_print_ex(itemWindow, 1, textY + 1, libtcod.BKGND_NONE, libtcod.LEFT, "(D)rop")
	
	x = defs.SCREEN_WIDTH / 2 - width / 2
	y = defs.SCREEN_HEIGHT / 2 - height / 2
	libtcod.console_blit(itemWindow, 0, 0, width, height, 0, x, y, 0.9, 0.7)
	
	#Present the root console to the player and wait for a keypress.
	libtcod.console_flush()
	key = libtcod.console_wait_for_keypress(True)
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt-Enter toggles fullscreen.
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	
	keyChar = chr(key.c)
	if keyChar == "u":
		result = activeItem.item.use()
	elif keyChar == "d":
		result = activeItem.item.drop()
		
	return None

#This function shows a menu with each item of the player's inventory as an option.
def inventoryMenu(header):
	if len(inventory) == 0:
		options = ["Inventory is empty."]
	else:
		options = []
		for item in inventory:
			text = item.name
			#Show additional information, in case it's equipped
			if item.equipment and item.equipment.isWorn:
				text = text + " (Equipped)"
			options.append(text)
		
	index = menu(header, options, defs.INVENTORY_WIDTH)
	
	#If an item was chosen, return it.
	if index is None or len(inventory) == 0: 
		return None
	return inventory[index].item
	
#This function displays messages in the message log on the status bar.
def message(newMessage, color = libtcod.white):
	#Split the message if necessary, among multiple lines. This uses Python's textwrap module.
	newMessageLines = textwrap.wrap(newMessage, defs.MESSAGE_WIDTH)
	
	for line in newMessageLines:
		#If the buffer is full, remove the first line to make room for the new one.
		if len(messageLog) == defs.MESSAGE_HEIGHT:
			del messageLog[0]
		
		#Add the new line as a tuple, with the text and the color.
		messageLog.append( (line, color) )

def showObjectInfoPanel():
	global mouse
	
	#Return a string with the names of all objects under the mouse cursor.
	(x, y) = (mouse.cx, mouse.cy)
	
	#Create a list with the names of all the objects at the mouse's coordinates. These objects must
	#be within the player's FOV, however, or else they would be able to detect things through walls.
	objectsAtMouse = []
	for obj in objects:
		if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fovMap, obj.x, obj.y):
			objectsAtMouse.append(obj)
	
	#The info panel should only be prepared and shown if the list of objects is NOT empty. The thinking
	#here is that due to dynamic typing, an empty list is false, and a list that is not empty is not false.
	#A more explicit way of testing for emptiness would be if len(objectsAtMouse) != 0.
	if objectsAtMouse:
		infopanelY = 2
		libtcod.console_set_default_background(infoPanel, libtcod.black)
		libtcod.console_clear(infoPanel)
		libtcod.console_print_frame(infoPanel, 0, 0, defs.INFO_PANEL_WIDTH, defs.MAP_HEIGHT, False, libtcod.BKGND_SET)
		
		for obj in objectsAtMouse:
			libtcod.console_set_default_foreground(infoPanel, libtcod.cyan)
			libtcod.console_print_ex(infoPanel, defs.INFO_PANEL_WIDTH / 2, infopanelY, libtcod.BKGND_NONE, libtcod.CENTER, obj.name)
			infopanelY += 2
			libtcod.console_set_default_foreground(infoPanel, libtcod.white)
			descHeight = libtcod.console_get_height_rect(con, 0, 0, defs.INFO_PANEL_WIDTH - 4, defs.SCREEN_HEIGHT, obj.desc)
			libtcod.console_print_rect_ex(infoPanel, 2, infopanelY, defs.INFO_PANEL_WIDTH - 4, descHeight, libtcod.BKGND_NONE, libtcod.LEFT, obj.desc)
			infopanelY += descHeight + 1
			if obj != player and obj.fighter:
				renderStatusBar(infoPanel, 2, infopanelY, defs.INFO_PANEL_WIDTH - 4, "Health", obj.fighter.cond, obj.fighter.hits, 
					libtcod.red, libtcod.darkest_red, "standard")
				infopanelY += 2
				
		libtcod.console_blit(infoPanel, 0, 0, 0, 0, 0, defs.MAP_WIDTH / 2, 0, 0.9, 0.7)
	
#This function renders a generic status bar, used for a health bar, a mana bar, experience bar, etc.
def renderStatusBar(targetConsole, x, y, totalWidth, name, value, maximum, barColor, backColor, barType = "standard"):
	#First, calculate width of the bar.
	barWidth = int(float(value) / maximum * totalWidth)
	
	#Render the background first.
	libtcod.console_set_default_background(targetConsole, libtcod.black)
	libtcod.console_rect(targetConsole, x, y, totalWidth, 1, False, libtcod.BKGND_SCREEN)
	libtcod.console_set_default_background(targetConsole, backColor)
	libtcod.console_rect(targetConsole, x, y, totalWidth, 1, False, libtcod.BKGND_SCREEN)
	
	#Now render the bar on top.
	libtcod.console_set_default_background(targetConsole, barColor)
	if barWidth > 0:
		libtcod.console_rect(targetConsole, x, y, barWidth, 1, False, libtcod.BKGND_SCREEN)
	
	#The barType variable determines how the bar's values are written on top of the bar.
	
	if barType == "size":
		#SIZE is used for Zilla's health bar. It converts her health, in inches, to a foot-and-inches readout.
		libtcod.console_set_default_foreground(targetConsole, libtcod.white)
		libtcod.console_print_ex(targetConsole, x + totalWidth / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
			convertHealthToSize(value) + " / " + convertHealthToSize(maximum))
	elif barType == "standard":
		#STANDARD places the value and maximum centered over the bar.
		libtcod.console_set_default_foreground(targetConsole, libtcod.white)
		libtcod.console_print_ex(targetConsole, x + totalWidth / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, 
			name + ": " + str(value) + "/" + str(maximum))
	elif barType == "no-name":
		#NO NAME places the value and maximum centered over the bar, without the bar name.
		libtcod.console_set_default_foreground(targetConsole, libtcod.white)
		libtcod.console_print_ex(targetConsole, x + totalWidth / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, 
			str(value) + " / " + str(maximum))
	elif barType == "weight":
		#WEIGHT is used for Zilla's weight bar. It converts her weight to a string in pounds, or tons if
		#necessary.
		libtcod.console_set_default_foreground(targetConsole, libtcod.white)
		libtcod.console_print_ex(targetConsole, x + totalWidth / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, 
			convertWeight(value))
		
#This function draws the map and all objects.
def renderAll():
	global fovNeedsToBeRecomputed

	if fovNeedsToBeRecomputed:
		#If this is true, then we must recalculate the field of view and render the map.
		fovNeedsToBeRecomputed = False
		libtcod.map_compute_fov(fovMap, player.x, player.y, defs.TORCH_RADIUS, defs.FOV_LIGHT_WALLS, defs.FOV_ALGO)
		
		#Iterate through the list of map tiles and set their background colors.
		for y in range(defs.MAP_HEIGHT):
			for x in range(defs.MAP_WIDTH):
				visible = libtcod.map_is_in_fov(fovMap, x, y)
				wall = map[x][y].blockSight
				if not visible:
					#If a tile is out of the player's field of view...
					if map[x][y].explored:
						#...it will only be drawn if the player has explored it
						if wall:
							libtcod.console_set_char_background(con, x, y, defs.cDarkWall, libtcod.BKGND_SET)
						else:
							libtcod.console_set_char_background(con, x, y, defs.cDarkGround, libtcod.BKGND_SET)
				else:
					#If a tile is in the player's field of view...
					if wall:
						libtcod.console_set_char_background(con, x, y, defs.cLitWall, libtcod.BKGND_SET)
					else:
						libtcod.console_set_char_background(con, x, y, defs.cLitGround, libtcod.BKGND_SET)
					map[x][y].explored = True
	
	#Draw all objects in the list, except the player, which needs to be drawn last.
	for object in objects:
		if object != player:
			object.draw()
	player.draw()
		
	#Blit the contents of con to the root console.
	libtcod.console_blit(con, 0, 0, defs.MAP_WIDTH, defs.MAP_HEIGHT, 0, 0, 0)
	
	#Prepare to render the status panel.
	libtcod.console_set_default_background(msgPanel, libtcod.black)
	libtcod.console_clear(msgPanel)
	libtcod.console_set_default_foreground(msgPanel, libtcod.white)
	libtcod.console_print_frame(msgPanel, 0, 0, defs.MESSAGE_PANEL_WIDTH, defs.MESSAGE_PANEL_HEIGHT, False, libtcod.BKGND_NONE, "BIGGER IS BETTER")
	
	#Print the message log, one line at a time.
	y = 1
	for (line, color) in messageLog:
		libtcod.console_set_default_foreground(msgPanel, color)
		libtcod.console_print_ex(msgPanel, 1, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
		y += 1
	
	#Prepare the sidebar panel.
	libtcod.console_set_default_background(sidebar, libtcod.darkest_flame)
	libtcod.console_clear(sidebar)
	#libtcod.console_rect(sidebar, 0, 0, data.SIDE_WIDTH, data.SIDE_HEIGHT, False, libtcod.BKGND_SET)
	libtcod.console_set_default_foreground(sidebar, libtcod.white)
	libtcod.console_print_frame(sidebar, 0, 0, defs.SIDEBAR_WIDTH, defs.SIDEBAR_HEIGHT, False, libtcod.BKGND_SET)
	
	libtcod.console_set_color_control(libtcod.COLCTRL_1, libtcod.green, libtcod.darkest_flame)
	xpToAdvance = defs.ADVANCE_BASE + player.level * defs.ADVANCE_FACTOR
	equippedArmor = getEquippedInSlot("bikini")
	equippedArmorName = ""
	if equippedArmor is not None:
		equippedArmorName = equippedArmor.owner.name
		
	sidebarY = 2
	libtcod.console_set_default_foreground(sidebar, libtcod.cyan)
	libtcod.console_print_ex(sidebar, defs.SIDEBAR_WIDTH / 2, sidebarY, libtcod.BKGND_NONE, libtcod.CENTER, "-VITALS-")
	
	sidebarY += 2
	libtcod.console_set_default_foreground(sidebar, libtcod.white)
	libtcod.console_print_ex(sidebar, 2, sidebarY, libtcod.BKGND_NONE, libtcod.LEFT, "Size")
	renderStatusBar(sidebar, 2, sidebarY + 1, defs.BAR_WIDTH, "Health", player.fighter.cond, player.fighter.hits, 
		libtcod.red, libtcod.darkest_red, "size")
		
	sidebarY += 3
	libtcod.console_print_ex(sidebar, 2, sidebarY, libtcod.BKGND_NONE, libtcod.LEFT, "Gurgle")
	renderStatusBar(sidebar, 2, sidebarY + 1, defs.BAR_WIDTH, "Gurgle", player.fighter.aura, player.fighter.sppt, 
		libtcod.blue, libtcod.darkest_blue, "no-name")
		
	sidebarY += 3
	libtcod.console_print_ex(sidebar, 2, sidebarY, libtcod.BKGND_NONE, libtcod.LEFT, "Weight")
	renderStatusBar(sidebar, 2, sidebarY + 1, defs.BAR_WIDTH, "Weight", player.weight, player.weight, 
		libtcod.purple, libtcod.darkest_purple, "weight")
		
	sidebarY += 3
	libtcod.console_print_ex(sidebar, 2, sidebarY, libtcod.BKGND_NONE, libtcod.LEFT, "Mutation")
	libtcod.console_set_default_foreground(sidebar, libtcod.green)
	libtcod.console_print_ex(sidebar, defs.SIDEBAR_WIDTH - 3, sidebarY, libtcod.BKGND_NONE, libtcod.RIGHT, str(player.level))
	libtcod.console_set_default_foreground(sidebar, libtcod.white)
	renderStatusBar(sidebar, 2, sidebarY + 1, defs.BAR_WIDTH, "Mutation", player.fighter.xp, xpToAdvance, 
		libtcod.green, libtcod.darkest_green, "no-name")
	
	sidebarY += 4
	libtcod.console_set_default_foreground(sidebar, libtcod.cyan)
	libtcod.console_print_ex(sidebar, defs.SIDEBAR_WIDTH / 2, sidebarY, libtcod.BKGND_NONE, libtcod.CENTER, "-STATS-")
	libtcod.console_set_default_foreground(sidebar, libtcod.white)
	
	sidebarY += 2
	libtcod.console_print_ex(sidebar, 2, sidebarY, libtcod.BKGND_NONE, libtcod.LEFT, "Attack")
	libtcod.console_set_default_foreground(sidebar, libtcod.green)
	libtcod.console_print_ex(sidebar, defs.SIDEBAR_WIDTH - 3, sidebarY + 1, libtcod.BKGND_NONE, libtcod.RIGHT, str(player.fighter.atk))
	libtcod.console_set_default_foreground(sidebar, libtcod.white)
	
	sidebarY += 3
	libtcod.console_print_ex(sidebar, 2, sidebarY, libtcod.BKGND_NONE, libtcod.LEFT, "Defense")
	libtcod.console_set_default_foreground(sidebar, libtcod.green)
	libtcod.console_print_ex(sidebar, defs.SIDEBAR_WIDTH - 3, sidebarY + 1, libtcod.BKGND_NONE, libtcod.RIGHT, str(player.fighter.dfn))
	libtcod.console_set_default_foreground(sidebar, libtcod.white)
	
	sidebarY += 3
	libtcod.console_print_ex(sidebar, 2, sidebarY, libtcod.BKGND_NONE, libtcod.LEFT, "Damage")
	libtcod.console_set_default_foreground(sidebar, libtcod.green)
	libtcod.console_print_ex(sidebar, defs.SIDEBAR_WIDTH - 3, sidebarY + 1, libtcod.BKGND_NONE, libtcod.RIGHT, str(player.fighter.minDamage) + " to " + str(player.fighter.maxDamage))
	libtcod.console_set_default_foreground(sidebar, libtcod.white)
	
	sidebarY += 3
	libtcod.console_print_ex(sidebar, 2, sidebarY, libtcod.BKGND_NONE, libtcod.LEFT, "Laboratory Level")
	libtcod.console_set_default_foreground(sidebar, libtcod.green)
	libtcod.console_print_ex(sidebar, defs.SIDEBAR_WIDTH - 3, sidebarY + 1, libtcod.BKGND_NONE, libtcod.RIGHT, str(dungeonLevel))
	libtcod.console_set_default_foreground(sidebar, libtcod.white)
	
	sidebarY += 4
	libtcod.console_set_default_foreground(sidebar, libtcod.cyan)
	libtcod.console_print_ex(sidebar, defs.SIDEBAR_WIDTH / 2, sidebarY, libtcod.BKGND_NONE, libtcod.CENTER, "-INVENTORY-")
	libtcod.console_set_default_foreground(sidebar, libtcod.white)
	
	sidebarY += 2
	for x in range(defs.INVENTORY_LIMIT):
		libtcod.console_set_default_foreground(sidebar, libtcod.yellow)
		libtcod.console_print_ex(sidebar, 2, sidebarY, libtcod.BKGND_NONE, libtcod.LEFT, str(x + 1))
		sidebarY += 1
	
	sidebarY -= defs.INVENTORY_LIMIT
	for i in range(len(inventory)):
		text = inventory[i].name
		
		if inventory[i].equipment and inventory[i].equipment.isWorn:
			libtcod.console_set_default_foreground(sidebar, libtcod.pink)
		else:
			libtcod.console_set_default_foreground(sidebar, libtcod.white)
			
		libtcod.console_print_ex(sidebar, 4, sidebarY, libtcod.BKGND_NONE, libtcod.LEFT, text[:15])
		sidebarY += 1
	
	#Check for objects under the mouse cursor, and display a readout for them.
	showObjectInfoPanel()
	
	#Blit the contents of panel to the root console.
	libtcod.console_blit(sidebar, 0, 0, 0, 0, 0, defs.MAP_WIDTH, 0)
	libtcod.console_blit(msgPanel, 0, 0, defs.SCREEN_WIDTH, defs.MESSAGE_PANEL_HEIGHT, 0, 0, defs.MESSAGE_PANEL_Y)
		
#########################################################################################################
# [ACTOR DEATH FUNCTIONS]                                                                               #
#########################################################################################################	
	
def playerDeath(player):
	#When Zilla is defeated, the game ends.
	global gameState
	
	player.glyph = defs.gSpace
	
	message("Zilla shrinks uncontrollably down to a microscopic size!", libtcod.darker_green)
	message("Oh well... you win some, you lose some. When's my next meal? I'm starving!", libtcod.sepia)
	message("[SIMULATION COMPLETE]", libtcod.cyan)
	gameState = "dead"

def monsterDeath(monster):
	#When a monster is defeated, it disappears from the game.
	message("The " + monster.name + " disappears in a puff of smoke!", libtcod.purple)
	objects.remove(monster)
	
#########################################################################################################
# [ITEM USAGE FUNCTIONS]                                                                                #
#########################################################################################################
	
#This function controls a basic food item with no side effects.
def genericEat():
	return "eat"
	
#This function controls a basic drink with no side effects.
def genericDrink():
	return "drink"

#This function heals Zilla.
def growPotion():
	if player.fighter.cond == player.fighter.hits:
		message("I'm already at full size. This potion won't make me any bigger.", defs.cZilla)
		return "cancel"
	
	message("Zilla drinks the potion and grows bigger!", libtcod.red)
	player.fighter.heal(player.fighter.hits / 2)
	
#This function controls the lightning bolt spell. It finds the closest enemy within a maximum range and
#damages it.
def castLightning():
	monster = closestMonster(defs.LIGHTNING_RANGE)
	if monster is None:
		message("No enemy is close enough to strike.", libtcod.red)
		return "cancel"
	
	message("You unfurl the scroll, and lightning erupts from it! The bolt strikes the " 
		+ monster.name + " for " + str(defs.LIGHTNING_DAMAGE) + " points of damage.", libtcod.light_blue)
	monster.fighter.takeDamage(defs.LIGHTNING_DAMAGE)

#This function asks the player for a target monster and then confuses it, disrupting its AI.
def castConfuse():
	#Ask the player for a target to confuse.
	message("Left-click an enemy to confuse it, or right-click to cancel.", libtcod.light_cyan)
	monster = targetMonster(defs.CONFUSE_RANGE)
	if monster is None:
		return "cancel"
	
	#Replace the affected monster's AI with a confused AI.
	oldAI = monster.ai
	monster.ai = ConfusedMonster(oldAI)
	monster.ai.owner = monster
	message("The eyes of the " + monster.name + " look vacant, as it starts to stumble around in a daze.",
		libtcod.light_green) 
	
#This function casts a large area-of-effect damage spell centered on the player.
def castAreaShrink():
	(x,y) = (player.x, player.y)
	
	for obj in objects:
		if obj.distance(x, y) <= defs.SHRINK_CHANT_RADIUS and obj.fighter:
			message("The " + obj.name + " " + script.selectFromList(script.shrinkNoises) + "!", libtcod.purple)
			damageAmount = rnd(defs.SHRINK_CHANT_MIN_DAMAGE, defs.SHRINK_CHANT_MAX_DAMAGE)
			damageAmount = damageAmount * player.level
			obj.fighter.takeDamage(damageAmount)

#This function asks the player for a target tile and then casts a large area-of-effect damage spell. 	
def castFireball():
	message("Left-click a target tile for the fireball, or right-click to cancel.", libtcod.light_cyan)
	(x,y) = targetTile()
	if x is None: 
		return "cancel"
	
	message("The fireball explodes, burning everything within " + str(defs.FIREBALL_RADIUS) + " tiles.", 
		libtcod.orange)
	
	for obj in objects:
		if obj.distance(x, y) <= defs.FIREBALL_RADIUS and obj.fighter:
			message("The " + obj.name + " is burned for " + str(defs.FIREBALL_DAMAGE) + 
				" points of fire damage.", libtcod.orange)
			obj.fighter.takeDamage(defs.FIREBALL_DAMAGE)

#########################################################################################################
# [MONSTER TEMPLATES]                                                                                   #
# These templates must go after the majority of the script's function declarations as they depend on    #
# the declared functions.                                                                               #
#########################################################################################################

M_NEWT = Object(0, 0, defs.gLizard, "Newt", libtcod.blue, desc = defs.DESC_NEWT, blocks = True,
	fighter = Fighter(hp = 8, aura = 0, atk = 1, dfn = 1, minDamage = 1, maxDamage = 1, xp = 20, deathEffect = monsterDeath),
	ai = BasicMonster())
	
M_GECKO = Object(0, 0, defs.gLizard, "Gecko", libtcod.chartreuse, desc = defs.DESC_GECKO, blocks = True,
	fighter = Fighter(hp = 8, aura = 0, atk = 1, dfn = 2, minDamage = 1, maxDamage = 1, xp = 25, deathEffect = monsterDeath),
	ai = BasicMonster())
	
M_LIZARD = Object(0, 0, defs.gLizard, "Lizard", libtcod.green, desc = defs.DESC_LIZARD, blocks = True, 
	fighter = Fighter(hp = 12, aura = 0, atk = 2, dfn = 1, minDamage = 1, maxDamage = 2, xp = 25, deathEffect = monsterDeath), 
	ai = BasicMonster())

M_BELLYIMP = Object(0, 0, defs.gBellything, "Bellyimp", libtcod.purple, desc = defs.DESC_BELLYIMP, blocks = True,
	fighter = Fighter(hp = 10, aura = 0, atk = 3, dfn = 1, minDamage = 2, maxDamage = 4, xp = 50, deathEffect = monsterDeath),  
	ai = BasicMonster())

M_SNAKE = Object(0, 0, defs.gSnake, "Snake", libtcod.black, desc = defs.DESC_SNAKE, blocks = True,
	fighter = Fighter(hp = 8, aura = 0, atk = 2, dfn = 1, minDamage = 2, maxDamage = 2, xp = 30, deathEffect = monsterDeath),  
	ai = BasicMonster())
	
tierZeroMonsters = [M_NEWT, M_GECKO, M_LIZARD, M_BELLYIMP, M_SNAKE]

M_BELLYDEMON = Object(0, 0, defs.gBellything, "Bellydemon", libtcod.violet, blocks = True,
	fighter = Fighter(hp = 40, aura = 0, atk = 4, dfn = 3, minDamage = 3, maxDamage = 4, xp = 200, deathEffect = monsterDeath),  
	ai = BasicMonster())

M_DIRE_CHARR = Object(0, 0, defs.gCharr, "Dire Charr", libtcod.orange, blocks = True,
	fighter = Fighter(hp = 18, aura = 0, atk = 4, dfn = 2, minDamage = 2, maxDamage = 4, xp = 160, deathEffect = monsterDeath),  
	ai = BasicMonster())
	
M_ALLIGATOR = Object(0, 0, defs.gCrocodilian, "Alligator", libtcod.green, blocks = True,
	fighter = Fighter(hp = 22, aura = 0, atk = 3, dfn = 3, minDamage = 2, maxDamage = 6, xp = 180, deathEffect = monsterDeath),  
	ai = BasicMonster())
				
M_KANGAROO = Object(0, 0, defs.gMarsupial, "Kangaroo", libtcod.darker_sepia, blocks = True,
	fighter = Fighter(hp = 16, aura = 0, atk = 2, dfn = 2, minDamage = 2, maxDamage = 4, xp = 120, deathEffect = monsterDeath),  
	ai = BasicMonster())
				
M_CROCODILE = Object(0, 0, defs.gCrocodilian, "Crocodile", libtcod.darker_green, blocks = True,
	fighter = Fighter(hp = 22, aura = 0, atk = 3, dfn = 3, minDamage = 2, maxDamage = 6, xp = 180, deathEffect = monsterDeath),  
	ai = BasicMonster())

tierOneMonsters = [M_BELLYDEMON, M_DIRE_CHARR, M_ALLIGATOR, M_KANGAROO, M_CROCODILE]

#########################################################################################################
# [ITEM TEMPLATES]                                                                                      #
# These templates must go after the majority of the script's function declarations as they depend on    #
# the declared functions.                                                                               #
#########################################################################################################			
#Hamburger, Chicken, Pasta, Cake, Bread, Shrinkberry, Growberry, Toxic waste, Ice cream
I_BANANA = Object(0, 0, defs.gFood, "Banana", libtcod.yellow, desc = defs.DESC_BANANA, alwaysVisible = True,
	item = Item(bloat = defs.B_FRUIT, useEffect = genericEat))

I_APPLE = Object(0, 0, defs.gFood, "Apple", libtcod.red, desc = defs.DESC_APPLE, alwaysVisible = True,
	item = Item(bloat = defs.B_FRUIT, useEffect = genericEat))
	
I_PEAR = Object(0, 0, defs.gFood, "Pear", libtcod.light_green, desc = defs.DESC_PEAR, alwaysVisible = True,
	item = Item(bloat = defs.B_FRUIT, useEffect = genericEat))
	
I_ORANGE = Object(0, 0, defs.gFood, "Orange", libtcod.orange, desc = defs.DESC_ORANGE, alwaysVisible = True,
	item = Item(bloat = defs.B_FRUIT, useEffect = genericEat))
	
I_MANGO = Object(0, 0, defs.gFood, "Mango", libtcod.dark_orange, desc = defs.DESC_MANGO, alwaysVisible = True,
	item = Item(bloat = defs.B_FRUIT, useEffect = genericEat))

I_JUG_MILK = Object(0, 0, defs.gFood, "Jug of Milk", libtcod.white, desc = defs.DESC_JUG_MILK, alwaysVisible = True,
	item = Item(bloat = defs.B_GALLON, useEffect = genericDrink))

I_JUG_APPLEJUICE = Object(0, 0, defs.gFood, "Jug of Apple Juice", libtcod.light_yellow, desc = defs.DESC_JUG_APPLEJUICE, alwaysVisible = True,
	item = Item(bloat = defs.B_GALLON, useEffect = genericDrink))

I_JUG_ORANGEJUICE = Object(0, 0, defs.gFood, "Jug of Orange Juice", libtcod.orange, desc = defs.DESC_JUG_ORANGEJUICE, alwaysVisible = True,
	item = Item(bloat = defs.B_GALLON, useEffect = genericDrink))	

I_BLOATBERRY = Object(0, 0, defs.gFood, "Bloatberry", libtcod.purple, desc = defs.DESC_BLOATBERRY, alwaysVisible = True,
	item = Item(bloat = defs.B_BLOATBERRY, useEffect = genericEat))
	
I_KEG_COLA = Object(0, 0, defs.gBarrel, "Keg of Cola", libtcod.black, desc = defs.DESC_KEG_COLA, alwaysVisible = True,
	item = Item(bloat = defs.B_KEG, useEffect = genericDrink))
	
I_BARREL_COLA = Object(0, 0, defs.gBarrel, "Barrel of Cola", libtcod.darkest_sepia, desc = defs.DESC_BARREL_COLA, alwaysVisible = True,
	item = Item(bloat = defs.B_BARREL, useEffect = genericDrink))
	
food = [I_BANANA, I_APPLE, I_PEAR, I_ORANGE, I_MANGO, I_JUG_MILK, I_JUG_APPLEJUICE, I_JUG_ORANGEJUICE,
	I_BLOATBERRY, I_KEG_COLA, I_BARREL_COLA]

I_POTION_MINORGROWTH = Object(0, 0, defs.gPotion, "Potion of Minor Growth", libtcod.red, desc = defs.DESC_POTION_MINORGROWTH, alwaysVisible = True,
	item = Item(useEffect = growPotion))

potions = [I_POTION_MINORGROWTH]
	
#The Shifter Skivvies are Zilla's starting outfit and do not have equipment bonuses nor is it generated
#randomly.
I_SHIFTER_SKIVVIES = Object(0, 0, defs.gArmor, "Shifter Skivvies", libtcod.purple, desc = defs.DESC_SHIFTER_SKIVVIES, alwaysVisible = True,
	equipment = Equipment(slot = "bikini"))
	
I_FLORAL_BIKINI = Object(0, 0, defs.gArmor, "Floral Bikini", libtcod.pink, desc = defs.DESC_FLORAL_BIKINI, alwaysVisible = True,
	equipment = Equipment(slot = "bikini", dfnBonus = 1))
	
I_BRAWLER_BIKINI = Object(0, 0, defs.gArmor, "Brawler Bikini", libtcod.red, desc = defs.DESC_BRAWLER_BIKINI, alwaysVisible = True,
	equipment = Equipment(slot = "bikini", atkBonus = 2))
	
I_CHAINMAIL_BIKINI = Object(0, 0, defs.gArmor, "Chainmail Bikini", libtcod.dark_gray, desc = defs.DESC_CHAINMAIL_BIKINI, alwaysVisible = True,
	equipment = Equipment(slot = "bikini", dfnBonus = 3))
	
armors = [I_FLORAL_BIKINI, I_BRAWLER_BIKINI, I_CHAINMAIL_BIKINI]

#########################################################################################################
# [DUNGEON GENERATION AND POPULATION FUNCTIONS]                                                         #
#########################################################################################################

def carveRoom(room):
	global map
	
	#Go through the tiles in the rectangle and make them passable. Incrementing x1 and y1 by 1
	#ensures that there is always a one-tile wall around a room.
	for x in range(room.x1 + 1, room.x2):
		for y in range(room.y1 + 1, room.y2):
			map[x][y].blocked = False
			map[x][y].blockSight = False

#This function carves a horizontal tunnel of unblocked tiles.
def carveHorizontalTunnel(x1, x2, y):
	global map
	
	#MIN and MAX return the minimum and maximum of two given values, respectively. For loops only work
	#from a lower value to a higher value. Min and max ensure that, no matter which is lower, x1 or x2,
	#the for loop will work as intended.
	for x in range(min(x1, x2), max(x1, x2) + 1):
		map[x][y].blocked = False
		map[x][y].blockSight = False
			
#This function carves a vertical tunnel of floor tiles.
def carveVerticalTunnel(y1, y2, x):
	global map
	
	for y in range(min(y1, y2), max(y1, y2) + 1):
		map[x][y].blocked = False
		map[x][y].blockSight = False

#This function checks to see if a tile is blocked.
def isBlocked(x, y):
	#First, test the tile itself.
	if map[x][y].blocked:
		return True
	
	#Now, check for any blocking objects.
	for object in objects:
		if object.blocks and object.x == x and object.y == y:
			return True
	
	return False
		
def makeMap():
	global map, objects, stairsDown
	
	#First, instantiate the list of objects, with just the player at this point.
	objects = [player]
	
	#Fill the map with "blocked" tiles. This uses a construct called a list comprehension. When
	#making a list comprehension such as this, it is imperative to always call the constructor of
	#the objects that are being created. For example, if we attempted to first create a variable,
	#and then refer to that variable here, all elements in this list would point to that same variable.
	#Calling the constructor ensures that all of these Tiles are distinct instances.
	map = [[ Tile(True)
		for y in range(defs.MAP_HEIGHT) ]
			for x in range(defs.MAP_WIDTH) ]
	
	rooms = []
	numberOfRooms = 0
	
	for r in range(defs.MAX_ROOMS):
		#Random width and height.
		width = libtcod.random_get_int(0, defs.ROOM_MIN_SIZE, defs.ROOM_MAX_SIZE)
		height = libtcod.random_get_int(0, defs.ROOM_MIN_SIZE, defs.ROOM_MAX_SIZE)
		
		#Random position, without going out of the boundaries of the map
		x = libtcod.random_get_int(0, 0, defs.MAP_WIDTH - width - 1)
		y = libtcod.random_get_int(0, 0, defs.MAP_HEIGHT - height - 1)
		
		newRoom = Rectangle(x, y, width, height)
		
		#Run through the other rooms to see if they intersect with this one. If it intersects with any
		#other rooms, reject the room and break from the loop.
		failed = False
		for otherRoom in rooms:
			if newRoom.intersect(otherRoom):
				failed = True
				break
		
		if not failed:
			#This point in the loop means that there are no intersections, so this room is valid. We
			#now paint it to the map's tiles.
			carveRoom(newRoom)
			placeObjects(newRoom)
			
			#Gather center coordinates of new room.
			(newX, newY) = newRoom.center()
			
			#Optionally, print a "room number" glyph to see how the map drawing worked. We may have more
			#than ten rooms, so we will print A for the first room, B for the next, etc. If this exceeds
			#the given uppercase letters, it will begin labelling rooms with various symbols and then
			#lowercase letters. However, this will not explicitly fail unless we exceed sixty-two rooms.
			#roomNumber = Object(newX, newY, chr(65 + numberOfRooms), "Room Number", libtcod.white, False)
			#objects.insert(0, roomNumber)
			
			if numberOfRooms == 0:
				#This must be the first room, so the player will start here.
				player.x = newX
				player.y = newY
			else:
				#For all rooms after the first, we must connect it to the previous room using a tunnel.
				#Not every room can be connected using a strictly horizontal or vertical tunnel. For
				#example, if a room is in the top left, and the second room is in the bottom right, both
				#horizontal tunnel and a vertical tunnel will be needed. Either tunnel can be carved
				#first, so we will choose between these two possibilities randomly.
				
				#Gather center coordinates of previous room.
				(prevX, prevY) = rooms[numberOfRooms - 1].center()
				
				if libtcod.random_get_int(0, 0, 1) == 1:
					#First move horizontally, then vertically.
					carveHorizontalTunnel(prevX, newX, prevY)
					carveVerticalTunnel(prevY, newY, newX)
				else:
					#First move vertically, then horizontally.
					carveVerticalTunnel(prevY, newY, prevX)
					carveHorizontalTunnel(prevX, newX, newY)
			
			#Finally, append the new room to the list.
			rooms.append(newRoom)
			numberOfRooms += 1
		
	#Create stairs down at the center of the last room.
	stairsDown = Object(newX, newY, defs.gStairsDown, "Elevator Down", libtcod.white, desc = defs.DESC_ELEVATOR_DOWN, alwaysVisible = True)
	objects.append(stairsDown)
	stairsDown.sendToBack()

#This function places objects into a room.
def placeObjects(room):
	#Choose a random number of monsters below the maximum
	maxMonsters = fromLabLevel([[2,1], [3,4], [5,6]])
	monsterChances = {}
	monsterChances["tierZero"] = 80
	monsterChances["tierOne"] = fromLabLevel([[15,3], [30,5], [60,7]])
	
	numberOfMonsters = libtcod.random_get_int(0, 0, maxMonsters)
	
	for i in range(numberOfMonsters):
		#Choose a random spot for this monster. X and Y values are offset by one because the room's
		#rectangle includes its walls as well, and if it picks a wall tile, it will not get created
		#due to the tile being blocked.
		x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
		y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
		
		if not isBlocked(x,y):
			#Only place the object if the tile is not blocked.
			choice = chooseFromDict(monsterChances)
			if choice == "tierZero":
				monster = copy.deepcopy(script.selectFromList(tierZeroMonsters))
					
			elif choice == "tierOne":
				monster = copy.deepcopy(script.selectFromList(tierOneMonsters))
						
			monster.x = x
			monster.y = y
			objects.append(monster)
	
	maxItems = fromLabLevel([[1,1], [2,4]])
	#itemChances = {"heal": 70, "lightning": 10, "fireball": 10, "confuse": 10}
	#itemChances = {}
	#itemChances["food"] = 90
	#itemChances["potion"] = fromLabLevel([[10,1], [15,3]])
	#itemChances["armor"] = fromLabLevel([[5,1], [10,4]])
	
	numberOfItems = libtcod.random_get_int(0, 0, maxItems)
	
	for i in range(numberOfItems):
		#Choose a random spot for this item.
		x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
		y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

		if not isBlocked(x,y):
			itemToPlace = generateItem(x,y)
			objects.append(itemToPlace)
			itemToPlace.sendToBack()
			#Only place this item if the tile is not blocked.
			#choice = chooseFromDict(itemChances)
			#if choice == "potion":
			#	item = copy.deepcopy(script.selectFromList(potions))
			#	
			#elif choice == "food":
			#	item = copy.deepcopy(script.selectFromList(food))
			#	
			#elif choice == "armor":
			#	item = copy.deepcopy(script.selectFromList(armors))
			
			#item.alwaysVisible = True
			#item.x = x
			#item.y = y
			#objects.append(item)
			#item.sendToBack() #Items appear below other objects.
			
#This function advances to the next level in the dungeon.
def nextLevel():
	global dungeonLevel
	
	message("Zilla descends one floor deeper into the laboratory.", libtcod.cyan)
	dungeonLevel += 1
	makeMap()
	initializeFOV()
			
#########################################################################################################
# [TARGETING AND DISTANCE CALCULATION]                                                                  #
#########################################################################################################
	
#This function finds the closest monster within the given range and in the player's field of view.
def closestMonster(maxRange):
	closestEnemy = None
	closestDistance = maxRange + 1
	
	for object in objects:
		if object.fighter and not object == player and libtcod.map_is_in_fov(fovMap, object.x, object.y):
			distance = player.distanceTo(object)
			if distance < closestDistance:
				closestEnemy = object
				closestDistance = distance
	return closestEnemy
	
def targetTile(maxRange = None):
	global key, mouse
	while True:
		libtcod.console_flush()
		libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
		renderAll()
		
		(x, y) = (mouse.cx, mouse.cy)
		
		if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fovMap, x, y) 
			and (maxRange is None or player.distance(x,y) <= maxRange)):
			return (x, y)
		
		#Cancel the targeting if the user presses right mouse button or ESC.
		#This must return a tuple of Nones since two variables are needed.
		if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
			return (None, None)
	
#This function returns a clicked monster inside the player's field of view up to a range, or None if the
#player right-clicks.
def targetMonster(maxRange = None):
	while True:
		(x, y) = targetTile(maxRange)
		if x is None: #cancelled by player
			return None
		
		#Return the first-clicked monster, otherwise continue looping.
		for obj in objects:
			if obj.x == x and obj.y == y and obj.fighter and obj != player:
				return obj
	
#This function watches the player's experience points and controls level ups.
def checkLevelup():
	xpToAdvance = defs.ADVANCE_BASE + player.level * defs.ADVANCE_FACTOR
	if player.fighter.xp >= xpToAdvance:
		player.level += 1
		player.fighter.xp -= xpToAdvance
		
		player.fighter.baseHits += rnd(6,12)
		player.fighter.baseSppt += rnd(6,12)
		player.fighter.heal(player.fighter.hits)
		player.fighter.recover(player.fighter.sppt)
		
		mutationBonus = rnd()
		if mutationBonus == 0:
			#This mutation raises Zilla's attack
			message("I feel a mutation coming on! I'm a GIANTESS! Large and in charge!", defs.cZilla)
			player.fighter.baseAtk += 2
		elif mutationBonus == 1:
			#This mutation raises Zilla's defense
			message("I feel a mutation coming on! I'm so TOUGH! My belly's as strong as iron!", defs.cZilla)
			player.fighter.baseDfn += 2
				
#This function chooses one option from a list of chances, returning its index. The dice will land 
#on some number between one and the sum of the chances.
def randomChoiceIndex(chances):
	dice = libtcod.random_get_int(0, 1, sum(chances))
	
	#Go through all chances, keeping the sum so far.
	runningSum = 0
	choice = 0
	for w in chances:
		runningSum += w
		
		#See if the dice landed in the part that corresponds to this choice.
		if dice <= runningSum:
			return choice
		choice += 1

#This function chooses one option randomly from a dictionary of choices, returning its key.
def chooseFromDict(possibilityDictionary):
	chances = possibilityDictionary.values()
	possibilities = possibilityDictionary.keys()
	
	return possibilities[randomChoiceIndex(chances)]
	
#This function is used for displaying Zilla's health, which is measured in inches and must be
#converted to feet on the fly.
def convertHealthToSize(amount):
	return str(amount / 12) + "'" + str(amount % 12) + '"'
	
#This function is used for displaying Zilla's weight, which is measured in pounds.
def convertWeight(amount):
	convertedToTons = amount / 2000.0
	
	if amount < 2000:
		return str(amount) + " lbs"
	else:
		return str("%.2f" % round(convertedToTons, 2)) + " tons"
	
#########################################################################################################
# [RANDOM NUMBER GENERATION]                                                                            #
#########################################################################################################
	
#This function is a more concise way of invoking the libtcod random function, for shortening
#the function call. Calling the function without parameters flips a coin (returns either 0 or 1).
def rnd(min = 0, max = 1):
	return libtcod.random_get_int(0, min, max)
	
#This function returns a value that depends on laboratory level. The table specifies what value occurs after each level, default is zero.
def fromLabLevel(table):
	for (value, level) in reversed(table):
		if dungeonLevel >= level:
			return value
	return 0
	
def getEquippedInSlot(slot):
	for obj in inventory:
		if obj.equipment and obj.equipment.slot == slot and obj.equipment.isWorn:
			return obj.equipment
	return None

def getAllEquipped(obj):
	if obj == player:
		equippedList = []
		for item in inventory:
			if item.equipment and item.equipment.isWorn:
				equippedList.append(item.equipment)
		return equippedList
	else:
		return [] #Non-player objects do not have equipment.
	
#This function generates an item using the object data loaded through parsing. It takes the generation
#step by step, putting together components as necessary, and finally returns the entire new Object.	
def generateItem(x, y):
	itemChances = {"food": 50, "potion": 20, "suit": 15}
	typeChoice = chooseFromDict(itemChances)
	
	if typeChoice == "food":
		itemChoice = script.selectFromList(loader.itemsFood)
	if typeChoice == "potion":
		itemChoice = script.selectFromList(loader.itemsPotions)
	if typeChoice == "suit":
		itemChoice = script.selectFromList(loader.itemsSuits)
	
	chosenData = loader.rawItemData[itemChoice]
			
	#First, we need to read chosenData's kind and assign it the proper glyph.
	if chosenData["kind"] == "food":
		glyphValue = defs.gFood
	elif chosenData["kind"] == "potion":
		glyphValue = defs.gPotion
	elif chosenData["kind"] == "suit":
		glyphValue = defs.gArmor
	
	# If the BLOAT value exists in the chosen item's struct, then the item component will need that value
	# added in.
	if "bloat" in chosenData:
		bloatValue = chosenData["bloat"]
	else:
		bloatValue = 0
			
	# If the SLOT value exists in the chosen item's struct, then the item is an Equipment and will need
	# the appropriate type.
	if 'slot' in chosenData:
		equipComponent = Equipment(slot = chosenData['slot'])
	else:
		equipComponent = None
				
	# If the item has a use function, add that to the item's object.
	if 'useEffect' in chosenData:
		useEffect = chosenData['useEffect']
	else:
		useEffect = None
				
	itemComponent = Item(bloat = bloatValue, useEffect = useEffect)
	if equipComponent is not None:
		return Object(x, y, glyph = glyphValue, name = chosenData['name'], color = chosenData['col'], 
			desc = chosenData["dsc"], alwaysVisible = True, equipment = equipComponent)
	else:
		return Object(x, y, glyph = glyphValue, name = chosenData['name'], color = chosenData['col'], 
			desc = chosenData["dsc"], alwaysVisible = True, item = itemComponent)

#########################################################################################################
#Initialize the consoles, font style, and FPS limit.
libtcod.console_set_custom_font('terminal8x8_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(defs.SCREEN_WIDTH, defs.SCREEN_HEIGHT, "ZillaRL", False)
libtcod.sys_set_fps(defs.FPS_LIMIT)

con = libtcod.console_new(defs.MAP_WIDTH, defs.MAP_HEIGHT)
msgPanel = libtcod.console_new(defs.MESSAGE_PANEL_WIDTH, defs.MESSAGE_PANEL_HEIGHT)
sidebar = libtcod.console_new(defs.SIDEBAR_WIDTH, defs.SIDEBAR_HEIGHT)
infoPanel = libtcod.console_new(defs.MAP_WIDTH / 2, defs.MAP_HEIGHT)

loader.loadObjectData()
mainMenu()