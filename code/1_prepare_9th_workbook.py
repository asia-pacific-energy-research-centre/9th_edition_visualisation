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
import csv

def save_checkpoint(df, name, folder='../intermediate_data/checkpoints/'):
    """
    Save a DataFrame or data object as a checkpoint using pickle.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    filepath = os.path.join(folder, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl")
    with open(filepath, 'wb') as f:
        try:
            pickle.dump(df, f)
            print(f"Checkpoint saved: {filepath}")
        except TypeError as e:
            print(f"Failed to save checkpoint {name}: {e}")

def load_checkpoint(name, folder='../intermediate_data/checkpoints/'):
    """
    Load a checkpoint from a pickle file.
    """
    checkpoints = [f for f in os.listdir(folder) if name in f and f.endswith('.pkl')]
    if not checkpoints:
        raise FileNotFoundError(f"No checkpoint found for {name}")
    checkpoints.sort()  # Sort by timestamp
    filepath = os.path.join(folder, checkpoints[-1])  # Load the latest checkpoint
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    print(f"Checkpoint loaded: {filepath}")
    return data

def data_checking_warning_or_error(message):
    if STRICT_DATA_CHECKING:
        raise Exception(message)
    else:
        print(message)

#######################################################
#%%
# User decides whether to create new checkpoint or load from existing one
LOAD_EXISTING_MAP_DATA = True
LOAD_EXISTING_CHARTS_MAPPING_1D = True

if LOAD_EXISTING_MAP_DATA:
    total_emissions_co2 = load_checkpoint('total_emissions_co2')
    total_emissions_ch4 = load_checkpoint('total_emissions_ch4')
    total_emissions_co2e = load_checkpoint('total_emissions_co2e')
    total_emissions_no2 = load_checkpoint('total_emissions_no2')
else:
    map_data = True
    if map_data:
        total_emissions_co2, total_emissions_ch4, total_emissions_co2e, total_emissions_no2 = map_9th_data_to_two_dimensional_plots(FILE_DATE_ID, ECONOMY_ID, EXPECTED_COLS, RAISE_ERROR=False)
        # Save checkpoint after mapping 2D data
        save_checkpoint(total_emissions_co2, 'total_emissions_co2')
        save_checkpoint(total_emissions_ch4, 'total_emissions_ch4')
        save_checkpoint(total_emissions_co2e, 'total_emissions_co2e')
        save_checkpoint(total_emissions_no2, 'total_emissions_no2')

#%%
if LOAD_EXISTING_CHARTS_MAPPING_1D:
    charts_mapping_1d = load_checkpoint('charts_mapping_1d')
else:
    charts_mapping_1d = map_9th_data_to_one_dimensional_plots(ECONOMY_ID, EXPECTED_COLS, total_emissions_co2, total_emissions_ch4, total_emissions_co2e, total_emissions_no2)
    # Save checkpoint after mapping 1D data
    save_checkpoint(charts_mapping_1d, 'charts_mapping_1d')

#%%
#######################################################
# Read in titles, only, from charts mapping for each available economy for the FILE_DATE_ID.
sources = ['energy', 'emissions_co2', 'emissions_ch4', 'emissions_co2e', 'emissions_no2', 'capacity']
all_charts_mapping_files_dict = {}
for source in sources:
    charts_mapping_files = [x for x in os.listdir('../intermediate_data/data/') if 'charts_mapping' in x and source in x]
    #just in case we accidentally pick up fiels from other sources that are named similarly, check that none of the others are in here:
    #if the source is emissions_co2, we should not have emissions_co2e in the list of files! (this is a bit of a manual check)
    if source == 'emissions_co2':
        charts_mapping_files = [x for x in charts_mapping_files if 'emissions_co2e' not in x]
    charts_mapping_files = [x for x in charts_mapping_files if 'pkl' in x]
    charts_mapping_files = [x for x in charts_mapping_files if FILE_DATE_ID in x]
    charts_mapping_files = [x for x in charts_mapping_files if ECONOMY_ID in x]
    if len(charts_mapping_files) > 1:
        print(f'We have more than 1 charts mapping input for the source {source}, economy {ECONOMY_ID}: {charts_mapping_files}')
    all_charts_mapping_files_dict[source] = []
    for mapping_file in charts_mapping_files:
        charts_mapping_df = pd.read_pickle(f'../intermediate_data/data/{mapping_file}')
        all_charts_mapping_files_dict[source].append(charts_mapping_df)

if len(charts_mapping_files) == 0:
    raise Exception('No charts mapping files found for FILE_DATE_ID: {}'.format(FILE_DATE_ID))

# Add the unique sources from charts_mapping_1d to all_charts_mapping_files_dict
for source in charts_mapping_1d.source.unique():
    all_charts_mapping_files_dict[source] = [charts_mapping_1d[charts_mapping_1d.source == source]]


#%%
############################################
# Import master_config xlsx
plotting_specifications = pd.read_excel('../config/master_config.xlsx', sheet_name='plotting_specifications')
plotting_name_to_label = pd.read_excel('../config/master_config.xlsx', sheet_name='plotting_name_to_label')
colours_dict = pd.read_excel('../config/master_config.xlsx', sheet_name='colors')
with open(f'../intermediate_data/config/plotting_names_order_{FILE_DATE_ID}.pkl', 'rb') as handle:
    plotting_names_order = pickle.load(handle)
################################################################################
# FORMAT CONFIGS
################################################################################
# Convert into dictionary
if len(plotting_specifications.columns) != 2:
    raise Exception('plotting_specifications must have exactly two columns')
plotting_specifications = plotting_specifications.set_index(plotting_specifications.columns[0]).to_dict()[plotting_specifications.columns[1]]
# format anything with [] in it as a list
for key in plotting_specifications.keys():
    # e.g. 
    # Format the bar_years as a list
    # plotting_specifications['bar_years'] = ast.literal_eval(plotting_specifications['bar_years'])
    if '[' in str(plotting_specifications[key]) and ']' in str(plotting_specifications[key]):
        plotting_specifications[key] = ast.literal_eval(plotting_specifications[key])

plotting_name_to_label_dict = plotting_name_to_label.set_index(plotting_name_to_label.columns[0]).to_dict()[plotting_name_to_label.columns[1]]
colours_dict = colours_dict.set_index(colours_dict.columns[0]).to_dict()[colours_dict.columns[1]]

#%%
########################################################
# Start process
########################################################
    
# PREPARE WORKBOOK
workbook, writer, space_format, percentage_format, header_format, cell_format1, cell_format2 = workbook_creation_functions.prepare_workbook_for_all_charts(ECONOMY_ID, FILE_DATE_ID)

#%%
# Start of the process
for source in all_charts_mapping_files_dict.keys():
    print(f'Starting mapping for source: {source}')
    charts_mapping_dfs = all_charts_mapping_files_dict[source]
    for charts_mapping in charts_mapping_dfs:
        workbook, writer = workbook_creation_functions.create_sheets_from_mapping_df(workbook, charts_mapping, total_plotting_names, MIN_YEAR, colours_dict, cell_format1, cell_format2, header_format, plotting_specifications, plotting_names_order, plotting_name_to_label_dict, writer, EXPECTED_COLS, ECONOMY_ID)


# Save the workbook
# writer.close()
# print("Workbook saved successfully.")



#%%
new_charts_dict = {
    'Refined products and crude supply': {
        'source': 'energy',
        'sheet_name': 'Refining_and_crude_supply',
        'function': workbook_creation_functions.create_refined_products_bar_and_net_imports_line,
        'chart_types': ['combined_line_bar'],
},
    'Refining output - incl. low-carbon fuels': {
        'source': 'energy',
        'sheet_name': 'Refining_and_low_carbon_fuels',
        'function': workbook_creation_functions.create_refining_and_low_carbon_fuels,
        'chart_types': ['line','percentage_bar']
    }
}

workbook, writer = workbook_creation_functions.create_extra_graphs(workbook, all_charts_mapping_files_dict, total_plotting_names, MIN_YEAR,  plotting_specifications, plotting_names_order,plotting_name_to_label_dict, colours_dict, cell_format1, cell_format2, new_charts_dict, header_format, writer, EXPECTED_COLS, ECONOMY_ID)
#%%
# Save the workbook
writer.close()
print("Workbook saved successfully.")

#%%

