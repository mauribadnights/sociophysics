# SOCIOPHYSICS
This is the repo of Team 7: Pretty Pigeon for the course Sociophysics (3QEUS0)

## GRID MANIPULATION LIBRARY
The grid manipulation library provides with different functions to easily divide an area in zones (Matplotlib Patches) in a grid shapes.
This explains how to use the different functions.

### Create a grid
This function has the following shape:

create_grid (grid_origin, patch_size, total_patches, grid_angle)

The output is a dictionary with the shape {(i,j)=Rectangle.path.object...}

grid_origin is a tuple of 2 numbers

