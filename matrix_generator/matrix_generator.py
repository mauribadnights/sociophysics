print('Installing libraries')
libraries_required = ['sys', 'numpy', 'time', 'csv', 'os', 'shutil', 'pyfiglet']

print('Importing neccesary libraries...')
import sys
sys.path.append('../')
from libraries.dataManipulation import *
from libraries.gridManipulation import *
from data_preparator import *
import numpy as np
import time
import csv
import os
import shutil
import pyfiglet
print('Libraries have been properly imported.')


days_to_analyze = [20220314, 20220315, 20220316, 20220317, 20220318,
                   20220321, 20220322, 20220323, 20220324, 20220325,
                   20220328, 20220329, 20220330, 20220331, 20220401,
                   20220404, 20220405, 20220406, 20220407, 20220408]

result_relative_paths = ['results/onboarding_no_train/', 'results/onboarding_top/', 'results/onboarding_bottom/', 'results/onboarding_both/', 'results/offboarding/']

start_title = pyfiglet.figlet_format("TRANSITION MATRIX GENERATOR")
finish_message = pyfiglet.figlet_format("DONE!")
print(start_title)

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

def make_matrix(data, path):
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
    markov_matrix = []
    for i in range(abs_total_patches+1):
        markov_matrix.append([])
        for j in range(abs_total_patches+1):
            markov_matrix[i].append(0)
    print('Markov matrix initialized succesfully')

    print('Initializing object routes dictionary')
    object_routes = {}
    for x in (data.tracked_object.unique()):
        object_routes[x] = []
    print('Initialized succesfully')

    print('Calculating pedestrian routes')
    sample_period = 1
    all_object_routes = []
    for x in object_routes:
        object_data = data[data['tracked_object'] == x].reset_index().drop('index', axis=1)
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
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(markov_matrix)
    f.close()


def analize_day(day_to_analyze):
    day_analysis_start = time.time()
    print('Analyzing day ' + str(day_to_analyze) + '...')
    print('Downloading day data...')
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

    make_matrix(data_on_no_train, result_relative_paths[0]+str(day_to_analyze)+'.csv')
    make_matrix(data_on_train_top, result_relative_paths[1]+str(day_to_analyze)+'.csv')
    make_matrix(data_on_train_bottom, result_relative_paths[2]+str(day_to_analyze)+'.csv')
    make_matrix(data_on_train_both, result_relative_paths[3]+str(day_to_analyze)+'.csv')
    make_matrix(data_off, result_relative_paths[4]+str(day_to_analyze)+'.csv')
    day_analysis_end = time.time()
    print('DAY TOOK ' + str(day_analysis_end-day_analysis_start) + 's TO ANALYZE')

def average_matrix(path):
    print(path)
    curr_dir = os.path.dirname(__file__)
    if path == 0:
        relative_path = input("Enter relative path between slashes: ")
    else:
        relative_path = path
    matrices_dir = curr_dir + relative_path

    shutil.rmtree(matrices_dir+'/.ipynb_checkpoints', ignore_errors=True)

    average_matrix = [[-1]]

    for fileName in os.listdir(matrices_dir):
        markov_matrix_file = open(matrices_dir + fileName)
        markov_matrix = np.loadtxt(markov_matrix_file, delimiter=",")
        if average_matrix[0][0] == -1:
            average_matrix = markov_matrix
        else:
            if len(average_matrix) == len(markov_matrix):
                for i in range(len(markov_matrix)):
                    for j in range(len(markov_matrix[i])):
                        average_matrix[i][j] = (average_matrix[i][j]+markov_matrix[i][j])/2

    with open(matrices_dir+"/average.csv", "w+") as my_csv:
        csvWriter = csv.writer(my_csv, delimiter=',')
        csvWriter.writerows(average_matrix)

print('Welcome to the transition matrix generator. Enter a command to start an analysis (use command h for help on commands).')
exit = 0
while exit==0:
    command = input('> ')
    match command:
        case 'q':
            exit = 1
        case 'list':
            for day in days_to_analyze:
                analize_day(day)
            print(finish_message)
        case 'day':
            day = input('What day would you like to analyze? (Input must have shape yyyymmdd): ')
            analize_day(day)
            print(finish_message)
        case 'avg':
            average_matrix(0)
            print(finish_message)
        case 'avgcomplete':
            for path in result_relative_paths:
                average_matrix(path)
            print(finish_message)
        case 'range':
            init_date = input('What date do you want the analysis to start at? (Value must have shape yyyymmdd): ')
            end_date = input('What date do you want the analysis to start at? (Value must have shape yyyymmdd and be in the same month that the start date): ')
            day_range = range(int(init_date),int(end_date)+1)
            for day in day_range:
                analize_day(day)
            print(finish_message)
        case 'rangecomplete':
            init_date = input('What date do you want the analysis to start at? (Value must have shape yyyymmdd): ')
            end_date = input('What date do you want the analysis to start at? (Value must have shape yyyymmdd and be in the same month that the start date): ')
            day_range = range(int(init_date),int(end_date)+1)
            for day in day_range:
                analize_day(day)
            for path in result_relative_paths:
                average_matrix(path)
            print(finish_message)
        case 'complete':
            for day in days_to_analyze:
                analize_day(day)
            for path in result_relative_paths:
                average_matrix(path)
            print(finish_message)
        case 'h':
            print('List of commands:')
            print('    - "q": quit program')
            print('    - "list": analyze all days in list "days_to_analyze" (declared on line 14 of this program). Edit the code to modify days to analyze.')
            print('    - "day": analyze a single day')
            print('    - "avg": compute average of several transition matrices in a specified path (matrices must be in a .csv file)')
            print('    - "complete": analyze days in list and perform average for all matrices obtained (results in 5 average matrices')
            print('    - "avgcomplete": compute average for all transition matrices in all result paths (results in 5 average matrices')
            print('    - "range": analyze all days within 2 specified dates (both included). Both dates must be in the same month.')
            print('    - "rangecomplete": analyze all days within 2 specified dates (both included) and compute average for all results. Both dates must be in the same month. This will result in 5 average transition matrices')
            print('Please note that this analysis can only be done for data in 2022, data from 2021 will result in wrong matrices.')
            print('For more information please check out the README file in GitHub. Enjoy the analysis!')
        case _:
            print('Command not recognized. Use command "h" to see the different available commands.')
