
# Purpose: This script will create the 9th edition workbook for each economy.
#it is the main script for creating the workbook. it will call functions from workbook_creation_functions.py
#%%
import pickle
import pandas as pd
from datetime import datetime
import os
import shutil
import ast
import workbook_creation_functions
from map_2d_plots import map_9th_data_to_two_dimensional_plots
from map_1d_plots import map_9th_data_to_one_dimensional_plots
from utility_functions import *
def data_checking_warning_or_error(message):
    if STRICT_DATA_CHECKING:
        raise Exception(message)
    else:
        print(message)

#######################################################
#%%
map_data = True
if map_data:
    map_9th_data_to_two_dimensional_plots(FILE_DATE_ID, ECONOMY_ID, EXPECTED_COLS, RAISE_ERROR=False)
    
#%%
charts_mapping_1d = map_9th_data_to_one_dimensional_plots(ECONOMY_ID, EXPECTED_COLS)
#%%
#######################################################
#read in titles, only, from charts mapping for each available economy for the FILE_DATE_ID. e.g. charts_mapping_9th_{economy_x}_{FILE_DATE_ID}.pkl. We will use each of these to create a workbook, for each economy

sources = ['energy', 'emissions', 'capacity']
all_charts_mapping_files_dict = {}
for source in sources:
    charts_mapping_files = [x for x in os.listdir('../intermediate_data/data/') if 'charts_mapping' in x and source in x]
    charts_mapping_files = [x for x in charts_mapping_files if 'pkl' in x]
    charts_mapping_files = [x for x in charts_mapping_files if FILE_DATE_ID in x]
    charts_mapping_files = [x for x in charts_mapping_files if ECONOMY_ID in x]
    if len(charts_mapping_files)>1:
        print(f'We have more than 1 charts mapping input for the source {source}, economy {ECONOMY_ID}: {charts_mapping_files}')
        breakpoint()
    all_charts_mapping_files_dict[source] = []
    for mappping_file in charts_mapping_files:
        charts_mapping_df = pd.read_pickle(f'../intermediate_data/data/{mappping_file}')
        all_charts_mapping_files_dict[source].append(charts_mapping_df)

if len(charts_mapping_files) == 0:
    raise Exception('No charts mapping files found for FILE_DATE_ID: {}'.format(FILE_DATE_ID))

#add the unique sources form charts_mapping_1d to all_charts_mapping_files_dict
for source in charts_mapping_1d.source.unique():
    all_charts_mapping_files_dict[source] = [charts_mapping_1d[charts_mapping_1d.source==source]]
    
#%%
############################################
#import master_config xlsx
plotting_specifications = pd.read_excel('../config/master_config.xlsx', sheet_name='plotting_specifications')
plotting_name_to_label = pd.read_excel('../config/master_config.xlsx', sheet_name='plotting_name_to_label')
colours_dict = pd.read_excel('../config/master_config.xlsx', sheet_name='colors')
with open(f'../intermediate_data/config/plotting_names_order_{FILE_DATE_ID}.pkl', 'rb') as handle:
    plotting_names_order = pickle.load(handle)
################################################################################
#FORMAT CONFIGS
################################################################################
#cconvert into dictrionary
if len(plotting_specifications.columns) != 2:
    raise Exception('plotting_specifications must have exactly two columns')
plotting_specifications = plotting_specifications.set_index(plotting_specifications.columns[0]).to_dict()[plotting_specifications.columns[1]]
# Format the bar_years as a list
plotting_specifications['bar_years'] = ast.literal_eval(plotting_specifications['bar_years']) #will be like ['2000', '2010', '2018', '2020', '2030', '2040', '2050'] so format it as a list

plotting_name_to_label_dict = plotting_name_to_label.set_index(plotting_name_to_label.columns[0]).to_dict()[plotting_name_to_label.columns[1]]
colours_dict = colours_dict.set_index(colours_dict.columns[0]).to_dict()[colours_dict.columns[1]]
####################################################################################################################################


#%%
########################################################.
#start process
########################################################.
#PREPARE WORKBOOK
workbook, writer, space_format, percentage_format, header_format, cell_format1, cell_format2 = workbook_creation_functions.prepare_workbook_for_all_charts(ECONOMY_ID, FILE_DATE_ID)
#%%
# Start of the process
for source in all_charts_mapping_files_dict.keys():
    charts_mapping_dfs = all_charts_mapping_files_dict[source]
    for charts_mapping in charts_mapping_dfs:
        workbook, writer = workbook_creation_functions.create_sheets_from_mapping_df(workbook, charts_mapping, total_plotting_names, MIN_YEAR, colours_dict, cell_format1, cell_format2, header_format, plotting_specifications, plotting_names_order, plotting_name_to_label_dict, writer, EXPECTED_COLS, ECONOMY_ID)#workbook, charts_mapping, source, ECONOMY_ID)

#todo add code for macro and renewable share and so on/ 
#save the workbook
writer.close()

#%%

#%%
