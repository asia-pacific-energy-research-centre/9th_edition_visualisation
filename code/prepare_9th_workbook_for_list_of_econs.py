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
#%%
#######################################################

for ECONOMY_ID in AGGREGATE_ECONOMY_MAPPING.keys():#"01_AUS", "02_BD", "03_CDA", "04_CHL", "05_PRC", "06_HKC", "07_INA", "08_JPN", "09_ROK", "10_MAS", "11_MEX", "12_NZ", "13_PNG", "14_PE", "15_PHL", "16_RUS", "17_SGP", "18_CT", "19_THA", "20_USA", "21_VN",'00_APEC', '23b_ONEA', '22_SEA', '23_NEA', '24_OAM', '25_OCE']:#ALL_ECONOMY_IDS:
    print(f"Starting workbook creation for {ECONOMY_ID}\n")
    MAP_DATA = True#False
    if MAP_DATA:
        map_9th_data_to_two_dimensional_plots(FILE_DATE_ID, ECONOMY_ID, EXPECTED_COLS, RAISE_ERROR=False)
        
        charts_mapping_1d = map_9th_data_to_one_dimensional_plots(ECONOMY_ID, EXPECTED_COLS)#, total_emissions_co2, total_emissions_ch4, total_emissions_co2e, total_emissions_no2)
        # Save checkpoint after mapping 1D data
        save_checkpoint(charts_mapping_1d, 'charts_mapping_1d')    
        
    
    #######################################################
    all_charts_mapping_files_dict = gather_charts_mapping_dict(ECONOMY_ID, FILE_DATE_ID, sources = ['energy', 'emissions_co2', 'emissions_ch4', 'emissions_co2e', 'emissions_no2', 'capacity'])
    
    ############################################
    plotting_specifications, plotting_name_to_label_dict, colours_dict, plotting_names_order = load_and_format_configs()
    
    ########################################################
    # Start process
    ########################################################
        
    # PREPARE WORKBOOK
    workbook, writer, space_format, percentage_format, header_format, cell_format1, cell_format2 = workbook_creation_functions.prepare_workbook_for_all_charts(ECONOMY_ID, FILE_DATE_ID)

    
    # Start of the process
    for source in all_charts_mapping_files_dict.keys():
        print(f'Starting mapping for source: {source}')
        charts_mapping_dfs = all_charts_mapping_files_dict[source]
        for charts_mapping in charts_mapping_dfs:
            workbook, writer = workbook_creation_functions.create_sheets_from_mapping_df(workbook, charts_mapping, total_plotting_names, MIN_YEAR, colours_dict, cell_format1, cell_format2, header_format, plotting_specifications, plotting_names_order, plotting_name_to_label_dict, writer, EXPECTED_COLS, ECONOMY_ID)

    
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
    
    workbook, writer = extra_graphs_plotting_functions.create_extra_graphs(workbook, all_charts_mapping_files_dict, total_plotting_names, MIN_YEAR,  plotting_specifications, plotting_names_order,plotting_name_to_label_dict, colours_dict, cell_format1, cell_format2, new_charts_dict, header_format, writer, EXPECTED_COLS, ECONOMY_ID)
    
    # Save the workbook
    writer.close()
    print("Workbook saved successfully.")

    
#%%


#create method to move files to C:\Users\finbar.maunsell\OneDrive - APERC\outlook 9th\Modelling\Visualisation\{ECONOMY_ID}\{ECONOMY_ID}_charts_{CURRENT_DATE_ID}.xlsx from C:\Users\finbar.maunsell\github\9th_edition_visualisation\output\output_workbooks\{ECONOMY_ID}\{ECONOMY_ID}_charts_20241112.xlsx

def move_workbooks_to_onedrive(origin_date_id=FILE_DATE_ID):
    CURRENT_DATE_ID = datetime.now().strftime("%Y%m%d")
    for economy_id in ALL_ECONOMY_IDS:
        source_path = f'C:/Users/finbar.maunsell/github/9th_edition_visualisation/output/output_workbooks/{economy_id}/{economy_id}_charts_{origin_date_id}.xlsx'
        destination_path = f'C:/Users/finbar.maunsell/OneDrive - APERC/outlook 9th/Modelling/Visualisation/{economy_id}/{economy_id}_charts_{CURRENT_DATE_ID}.xlsx'
        
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        # Move the file
        shutil.copy(source_path, destination_path)
        print(f"Moved {source_path} to {destination_path}")
DO_THIS=False
if DO_THIS:
    move_workbooks_to_onedrive(origin_date_id=FILE_DATE_ID)   

        
# %%
