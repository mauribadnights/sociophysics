import sys
sys.path.append('../')
from libraries.dataManipulation import *
import time
import datetime
import pandas as pd

def division_by_direction(data):
    data['time'] = (data['date_time_utc'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
    directions = direction_label(data)
    stats = directions['direction'].value_counts(normalize=True)*100
    if stats['undefined'] > 2:
        print('WARNING: Results might be wrong, large number of undefined direction objects.')
    data['direction'] = 'unassigned'
    directions_dict = directions.set_index('tracked_object')['direction'].to_dict()
    data['direction'] = data['tracked_object'].map(directions_dict)
    data_off = data[data['direction']=='offboarding']
    data_on = data[data['direction']=='onboarding']
    data_off = data_off.drop('direction',axis=1)
    data_on = data_on.drop('direction',axis=1)
    return (data_on, data_off)

def division_by_train_presence(data_on):
    train_data = SociophysicsDataHandler()
    train_data.fetch_prorail_train_information(station='ehv')
    train_data = train_data.train_information

    train_data = train_data.drop(columns=['date', 'station', 'door_no', 'door_x', 'door_y'])

    def to_unix_timestamp(dt):
        return dt.timestamp()

    train_data['arrival_unix'] = train_data['arrival_time'].apply(to_unix_timestamp)
    train_data['departure_unix'] = train_data['departure_time'].apply(to_unix_timestamp)
    
    unix_timestamp_day_start = data_on.iloc[0]['time']
    unix_timestamp_day_end = data_on.iloc[-1]['time']
    day_train_data = train_data[(train_data['arrival_unix'] > unix_timestamp_day_start) & (train_data['departure_unix'] < unix_timestamp_day_end)]
    day_train_data = day_train_data.reset_index(drop=True)

    trains_in_day = len(day_train_data.index)
    data_on['train'] = False
    for train in range(trains_in_day):
        arrival = day_train_data.loc[train]['arrival_unix']
        departure = day_train_data.loc[train]['departure_unix']
        data_on.loc[(data_on['time'] > arrival) & (data_on['time'] < departure), 'train'] = True

    data_on_train = data_on[data_on['train']==True]
    data_on_no_train = data_on[data_on['train']==False]
    data_on_train = data_on_train.drop('train',axis=1)
    data_on_no_train = data_on_no_train.drop('train',axis=1)

    return(data_on_train, data_on_no_train)
