# Prototype only. Run in a new dedicated test world.
# Replaces x=80..96, y=79..86, z=0..14.
fill 80 79 0 96 86 14 air
fill 80 79 0 96 79 14 steelwater_utp:grated_floor
fill 84 80 10 92 85 10 steelwater_utp:navy_metal
fill 84 85 5 92 85 9 steelwater_utp:ceiling_panel
# Straight samples along Z, X and Y.
setblock 82 81 2 steelwater_utp:straight_pipe ["minecraft:block_face"="north"]
setblock 84 81 2 steelwater_utp:straight_pipe ["minecraft:block_face"="east"]
setblock 86 81 2 steelwater_utp:straight_pipe ["minecraft:block_face"="up"]
setblock 88 81 2 steelwater_utp:elbow_pipe ["minecraft:cardinal_direction"="north","minecraft:block_face"="north"]
# Horizontal elbow joins an east-west run to a north-south run.
fill 88 82 9 91 82 9 steelwater_utp:straight_pipe ["minecraft:block_face"="east"]
setblock 87 82 9 steelwater_utp:elbow_pipe ["minecraft:cardinal_direction"="north","minecraft:block_face"="north"]
fill 87 82 6 87 82 8 steelwater_utp:straight_pipe ["minecraft:block_face"="north"]
# Vertical elbow beside the wall.
setblock 87 81 9 steelwater_utp:elbow_pipe ["minecraft:cardinal_direction"="north","minecraft:block_face"="up"]
fill 88 81 9 91 81 9 steelwater_utp:straight_pipe ["minecraft:block_face"="east"]
setblock 87 80 9 steelwater_utp:straight_pipe ["minecraft:block_face"="up"]
give @s steelwater_utp:straight_pipe 64
give @s steelwater_utp:elbow_pipe 64
tp @s 91 80 4
