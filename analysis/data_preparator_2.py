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
    #data_on['time'] = data_on['Time']
    train_data = SociophysicsDataHandler()
    train_data.fetch_prorail_train_information(station='ehv')
    train_data = train_data.train_information

    train_data = train_data.drop(columns=['date', 'station'])

    def to_unix_timestamp(dt):
        return dt.timestamp()

    train_data['arrival_unix'] = train_data['arrival_time'].apply(to_unix_timestamp)
    train_data['departure_unix'] = train_data['departure_time'].apply(to_unix_timestamp)

    train_data_no_nan = train_data.dropna()
    #limit rows to 1 row per train (individual door information deleted)
    train_data_filtered = train_data_no_nan.drop_duplicates('arrival_time')


    
    unix_timestamp_day_start = data_on.Time[0]
    unix_timestamp_day_end = data_on['Time'].iloc[-1]
    day_train_data = train_data_filtered[(train_data_filtered['arrival_unix'] > unix_timestamp_day_start) & (train_data_filtered['departure_unix'] < unix_timestamp_day_end)]
    day_train_data = day_train_data.reset_index(drop=True)

    day_train_data = day_train_data.assign(train_position=lambda x: np.where(x['door_y'] > 2500, 'top', 'bottom'))

    trains_in_day = len(day_train_data.index)
    data_on['train'] = 'No train' 
    for train in range(trains_in_day):
        arrival = day_train_data.loc[train]['arrival_unix']
        departure = day_train_data.loc[train]['departure_unix']
        
        data_on.loc[(data_on['time'] > arrival) & (data_on['time'] < departure), 'train'] = True

    data_on_train = data_on[data_on['train']==True]
    data_on_no_train = data_on[data_on['train']==False]
    data_on_train = data_on_train.drop('train',axis=1)
    data_on_no_train = data_on_no_train.drop('train',axis=1)

    return(data_on_train, data_on_no_train)

def division_by_train_position(data_on):
    data_on['time'] = data_on['Time']
    train_data = SociophysicsDataHandler()
    train_data.fetch_prorail_train_information(station='ehv')
    train_data = train_data.train_information

    train_data = train_data.drop(columns=['date', 'station'])

    def to_unix_timestamp(dt):
        return dt.timestamp()

    train_data['arrival_unix'] = train_data['arrival_time'].apply(to_unix_timestamp)
    train_data['departure_unix'] = train_data['departure_time'].apply(to_unix_timestamp)

    train_data_no_nan = train_data.dropna()
    #limit rows to 1 row per train (individual door information deleted)
    train_data_filtered = train_data_no_nan.drop_duplicates('arrival_time')

    unix_timestamp_day_start = data_on.iloc[0]['time']
    unix_timestamp_day_end = data_on.iloc[-1]['time']
    day_train_data = train_data_filtered[(train_data_filtered['arrival_unix'] > unix_timestamp_day_start) & (train_data_filtered['departure_unix'] < unix_timestamp_day_end)]
    day_train_data = day_train_data.reset_index(drop=True)

    day_train_data = day_train_data.assign(train_position=lambda x: np.where(x['door_y'] > 2500, 'top', 'bottom'))

    day_train_data = day_train_data.drop(columns=['arrival_time', 'departure_time', 'door_no', 'door_x', 'door_y'])

    trains_in_day = len(day_train_data.index)
    data_on['train'] = 'no train' 
    for train in range(trains_in_day):
        arrival = day_train_data.loc[train]['arrival_unix']
        departure = day_train_data.loc[train]['departure_unix']
        if day_train_data.loc[train]['train_position'] == 'top':
            data_on.loc[(data_on['time'] > arrival) & (data_on['time'] < departure) & (data_on['train'] == 'no train'), 'train'] = 'top'
            data_on.loc[(data_on['time'] > arrival) & (data_on['time'] < departure) & (data_on['train'] == 'bottom'), 'train'] = 'both'
        elif day_train_data.loc[train]['train_position'] == 'bottom':
            data_on.loc[(data_on['time'] > arrival) & (data_on['time'] < departure) & (data_on['train'] == 'no train'), 'train'] = 'bottom'
            data_on.loc[(data_on['time'] > arrival) & (data_on['time'] < departure) & (data_on['train'] == 'top'), 'train'] = 'both'

    data_on_train_top = data_on[data_on['train']=='top']
    data_on_train_bottom = data_on[data_on['train']=='bottom']
    data_on_train_both = data_on[data_on['train']=='both']
    data_on_no_train = data_on[data_on['train']=='no train']

    data_on_train_top = data_on_train_top.drop('train',axis=1)
    data_on_train_bottom = data_on_train_bottom.drop('train',axis=1)
    data_on_train_both = data_on_train_both.drop('train',axis=1)
    data_on_no_train = data_on_no_train.drop('train',axis=1)

    return [data_on_no_train, data_on_train_top, data_on_train_bottom, data_on_train_both]

def data_division(data):
    (data_on, data_off) = division_by_direction(data)
    data_on_array = division_by_train_position(data_on)
    return (data_on_array, data_off)

