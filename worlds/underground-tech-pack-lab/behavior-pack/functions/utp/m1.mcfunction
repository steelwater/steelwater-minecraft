# DEVELOPMENT ONLY. Run only in a new dedicated test world.
# Replaces x=40..75, y=79..88, z=0..32. Never run in an existing build.
fill 40 79 0 75 88 32 air
fill 40 79 0 75 79 32 stone
# 5x5 repetition sample: navy_metal
fill 42 80 2 46 84 2 steelwater_utp:navy_metal
# 5x5 repetition sample: smooth_navy_metal
fill 50 80 2 54 84 2 steelwater_utp:smooth_navy_metal
# 5x5 repetition sample: reinforced_panel
fill 58 80 2 62 84 2 steelwater_utp:reinforced_panel
# 5x5 repetition sample: grated_floor
fill 66 80 2 70 84 2 steelwater_utp:grated_floor
# 5x5 repetition sample: ceiling_panel
fill 42 80 10 46 84 10 steelwater_utp:ceiling_panel
# 5x5 repetition sample: metal_trim
fill 50 80 10 54 84 10 steelwater_utp:metal_trim
# 5x5 repetition sample: vent_panel
fill 58 80 10 62 84 10 steelwater_utp:vent_panel
# 5x5 repetition sample: hazard_panel
fill 66 80 10 70 84 10 steelwater_utp:hazard_panel
# Compact room: dim; all eight pieces.
fill 42 79 20 52 85 30 steelwater_utp:smooth_navy_metal hollow
fill 43 79 21 51 79 29 steelwater_utp:grated_floor
fill 43 85 21 51 85 29 steelwater_utp:ceiling_panel
fill 43 80 30 51 83 30 steelwater_utp:navy_metal
fill 43 84 30 51 84 30 steelwater_utp:metal_trim
fill 42 80 23 42 83 27 steelwater_utp:reinforced_panel
fill 52 81 24 52 82 26 steelwater_utp:vent_panel
fill 46 80 20 47 81 20 air
setblock 45 80 20 steelwater_utp:hazard_panel
# Compact room: lit; all eight pieces.
fill 59 79 20 69 85 30 steelwater_utp:smooth_navy_metal hollow
fill 60 79 21 68 79 29 steelwater_utp:grated_floor
fill 60 85 21 68 85 29 steelwater_utp:ceiling_panel
fill 60 80 30 68 83 30 steelwater_utp:navy_metal
fill 60 84 30 68 84 30 steelwater_utp:metal_trim
fill 59 80 23 59 83 27 steelwater_utp:reinforced_panel
fill 69 81 24 69 82 26 steelwater_utp:vent_panel
fill 63 80 20 64 81 20 air
setblock 62 80 20 steelwater_utp:hazard_panel
setblock 64 84 25 sea_lantern
give @s steelwater_utp:navy_metal 64
give @s steelwater_utp:smooth_navy_metal 64
give @s steelwater_utp:reinforced_panel 64
give @s steelwater_utp:grated_floor 64
give @s steelwater_utp:ceiling_panel 64
give @s steelwater_utp:metal_trim 64
give @s steelwater_utp:vent_panel 64
give @s steelwater_utp:hazard_panel 64
tp @s 56 80 17
tellraw @s {"rawtext":[{"text":"M1 lab: north = eight 5x5 samples; south = dim and lit rooms. Add a temporary light to inspect the dim room. Test placement and save/reopen manually."}]}
