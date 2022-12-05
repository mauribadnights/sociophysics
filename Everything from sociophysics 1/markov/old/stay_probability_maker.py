import numpy as np
import os
import csv

curr_dir = os.path.dirname(__file__)
print("Enter relative path between slashes: ")
relative_path = input()
matrices_dir = curr_dir + relative_path
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

platform_stay = [[],[],[],[]]
for row in range(4):
    for column in range(3-row, 72-row, 4):
        platform_stay[row].append(markov_matrix[column][column])

with open(curr_dir + "/platform_stay.csv", "w+") as my_csv:
    csvWriter = csv.writer(my_csv, delimiter=',')
    csvWriter.writerows(platform_stay)
