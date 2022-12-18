from wsgiref.handlers import format_date_time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib.patches as patches
import math
from sociophysicsDataHandler import SociophysicsDataHandler

dh = SociophysicsDataHandler()

#Currently only supports ehv
def getDay(day, station):
    if (station == 'ehv'):
        file_path = 'ehv/platform2.1/' + str(day)
        fLst = dh.list_files(file_path)
        daydf = pd.DataFrame
        dh.fetch_prorail_data_from_path(file_path + "/" + fLst.name[0])
        dh.df['date_time_utc'] = pd.to_datetime(dh.df['date_time_utc'], unit = 'ms')
        daydf = dh.df
        for hour in fLst.index:
            dh.fetch_prorail_data_from_path(file_path + "/" + fLst.name[hour])
            dh.df['date_time_utc'] = pd.to_datetime(dh.df['date_time_utc'], unit = 'ms')
            daydf = pd.concat([daydf, dh.df], ignore_index=True)
        daydf.rename(columns = {'x_pos':'y_pos', 'y_pos':'x_pos'}, inplace = True)
        return daydf
    else:
        print(str(station)+" is not a valid station.")
        return 0 

def getHours(from_index, to_index, day, station):
    file_path = 'ehv/platform2.1/' + str(day)
    fLst = dh.list_files(file_path)
    hoursdf = pd.DataFrame
    dh.fetch_prorail_data_from_path(file_path + "/" + fLst.name[from_index])
    dh.df['date_time_utc'] = pd.to_datetime(dh.df['date_time_utc'], unit = 'ms')
    hoursdf = dh.df
    if (from_index == to_index):
        hoursdf.rename(columns = {'x_pos':'y_pos', 'y_pos':'x_pos'}, inplace = True)
        return hoursdf
    else:
        for hour in range(from_index+1, to_index):
            dh.fetch_prorail_data_from_path(file_path + "/" + fLst.name[hour])
            dh.df['date_time_utc'] = pd.to_datetime(dh.df['date_time_utc'], unit = 'ms')
            hoursdf = pd.concat([hoursdf, dh.df], ignore_index=True)
    hoursdf.rename(columns = {'x_pos':'y_pos', 'y_pos':'x_pos'}, inplace = True)
    return hoursdf

def getTime(from_datetime, to_datetime, station):
    #From the date time, get the date to use in the getHours function
    year = str(from_datetime.year)
    month = str(from_datetime.month)
    day = str(from_datetime.day)
    #Check if the month and day are displayed in two digits
    if (len(month) < 2):
        month = "0" + month
    if (len(day) < 2):
        day = "0"+ day
    date = year + month + day
    #Get the hours in which the times are specified
    timedf = getHours(from_datetime.hour+1, to_datetime.hour+2, date, station)
    #Crop the selected hours to the specified times
    timedf = timedf[timedf['date_time_utc'] >= from_datetime]
    timedf = timedf[timedf['date_time_utc'] <= to_datetime]
    return timedf


def direction_label(data):
    def compute_direction(group):
        first_appearance_index = group.index[0]
        last_appearance_index = group.index[-1]
        start_coordinate = group.loc[first_appearance_index]['x_pos']
        end_coordinate = group.loc[last_appearance_index]['x_pos']
        x_displacement = end_coordinate - start_coordinate
        if x_displacement > 0:
            return 'onboarding'
        elif x_displacement < 0:
            return 'offboarding'
        else:
            return 'undefined'
    result_series = data.groupby('tracked_object').apply(compute_direction)
    result_df = result_series.to_frame()
    result_df.columns = ['direction']
    result_df = result_df.reset_index()
    return result_df

