########################################################################################################
# zillarl-data.py
#    by Bluey
# Definitions module for Bigger is Better (ZillaRL), containing integer values and script strings.
# http://www.forcastia.com | http://gaingirls.tumblr.com
#    Last updated on July 21, 2014
#    2014 Studio Draconis
########################################################################################################

import libtcodpy as libtcod

#Common Glyphs
#Zilla
gZilla = "Z"
gZillaClassic = "@"
gZillaShrunk = "."

#Terrain Tiles
gSpace = " "
gWall = "#"
gFloor = "."
gStairsDown = ">"

#Item Types
gFood = "%"
gSundry = ":"
gPotion = "?"
gScroll = "!"
gArmor = "]"
gBarrel = "0"
gRune = "&"

#Monster Types
gBellything = "b"	#Bellymage, Bellylord
gCharr = "c"		#Shadow Charr
gCrocodilian = "C"
gMarsupial = "k"
gLizard = "l"
gSnake = "s"		#Naga

#Size Constants
MESSAGE_PANEL_HEIGHT = 7
SIDEBAR_WIDTH = 20
MAP_WIDTH = 60
MAP_HEIGHT = 53

#Calculated Constants
SCREEN_WIDTH = MAP_WIDTH + SIDEBAR_WIDTH 			#Should be 80.
SCREEN_HEIGHT = MESSAGE_PANEL_HEIGHT + MAP_HEIGHT 	#Should be 60.
MESSAGE_PANEL_WIDTH = SCREEN_WIDTH - SIDEBAR_WIDTH
MESSAGE_WIDTH = MESSAGE_PANEL_WIDTH - 2
SIDEBAR_HEIGHT = SCREEN_HEIGHT
BAR_WIDTH = SIDEBAR_WIDTH - 4
MESSAGE_PANEL_Y = SCREEN_HEIGHT - MESSAGE_PANEL_HEIGHT
MESSAGE_HEIGHT = MESSAGE_PANEL_HEIGHT - 2

INFO_PANEL_WIDTH = MAP_WIDTH / 2

INVENTORY_LIMIT = 8

ITEM_WINDOW_WIDTH = 40
ITEM_WINDOW_HEIGHT = 10

INVENTORY_WIDTH = 50
ADVANCE_MENU_WIDTH = 40
MIRROR_SCREEN_WIDTH = 30

HEAL_AMOUNT = 36
LIGHTNING_DAMAGE = 20
LIGHTNING_RANGE = 5
CONFUSE_NUM_TURNS = 10
CONFUSE_RANGE = 8
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 12

SHRINK_CHANT_RADIUS = 3
SHRINK_CHANT_MIN_DAMAGE = 2
SHRINK_CHANT_MAX_DAMAGE = 8

#Experience and Leveling
#A player levels up upon attaining ADVANCE_BASE + (level * ADVANCE_FACTOR) experience
ADVANCE_BASE = 200
ADVANCE_FACTOR = 150

#Parameters for the Level Generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 32

#Field of View Constants
FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

#FPS Limit
FPS_LIMIT = 20

#Common Colors
cDarkWall = libtcod.darkest_blue
cDarkGround = libtcod.darker_blue
cLitWall = libtcod.sky
cLitGround = libtcod.light_grey
cZilla = libtcod.sepia

#Item Colors
cBikiniArmor = libtcod.pink
cBarrel = libtcod.darker_sepia

#Food Bloat Ratings
B_FRUIT = 1
B_BURGER = 3
B_BLOATBERRY = 6
B_GALLON = 8
B_KEG = B_GALLON * 15 		#15 gallons
B_BARREL = B_GALLON * 31 	#31 gallons
	
#Descriptions
DESC_DEFAULT = "This object has no description."
DESC_ZILLA = "One of our finest test subjects. She was granted extraordinary strength and shapeshifting abilities by our genetic experimentation."

#Features
DESC_ELEVATOR_DOWN = "This elevator will take the rider one floor downward in the laboratory."
DESC_COOKING_POT = "This pot can be used for cooking stews and soups."

#Monsters
DESC_NEWT = "A small aquatic amphibian lizard, prized by witches for polymorph practice."
DESC_GECKO = "A gecko."
DESC_LIZARD = "A lizard."
DESC_BELLYIMP = "This small, chubby demon wisps around on tiny wings, playing tricks and causing trouble. They are particularly fond of force-feeding defenseless creatures."
DESC_SNAKE = "A snake."

#Items - Food
DESC_BANANA = "A distinctively-shaped yellow fruit, typically harvested in large bunches."
DESC_APPLE = "A ripe, juicy, red fruit."
DESC_ORANGE = "A juicy orange fruit."
DESC_PEAR = "A ripe, juicy, green fruit."
DESC_MANGO = "A sweet, tropical fruit."
DESC_BLOATBERRY = "This small purple berry has extraordinary fattening properties and contains several thousand more calories than similar-sized fruits."
DESC_JUG_MILK = "A refrigerated container holding a gallon of fresh milk."
DESC_JUG_APPLEJUICE = "A refrigerated container holding a gallon of apple juice."
DESC_JUG_ORANGEJUICE = "A refrigerated container holding a gallon of orange juice."
DESC_KEG_COLA = "This large, silver keg contains fifteen gallons of cola. Drinking this will cause Zilla's belly to gurgle and rumble."
DESC_BARREL_COLA = "This heavy shipping barrel contains thirty-one gallons of cola. Drinking this will cause Zilla's belly to gurgle and rumble."

#Items - Consumables
DESC_POTION_MINORGROWTH = "This potion is made from growberry extract and healing herbs. It rejuvenates the body and reverses the effects of shrinking."
DESC_POTION_MAJORGROWTH = "This potion is made from growberry extract and potent herbs. It completely reverses the effects of shrinking and returns the user to full size."

#Items - Equipment
DESC_SHIFTER_SKIVVIES = "A matching purple set of bra and panties, stretched and strained from constant shapeshifting."
DESC_FLORAL_BIKINI = "This purple two-piece bikini has a flower-shaped design."
DESC_BRAWLER_BIKINI = "This red and white bikini resembles wrestler outfits and, using genetic triggers, imparts confidence and hand-to-hand combat knowledge."
DESC_EMBER_BIKINI = "A flame-colored bikini that is warm to the touch."
DESC_NANOWEAVE_BIKINI = "This black two-piece bikini has red trim and comes with matching wristbands. It is made of strong nanofibers that stretch and shrink with the wearer."
DESC_CHAINMAIL_BIKINI = "An armored bikini made of interweaving metal rings. It provides a surprising amount of protection to the wearer."
DESC_SILKSTEEL_BIKINI = "This green two-piece bikini is skin-tight and extraordinarily durable."
DESC_NEUTRONIUM_BIKINI = "This brown bikini is fabricated from the material within stellar bodies. It requires immense strength to lift, let alone wear."