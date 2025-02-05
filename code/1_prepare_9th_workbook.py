#%%
import pickle
import pandas as pd
from datetime import datetime
import os
import shutil
import ast
import workbook_creation_functions
import extra_graphs_plotting_functions
from mapping_functions import gather_charts_mapping_dict, load_and_format_configs
from map_2d_plots import map_9th_data_to_two_dimensional_plots
from map_1d_plots import map_9th_data_to_one_dimensional_plots
from utility_functions import *
import csv
#######################################################
#%%
ECONOMY_ID = '09_ROK'
check_base_year_is_as_expected(ECONOMY_ID)

charts_mapping_1d = map_9th_data_to_one_dimensional_plots(ECONOMY_ID, EXPECTED_COLS)#

save_checkpoint(charts_mapping_1d, f'charts_mapping_1d_{ECONOMY_ID}')   
#%%
MAP_DATA = False#False
if MAP_DATA:
    map_9th_data_to_two_dimensional_plots(FILE_DATE_ID, ECONOMY_ID, EXPECTED_COLS, RAISE_ERROR=False)
        
    charts_mapping_1d = map_9th_data_to_one_dimensional_plots(ECONOMY_ID, EXPECTED_COLS)#, total_emissions_co2, total_emissions_ch4, total_emissions_co2e, total_emissions_no2)
    # Save checkpoint after mapping 1D data
    save_checkpoint(charts_mapping_1d, f'charts_mapping_1d_{ECONOMY_ID}')    
    
#%%
#######################################################
all_charts_mapping_files_dict = gather_charts_mapping_dict(ECONOMY_ID, FILE_DATE_ID, sources = ['energy', 'emissions_co2', 'emissions_ch4', 'emissions_co2e', 'emissions_no2', 'capacity'])
#%%
############################################
plotting_specifications, plotting_name_to_label_dict, colours_dict, plotting_names_order = load_and_format_configs()
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

#%%
new_charts_dict = {
    'Refined products and crude supply': {
        'source': 'energy',
        'sheet_name': 'Refining_and_crude_supply',
        'function': extra_graphs_plotting_functions.create_refined_products_bar_and_net_imports_line,
        'chart_types': ['combined_line_bar'],
},
    'Refining output - incl. low-carbon fuels': {
        'source': 'energy',
        'sheet_name': 'Refining_and_low_carbon_fuels',
        'function': extra_graphs_plotting_functions.create_refining_and_low_carbon_fuels,
        'chart_types': ['line','percentage_bar']
    },
    'Natural gas and LNG supply': {
        'source': 'energy',
        'sheet_name': 'Natural_gas_and_LNG_supply',
        'function': extra_graphs_plotting_functions.create_natural_gas_and_lng_supply_charts,
        'chart_types': ['bar']
    },
    'Liquid biofuels and bioenergy supply': {
        'source': 'energy',
        'sheet_name': 'Liq_and_bioenergy_supply',
        'function': extra_graphs_plotting_functions.create_liquid_biofuels_and_bioenergy_supply_charts,
        'chart_types': ['bar']
    },
}
#%%
workbook, writer = extra_graphs_plotting_functions.create_extra_graphs(workbook, all_charts_mapping_files_dict, total_plotting_names, MIN_YEAR,  plotting_specifications, plotting_names_order,plotting_name_to_label_dict, colours_dict, cell_format1, cell_format2, new_charts_dict, header_format, writer, EXPECTED_COLS, ECONOMY_ID)
#%%
# Save the workbook
writer.close()
print("Workbook saved successfully.")

#%%
