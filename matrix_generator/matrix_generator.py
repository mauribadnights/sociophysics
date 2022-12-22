print('Importing neccesary libraries...')
import sys
sys.path.append('../')
from libraries.dataManipulation import *
from libraries.gridManipulation import *
from data_preparator import *
import numpy as np
from collections import Counter
print('Libraries have been properly imported.')

print('Declaring grid configuration:')
#GRID CONFIGURATION IS DECLARED
o_x = 5000
o_y = -10000
o = (o_x,o_y)

#TOTAL GRID SHOULD BE SIZE 67000x13000
patch_width = 1000
patch_height = 1000
patch_size = (patch_width, patch_height)

total_patches = (67,14)
abs_total_patches = total_patches[0]*total_patches[1]

grid_angle = 0
print('Grid will have ' + 
      str(total_patches[0]) + 
      ' zones along the x axis and ' + 
      str(total_patches[1]) +
      ' zones along the y axis, making a total of ' +
      str(abs_total_patches) +
      ' patches.'
      )

print('Each patch will have the following dimensions: ' + 
      str(patch_width) + 
      'x' +
      str(patch_height)
      )

print('The angle of the grid is ' + str(grid_angle) + ' degrees.')

print('Grid starts in coordinates: ' + 
      str(o_x) + 'x' + str(o_y))

#GRID IS CREATED USING CONFIG
print('Creating grid...')
grid = create_grid(o, patch_size, total_patches, grid_angle)
print('grid succesfully created')

print('Downloading day data...')
data = getDay(20220314,'ehv')
print('day data succesfully downloaded.')
print('Removing data from outside bounds...')
data = data.drop(data[data.x_pos < o_x].index)
data = data.drop(data[data.y_pos < o_y].index)
data = data.drop(data[data.x_pos > (total_patches[0]-1)*patch_width].index)
data = data.drop(data[data.y_pos > (total_patches[1]-1)*patch_height].index)
print('data succesfully removed.')

print('Dividing data by train presence and location...')
(data_on_array ,data_off) = data_division(data)

data_on_no_train = data_on_array[0]
data_on_train_top = data_on_array[1]
data_on_train_bottom = data_on_array[2]
data_on_train_both = data_on_array[3]
print('data succesfully divided')

print('Preparing zone indentifier...')
def zone(x_pos, y_pos):
    origin = o
    size = patch_size
    
    i = np.floor((x_pos-origin[0])/size[0])
    j = np.floor((y_pos-origin[1])/size[1])
    
    total_x_patches = total_patches[0]
    total_y_patches = total_patches[1]
    
    zone = (i*total_y_patches)+j
    return int(zone)
print('zone indentifier ready.')

print('Processing data_off...')
data_off['zone'] = np.vectorize(zone)(data_off['x_pos'], data_off['y_pos'])
print('...data_off processed.')

print('Processing data_on_no_train...')
data_on_no_train['zone'] = np.vectorize(zone)(data_on_no_train['x_pos'], data_on_no_train['y_pos'])
print('...data_on_no_train processed.')

print('Processing data_on_train_top...')
data_on_train_top['zone'] = np.vectorize(zone)(data_on_train_top['x_pos'], data_on_train_top['y_pos'])
print('...data_on_train_top processed.')

print('Processing data_on_train_bottom...')
data_on_train_bottom['zone'] = np.vectorize(zone)(data_on_train_bottom['x_pos'], data_on_train_bottom['y_pos'])
print('...data_on_train_bottom processed.')

print('Starting transition and zone count, this will take around 6 hours per day...')
