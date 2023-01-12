print('Importing neccesary libraries...')
import sys
sys.path.append('../')
from libraries.dataManipulation import *
from libraries.gridManipulation import *
from data_preparator import *
import numpy as np
from collections import Counter
import time
import csv
start_time = time.time()
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
day_to_analyze = input('What day do you want to analyze?:')
data = getDay(day_to_analyze,'ehv')
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

print('Initializing markov matrix to appropiate size')
markov_matrix = []
for i in range(abs_total_patches+1):
    markov_matrix.append([])
    for j in range(abs_total_patches+1):
        markov_matrix[i].append(0)
print('Markov matrix initialized succesfully')

print('Initializing object routes dictionary')
object_routes = {}
for x in (data_off.tracked_object.unique()):
    object_routes[x] = []
print('Initialized succesfully')

print('Calculating pedestrian routes')
sample_period = 1
all_object_routes = []
for x in object_routes:
    object_data = data_off[data_off['tracked_object'] == x].reset_index().drop('index', axis=1)
    for y in range(0, len(object_data)-1, sample_period*10):
        curr_patch = zone(object_data.x_pos[y],object_data.y_pos[y])
        object_routes[x].append(curr_patch)
    object_routes[x].append(-1)
    all_object_routes.extend(object_routes[x])
print('Routes calculated')

print('Counting movements and transitions')
change_count = {}
zone_appearance_count = {}
for zone in range(len(all_object_routes)):
    curr_zone = all_object_routes[zone]
    
    if (zone+1 != len(all_object_routes)) and (curr_zone != -1):
        next_zone = all_object_routes[zone+1]
        
        if ((curr_zone,next_zone) in change_count):
            change_count[(curr_zone,next_zone)] += 1
        else:
            change_count[(curr_zone,next_zone)] = 1
        
        if (curr_zone in zone_appearance_count):
            zone_appearance_count[(curr_zone)] += 1
        else:
            zone_appearance_count[(curr_zone)] = 1
print('Counting finished succesfully')

print('Calculating frequencies')
change_probabilities = {}
for zone_1, zone_2 in change_count:
    change_probabilities[(zone_1,zone_2)] = change_count[(zone_1,zone_2)]/zone_appearance_count[zone_1]
    markov_matrix[zone_1][zone_2] = change_probabilities[(zone_1,zone_2)]
print('Frequencies succesfully calculated')

print('Exporting result to matrix')
result_name_and_path = 'results/offboarding/'+day_to_analyze+'.csv'
with open(result_name_and_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(markov_matrix)
f.close()










def zone(x_pos, y_pos):
    origin = o
    size = patch_size
    
    i = np.floor((x_pos-origin[0])/size[0])
    j = np.floor((y_pos-origin[1])/size[1])
    
    total_x_patches = total_patches[0]
    total_y_patches = total_patches[1]
    
    zone = (i*total_y_patches)+j
    return int(zone)

print('Initializing markov matrix to appropiate size')
markov_matrix_on_no = []
for i in range(abs_total_patches+1):
    markov_matrix_on_no.append([])
    for j in range(abs_total_patches+1):
        markov_matrix_on_no[i].append(0)
print('Markov matrix initialized succesfully')

print('Initializing object routes dictionary')
object_routes_on_no = {}
for x in (data_on_no_train.tracked_object.unique()):
    object_routes_on_no[x] = []
print('Initialized succesfully')

print('Calculating pedestrian routes')
all_object_routes_on_no = []
for x in object_routes_on_no:
    object_data = data_on_no_train[data_on_no_train['tracked_object'] == x].reset_index().drop('index', axis=1)
    for y in range(0, len(object_data)-1, sample_period*10):
        curr_patch = zone(object_data.x_pos[y],object_data.y_pos[y])
        object_routes_on_no[x].append(curr_patch)
    object_routes_on_no[x].append(-1)
    all_object_routes_on_no.extend(object_routes_on_no[x])
print('Routes calculated')

print('Counting movements and transitions')
change_count_on_no = {}
zone_appearance_count_on_no = {}
for zone in range(len(all_object_routes_on_no)):
    curr_zone = all_object_routes_on_no[zone]
    
    if (zone+1 != len(all_object_routes_on_no)) and (curr_zone != -1):
        next_zone = all_object_routes_on_no[zone+1]
        
        if ((curr_zone,next_zone) in change_count_on_no):
            change_count_on_no[(curr_zone,next_zone)] += 1
        else:
            change_count_on_no[(curr_zone,next_zone)] = 1
        
        if (curr_zone in zone_appearance_count_on_no):
            zone_appearance_count_on_no[(curr_zone)] += 1
        else:
            zone_appearance_count_on_no[(curr_zone)] = 1
print('Counting finished succesfully')

print('Calculating frequencies')
change_probabilities_on_no = {}
for zone_1, zone_2 in change_count_on_no:
    change_probabilities_on_no[(zone_1,zone_2)] = change_count_on_no[(zone_1,zone_2)]/zone_appearance_count_on_no[zone_1]
    markov_matrix_on_no[zone_1][zone_2] = change_probabilities_on_no[(zone_1,zone_2)]
print('Frequencies succesfully calculated')

print('Exporting result to matrix')
result_name_and_path_on_no = 'results/onboarding_no_train/'+str(day_to_analyze)+'.csv'
with open(result_name_and_path_on_no, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(markov_matrix_on_no)
f.close()






def zone(x_pos, y_pos):
    origin = o
    size = patch_size
    
    i = np.floor((x_pos-origin[0])/size[0])
    j = np.floor((y_pos-origin[1])/size[1])
    
    total_x_patches = total_patches[0]
    total_y_patches = total_patches[1]
    
    zone = (i*total_y_patches)+j
    return int(zone)

print('Initializing markov matrix to appropiate size')
markov_matrix_on_top = []
for i in range(abs_total_patches+1):
    markov_matrix_on_top.append([])
    for j in range(abs_total_patches+1):
        markov_matrix_on_top[i].append(0)
print('Markov matrix initialized succesfully')

print('Initializing object routes dictionary')
object_routes_on_top = {}
for x in (data_on_train_top.tracked_object.unique()):
    object_routes_on_top[x] = []
print('Initialized succesfully')

print('Calculating pedestrian routes')
all_object_routes_on_top = []
for x in object_routes_on_top:
    object_data = data_on_train_top[data_on_train_top['tracked_object'] == x].reset_index().drop('index', axis=1)
    for y in range(0, len(object_data)-1, sample_period*10):
        curr_patch = zone(object_data.x_pos[y],object_data.y_pos[y])
        object_routes_on_top[x].append(curr_patch)
    object_routes_on_top[x].append(-1)
    all_object_routes_on_top.extend(object_routes_on_top[x])
print('Routes calculated')

print('Counting movements and transitions')
change_count_on_top = {}
zone_appearance_count_on_top = {}
for zone in range(len(all_object_routes_on_top)):
    curr_zone = all_object_routes_on_top[zone]
    
    if (zone+1 != len(all_object_routes_on_top)) and (curr_zone != -1):
        next_zone = all_object_routes_on_top[zone+1]
        
        if ((curr_zone,next_zone) in change_count_on_top):
            change_count_on_top[(curr_zone,next_zone)] += 1
        else:
            change_count_on_top[(curr_zone,next_zone)] = 1
        
        if (curr_zone in zone_appearance_count_on_top):
            zone_appearance_count_on_top[(curr_zone)] += 1
        else:
            zone_appearance_count_on_top[(curr_zone)] = 1
print('Counting finished succesfully')

print('Calculating frequencies')
change_probabilities_on_top = {}
for zone_1, zone_2 in change_count_on_top:
    change_probabilities_on_top[(zone_1,zone_2)] = change_count_on_top[(zone_1,zone_2)]/zone_appearance_count_on_top[zone_1]
    markov_matrix_on_top[zone_1][zone_2] = change_probabilities_on_top[(zone_1,zone_2)]
print('Frequencies succesfully calculated')

print('Exporting result to matrix')
result_name_and_path_on_top = 'results/onboarding_top/'+str(day_to_analyze)+'.csv'
with open(result_name_and_path_on_top, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(markov_matrix_on_top)
f.close()





def zone(x_pos, y_pos):
    origin = o
    size = patch_size
    
    i = np.floor((x_pos-origin[0])/size[0])
    j = np.floor((y_pos-origin[1])/size[1])
    
    total_x_patches = total_patches[0]
    total_y_patches = total_patches[1]
    
    zone = (i*total_y_patches)+j
    return int(zone)

print('Initializing markov matrix to appropiate size')
markov_matrix_on_bottom = []
for i in range(abs_total_patches+1):
    markov_matrix_on_bottom.append([])
    for j in range(abs_total_patches+1):
        markov_matrix_on_bottom[i].append(0)
print('Markov matrix initialized succesfully')

print('Initializing object routes dictionary')
object_routes_on_bottom = {}
for x in (data_on_train_bottom.tracked_object.unique()):
    object_routes_on_bottom[x] = []
print('Initialized succesfully')

print('Calculating pedestrian routes')
all_object_routes_on_bottom = []
for x in object_routes_on_bottom:
    object_data = data_on_train_bottom[data_on_train_bottom['tracked_object'] == x].reset_index().drop('index', axis=1)
    for y in range(0, len(object_data)-1, sample_period*10):
        curr_patch = zone(object_data.x_pos[y],object_data.y_pos[y])
        object_routes_on_bottom[x].append(curr_patch)
    object_routes_on_bottom[x].append(-1)
    all_object_routes_on_bottom.extend(object_routes_on_bottom[x])
print('Routes calculated')

print('Counting movements and transitions')
change_count_on_bottom = {}
zone_appearance_count_on_bottom = {}
for zone in range(len(all_object_routes_on_bottom)):
    curr_zone = all_object_routes_on_bottom[zone]
    
    if (zone+1 != len(all_object_routes_on_bottom)) and (curr_zone != -1):
        next_zone = all_object_routes_on_bottom[zone+1]
        
        if ((curr_zone,next_zone) in change_count_on_bottom):
            change_count_on_bottom[(curr_zone,next_zone)] += 1
        else:
            change_count_on_bottom[(curr_zone,next_zone)] = 1
        
        if (curr_zone in zone_appearance_count_on_bottom):
            zone_appearance_count_on_bottom[(curr_zone)] += 1
        else:
            zone_appearance_count_on_bottom[(curr_zone)] = 1
print('Counting finished succesfully')

print('Calculating frequencies')
change_probabilities_on_bottom = {}
for zone_1, zone_2 in change_count_on_bottom:
    change_probabilities_on_bottom[(zone_1,zone_2)] = change_count_on_bottom[(zone_1,zone_2)]/zone_appearance_count_on_bottom[zone_1]
    markov_matrix_on_bottom[zone_1][zone_2] = change_probabilities_on_bottom[(zone_1,zone_2)]
print('Frequencies succesfully calculated')

print('Exporting result to matrix')
result_name_and_path_on_bottom = 'results/onboarding_bottom/'+str(day_to_analyze)+'.csv'
with open(result_name_and_path_on_bottom, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(markov_matrix_on_bottom)
f.close()






def zone(x_pos, y_pos):
    origin = o
    size = patch_size
    
    i = np.floor((x_pos-origin[0])/size[0])
    j = np.floor((y_pos-origin[1])/size[1])
    
    total_x_patches = total_patches[0]
    total_y_patches = total_patches[1]
    
    zone = (i*total_y_patches)+j
    return int(zone)

print('Initializing markov matrix to appropiate size')
markov_matrix_on_both = []
for i in range(abs_total_patches+1):
    markov_matrix_on_both.append([])
    for j in range(abs_total_patches+1):
        markov_matrix_on_both[i].append(0)
print('Markov matrix initialized succesfully')

print('Initializing object routes dictionary')
object_routes_on_both = {}
for x in (data_on_train_both.tracked_object.unique()):
    object_routes_on_both[x] = []
print('Initialized succesfully')

print('Calculating pedestrian routes')
all_object_routes_on_both = []
for x in object_routes_on_both:
    object_data = data_on_train_both[data_on_train_both['tracked_object'] == x].reset_index().drop('index', axis=1)
    for y in range(0, len(object_data)-1, sample_period*10):
        curr_patch = zone(object_data.x_pos[y],object_data.y_pos[y])
        object_routes_on_both[x].append(curr_patch)
    object_routes_on_both[x].append(-1)
    all_object_routes_on_both.extend(object_routes_on_both[x])
print('Routes calculated')

print('Counting movements and transitions')
change_count_on_both = {}
zone_appearance_count_on_both = {}
for zone in range(len(all_object_routes_on_both)):
    curr_zone = all_object_routes_on_both[zone]
    
    if (zone+1 != len(all_object_routes_on_both)) and (curr_zone != -1):
        next_zone = all_object_routes_on_both[zone+1]
        
        if ((curr_zone,next_zone) in change_count_on_both):
            change_count_on_both[(curr_zone,next_zone)] += 1
        else:
            change_count_on_both[(curr_zone,next_zone)] = 1
        
        if (curr_zone in zone_appearance_count_on_both):
            zone_appearance_count_on_both[(curr_zone)] += 1
        else:
            zone_appearance_count_on_both[(curr_zone)] = 1
print('Counting finished succesfully')

print('Calculating frequencies')
change_probabilities_on_both = {}
for zone_1, zone_2 in change_count_on_both:
    change_probabilities_on_both[(zone_1,zone_2)] = change_count_on_both[(zone_1,zone_2)]/zone_appearance_count_on_both[zone_1]
    markov_matrix_on_both[zone_1][zone_2] = change_probabilities_on_both[(zone_1,zone_2)]
print('Frequencies succesfully calculated')

print('Exporting result to matrix')
result_name_and_path_on_both = 'results/onboarding_both/'+str(day_to_analyze)+'.csv'
with open(result_name_and_path_on_both, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(markov_matrix_on_both)
f.close()


end_time = time.time()

print(end_time-start_time)