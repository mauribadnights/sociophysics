import matplotlib.pyplot as plt
import datetime
import matplotlib.patches as patches
import math
from sociophysicsDataHandler import SociophysicsDataHandler

dh = SociophysicsDataHandler()
def getPic(station):
    if (str(station) == 'ehv'):
        dh.fetch_background_image_from_path('ehv/background_images/EHV.Perron2.1_multisensor.png')
        return dh.bg
    else:
        print(str(station)+' is not a valid station.')
        return 0

#Function to calculate lower left corner of square in grid given grid angle
def initial_positions (patch_width, patch_height, patch_angle, o_x, o_y, i, j):
    patch_angle_rad = patch_angle*math.pi/180
    cos = math.cos(patch_angle_rad)
    sin = math.sin(patch_angle_rad)
    
    new_i = i*patch_width
    new_j = j*patch_height
    
    initial_x = int(((new_i*cos)+(new_j*sin))+o_x)
    initial_y = int(((new_j*cos)-(new_i*sin))+o_y)
    
    return((initial_x, initial_y))

def create_grid (grid_origin, patch_size, total_patches, grid_angle):
    grid = {}

    for i in range(total_patches[0]):
        for j in range(total_patches[1]):
            patch_origin = initial_positions(patch_size[0], patch_size[1], grid_angle, grid_origin[0], grid_origin[1],i,j)
            grid[(i,j)] = patches.Rectangle(patch_origin,patch_size[0],patch_size[1],angle=-grid_angle,linewidth=1, edgecolor='r', facecolor='none')
    return grid


def plot_grid (grid, station):
    fig = plt.figure(figsize=(20,8))
    ax = fig.add_subplot(111)
    xmin = -5134
    ymin = -17731
    xmax =  75135
    ymax =  11645

    pic_object = getPic(station)
    if (pic_object == 0):
        return 0
    else:
        ax.imshow(pic_object, cmap = 'gray', extent=[xmin, xmax, ymin, ymax])
        for i, j in grid:
            ax.add_patch(grid[i,j])

def patch_borders(grid):
    borders = {}
    for i, j in grid:
        width = grid[i,j].get_width()
        height = grid[i,j].get_height()
        origin = grid[i,j].get_xy()
        upperright = (origin[0]+width, origin[1]+height)
        borders[(i,j)] = (origin[0],upperright[0], origin[1], upperright[1])
    return borders


def point_in_patch(point, patch):
    down_limit = patch.get_y()
    left_limit = patch.get_x()
    up_limit = down_limit+patch.get_height()
    right_limit = left_limit+patch.get_width()
    
    point_x = point[0]
    point_y = point[1]

    if (point_x>left_limit and point_x<right_limit and point_y>down_limit and point_y<up_limit):
        return True
    else:
        return False

def point_patch(origin, size, point):
    o_x = origin[0]
    o_y = origin[1]
    width = size[0]
    height = size[1]
    point_x = point[0]
    point_y = point[1]

    i = math.floor((point_x-o_x)/width)
    j = math.floor((point_y-o_y)/height)

    return(i,j)
