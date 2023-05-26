import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
STRICT_DATA_CHECKING = False
def data_checking_warning_or_error(message):
    if STRICT_DATA_CHECKING:
        raise Exception(message)
    else:
        print(message)

#create FILE_DATE_ID for use in file names
FILE_DATE_ID = datetime.now().strftime('%Y%m%d')
#read in data
#%%
#load data from pickle
plotting_df = pd.read_pickle('../intermediate_data/data/data_mapped_to_plotting_names_9th.pkl')
# plotting_df.columns
# Index(['scenarios', 'economy', 'year', 'sectors_plotting', 'fuels_plotting',
#        'value'],
#       dtype='object')

charts_mapping = pd.read_pickle('../intermediate_data/data/charts_mapping_9th.pkl')
# charts_mapping.columns Index(['sheet', 'unit', 'table_number', 'table_id', 'scenarios', 'economy',
#    'year', 'sectors_plotting', 'fuels_plotting', 'value', 'legend'],
#   dtype='object')

#import chart_config xlsx
chart_config = pd.read_excel('../config/chart_config.xlsx', sheet_name='variables')


#load in colours dict, make sure top row is not a header
colours_dict = pd.read_csv('../config/colours_dict.csv', header=None)
colours_dict = colours_dict.set_index(colours_dict.columns[0]).to_dict()[colours_dict.columns[1]]

#%%
#####################################################################################################################################
#CREATE DICTS THAT CONTAIN SETTINGS FOR THE GRAPHS WE WILL CREATE
#####################################################################################################################################
#extract the unique sheets we will create:
sheets = charts_mapping['sheet'].unique()

#create a dictionary of the sheets and the dataframes we will use to populate them:
sheet_dfs = {}
for sheet in sheets:
    sheet_dfs[sheet] = ()

    sheet_data = charts_mapping.loc[charts_mapping['sheet'] == sheet]
    sheet_data = sheet_data[['unit', 'value', 'fuels_plotting','sectors_plotting','scenarios','year','table_number','table_id']]
    #pivot the data and create order of cols
    sheet_data = sheet_data.pivot(index=['table_id','unit','fuels_plotting','sectors_plotting','scenarios','table_number'], columns='year', values='value')
    sheet_data = sheet_data.reset_index()

    #add tables to tuple by table number
    for table in sheet_data['table_number'].unique():
        table_data = sheet_data.loc[(sheet_data['table_number'] == table)]
        #drop table number from table data
        table_data = table_data.drop(columns = ['table_number'])
        #add table data to tuple
        sheet_dfs[sheet] = sheet_dfs[sheet] + (table_data,)

#create table_id_to_labels_dict
table_id_to_labels_dict = {}
for sheet in sheets:
    for table in sheet_dfs[sheet]:
        #find key column
        if len(table['fuels_plotting'].unique()) > len(table['sectors_plotting'].unique()):
            key_column = 'fuels_plotting'
        else:
            key_column = 'sectors_plotting'
        table_id_to_labels_dict[table['table_id'].iloc[0]] = table[key_column].unique().tolist()

#save to config 
table_id_to_labels_df = pd.DataFrame.from_dict(table_id_to_labels_dict, orient = 'index')
table_id_to_labels_df.to_csv(f'../config/computer_generated/table_id_to_labels_{FILE_DATE_ID}.csv')
#create table_id_to_chart_type_dict
table_id_to_chart_type_dict = {}
for sheet in sheets:
    for table in sheet_dfs[sheet]:
        table_id_to_chart_type_dict[table['table_id'].iloc[0]] = 'area_chart'
#save to config
table_id_to_chart_type_df = pd.DataFrame.from_dict(table_id_to_chart_type_dict, orient = 'index')
table_id_to_chart_type_df.to_csv(f'../config/computer_generated/table_id_to_chart_type_{FILE_DATE_ID}.csv')
#create table_id_to_chart_position_dict
table_id_to_chart_position_dict = {}
for sheet in sheets:
    for table in sheet_dfs[sheet]:
        table_id_to_chart_position_dict[table['table_id'].iloc[0]] = 'above_table'
#save to config
table_id_to_chart_position_df = pd.DataFrame.from_dict(table_id_to_chart_position_dict, orient = 'index')
table_id_to_chart_position_df.to_csv(f'../config/computer_generated/table_id_to_chart_position_{FILE_DATE_ID}.csv')

# #extract the conifgs data and put in dictss
# table_id_to_chart_position_df = pd.read_csv(f'../config/computer_generated/table_id_to_chart_position_{FILE_DATE_ID}.csv', index_col=0)
# table_id_to_chart_position_dict = table_id_to_chart_position_df.to_dict()[table_id_to_chart_position_df.columns[0]]
# table_id_to_chart_type_df = pd.read_csv(f'../config/computer_generated/table_id_to_chart_type_{FILE_DATE_ID}.csv', index_col=0)
# table_id_to_chart_type_dict = table_id_to_chart_type_df.to_dict()[table_id_to_chart_type_df.columns[0]]
# table_id_to_labels_df = pd.read_csv(f'../config/computer_generated/table_id_to_labels_{FILE_DATE_ID}.csv', index_col=0)
# table_id_to_labels_dict = table_id_to_labels_df.to_dict()[table_id_to_labels_df.columns[0]]






#tell user to check tehse config files and copy them into chart_config.xlsx
print('Please check the following files and copy them into chart_config.xlsx')
# #automatically put them in as new sheets to chart_config.xlsx. make sure not to delete any existing sheets
automatic = False
if automatic:
    #take in exisiting sheets and  where they aren't overwritten, add new sheets
    existing_sheets = pd.ExcelFile('../config/chart_config.xlsx')
    existing_sheet_names = existing_sheets.sheet_names
    existing_sheets = [pd.read_excel('../config/chart_config.xlsx', sheet_name=sheet, index_col=None) for sheet in existing_sheet_names]
    #add new sheets
    chart_config =  pd.ExcelWriter('../config/chart_config.xlsx', engine='xlsxwriter')
    table_id_to_labels_df.to_excel(chart_config, sheet_name='table_id_to_labels')
    table_id_to_chart_type_df.to_excel(chart_config, sheet_name='table_id_to_chart_type')
    table_id_to_chart_position_df.to_excel(chart_config, sheet_name='table_id_to_chart_position')
    #find sheets that are in existing_sheets but not in chart_config and add them
    for sheet in existing_sheet_names:
        if sheet not in chart_config.sheets.keys():
            sheet_df = existing_sheets[existing_sheet_names.index(sheet)]
            sheet_df.to_excel(chart_config, sheet_name=sheet, index=False)
    chart_config.close()
####################################################################################################################################
#CHECK COLOR DATA SATISFIES REQUIREMENTS
####################################################################################################################################

unique_fuels = plotting_df.fuels_plotting.unique()
unique_sectors = plotting_df.sectors_plotting.unique()
unique_fuels_and_sectors = np.concatenate((unique_fuels, unique_sectors))
# colours_dict = {}
# for i in unique_fuels_and_sectors:
#     colours_dict[i] = '#%06X' % np.random.randint(0, 0xFFFFFF)
#check if we have a color for each unique value
#first filter out any keys that arent in unique_fuels_and_sectors
extra_keys = []
missing_keys = []
for key in colours_dict.keys():
    if key not in unique_fuels_and_sectors:
        extra_keys.append(key)
for key in extra_keys:
    del colours_dict[key]
#now check if we have a color for each unique value
for i in unique_fuels_and_sectors:
    if i not in colours_dict.keys():
        data_checking_warning_or_error('colours_dict is misisng a color for ' + i)
        #add missing key to list
        missing_keys.append(i)

if len(extra_keys) > 0:
    data_checking_warning_or_error('colours_dict has extra keys: ' + str(extra_keys))

#save missing keys to csv in intermediate_data in case we want to add them later
if len(missing_keys) > 0:
    missing_keys_df = pd.DataFrame(missing_keys, columns=['missing_keys'])
    missing_keys_df.to_csv(f'../intermediate_data/config/missing_colors_dict_{FILE_DATE_ID}.csv')