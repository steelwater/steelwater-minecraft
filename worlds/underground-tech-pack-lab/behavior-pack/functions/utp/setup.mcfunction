# DEVELOPMENT ONLY. Run once in an empty dedicated test world.
# Replaces x=0..31, y=79..87, z=0..23. Never run in an existing build.
fill 0 79 0 31 87 23 air
fill 0 79 0 31 79 23 stone
# Daylight repetition wall and floor strip.
fill 2 80 2 9 83 2 steelwater_utp:navy_metal
fill 2 80 5 9 80 8 steelwater_utp:navy_metal
# Isolated cube, jump step, and two-block collision wall.
setblock 12 80 2 steelwater_utp:navy_metal
fill 12 80 5 12 81 8 steelwater_utp:navy_metal
setblock 14 80 5 steelwater_utp:navy_metal
# Vanilla scale/material controls and reserved comparison lane.
setblock 17 80 2 iron_block
setblock 19 80 2 stone
setblock 21 80 2 steelwater_utp:navy_metal
# Enclosed light-check room. West-facing entrance with short baffle.
fill 2 80 13 12 85 22 stone hollow
fill 2 80 15 2 81 16 air
fill 4 80 14 4 82 17 stone
fill 7 80 21 11 83 21 steelwater_utp:navy_metal
setblock 9 80 18 steelwater_utp:navy_metal
# Lit comparison alcove at right.
fill 17 80 13 27 85 22 stone hollow
fill 17 80 15 17 81 16 air
fill 22 80 21 26 83 21 steelwater_utp:navy_metal
setblock 24 84 18 sea_lantern
gamerule doDaylightCycle false
gamerule doWeatherCycle false
gamerule doMobSpawning false
gamerule keepInventory true
time set noon
weather clear
give @s steelwater_utp:navy_metal 64
tp @s 15 80 10
tellraw @s {"rawtext":[{"text":"UTP lab built. North: daylight/scale. South-west: dark room. South-east: lit room. Save, close and reopen after testing."}]}
