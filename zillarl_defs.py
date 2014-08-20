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

#Zilla Base Stats
ZILLA_HITS = 64
ZILLA_SPPT = 24
ZILLA_ATK = 2
ZILLA_DEF = 2
ZILLA_MIN = 2
ZILLA_MAX = 3

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
cLitGround = libtcod.grey
cLitGroundAlternate = libtcod.light_grey
cZilla = libtcod.sepia

#Item Colors
cBikiniArmor = libtcod.pink
cBarrel = libtcod.darker_sepia

#Features
DESC_ELEVATOR_DOWN = "This elevator will take the rider one floor downward in the laboratory."
DESC_COOKING_POT = "This pot can be used for cooking stews and soups."