from gridManipulation import *
from dataManipulation import *
import matplotlib.patches as patches
import csv
import os

curr_dir = os.path.dirname(__file__)

o_x = 5000
o_y = -10000
o = (o_x, o_y)

patch_width = 3750
patch_height = 3750
patch_size = (patch_width, patch_height)

x_patches = 18
y_patches = 4
total_patches = (x_patches, y_patches)
abs_total_patches = x_patches*y_patches

grid_angle = 0.9

day_selection = [20220209, 20220210, 20220208, 20220319, 20220318, 20220317, 20220316, 20220315, 20220314, 20220313, 20220312, 20220311, 20220310, 20220309]
station = 'ehv'

grid = create_grid(o, patch_size, total_patches, grid_angle)

for day in day_selection:
    data = getDay(day, station)
    data = data.drop(data[data.x_pos < o_x].index)
    data = data.drop(data[data.y_pos < o_y].index)
    data = data.drop(data[data.x_pos > (total_patches[0]-1)*patch_width].index)
    data = data.drop(data[data.y_pos > (total_patches[1]-1)*patch_height].index)

    #INITIALIZE MARKOV MATRIX TO APPROPIATE SIZE ALL 0s
    markov_matrix = []
    for i in range(abs_total_patches):
        markov_matrix.append([])
        for j in range(abs_total_patches):
            markov_matrix[i].append(0)

    #CREATE DICTIONARY THAT NAMES EACH ZONE WITH AN INDEX FOR MARKOV MATRIX
    markov_matrix_zone_reference = {}
    index = 0;
    for i,j in grid:
        markov_matrix_zone_reference[(i,j)] = index
        index = index + 1

    object_routes = {}
    for x in (data.tracked_object.unique()):
        object_routes[x] = []

    sample_period = 1

    for x in object_routes:
        object_data = data[data['tracked_object'] == x].reset_index().drop('index', axis=1)
        for y in range(0, len(object_data)-1, sample_period*10):
            curr_point = (object_data.x_pos[y],object_data.y_pos[y])
            curr_patch = point_patch(o,patch_size,curr_point)
            object_routes[x].append(curr_patch)
    all_users_route = []
    for user in object_routes:
        user_route = object_routes[user]
        for zone in range(len(user_route)):
            all_users_route.append(markov_matrix_zone_reference[user_route[zone]])
        all_users_route.append(-1)

    change_count = {}
    zone_appearance_count = {}
    for zone in range(len(all_users_route)):
        curr_zone = all_users_route[zone]
        if (zone+1 == len(all_users_route)):
            next_zone = -1
        else: next_zone = all_users_route[zone+1]
        if next_zone != -1 and curr_zone != -1:
            if ((curr_zone,next_zone) in change_count):
                change_count[(curr_zone,next_zone)] += 1
            else:
                change_count[(curr_zone,next_zone)] = 1
            if (curr_zone in zone_appearance_count):
                zone_appearance_count[(curr_zone)] += 1
            else:
                zone_appearance_count[(curr_zone)] = 1
       

    change_probabilities = {}
    for zone_1, zone_2 in change_count:
        change_probabilities[(zone_1,zone_2)] = change_count[(zone_1,zone_2)]/zone_appearance_count[zone_1]
        markov_matrix[zone_1][zone_2] = change_probabilities[(zone_1,zone_2)]

    with open(curr_dir + '/markov_matrices/' + str(day) + '.csv',"w+") as my_csv:
        csvWriter = csv.writer(my_csv,delimiter=',')
        csvWriter.writerows(markov_matrix)
