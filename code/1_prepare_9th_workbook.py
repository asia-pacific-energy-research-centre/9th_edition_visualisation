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
from create_table import create_table_handler
#######################################################
#%%
ECONOMY_ID = '21_VN'#00_APEC'
check_base_year_is_as_expected(ECONOMY_ID)
import_files_from_ebt_system(ECONOMY_ID, ebt_system_file_path='../../Outlook9th_EBT/results/')
clean_up_old_files(ECONOMY_ID)
#files to load
#
#%%
MAP_DATA_2D = True#False
if MAP_DATA_2D:
    map_9th_data_to_two_dimensional_plots(FILE_DATE_ID, ECONOMY_ID, EXPECTED_COLS, RAISE_ERROR=False, TESTING=False)
    
#%%
charts_mapping_1d = map_9th_data_to_one_dimensional_plots(ECONOMY_ID, EXPECTED_COLS)
# Save checkpoint after mapping 1D data
save_checkpoint(charts_mapping_1d, f'charts_mapping_1d_{ECONOMY_ID}')    
    
#%%
#######################################################
all_charts_mapping_files_dict = gather_charts_mapping_dict(ECONOMY_ID, FILE_DATE_ID, sources = ['energy', 'emissions_co2', 'emissions_ch4', 'emissions_co2e', 'emissions_no2', 'capacity'])
#%%
############################################
plotting_specifications, plotting_name_to_label_dict, colours_dict, patterns_dict, plotting_names_order = load_and_format_configs()
#%%
########################################################
# Start process
########################################################
    
# PREPARE WORKBOOK
workbook, writer, space_format, percentage_format, header_format, cell_format1, cell_format2 = workbook_creation_functions.prepare_workbook_for_all_charts(ECONOMY_ID, FILE_DATE_ID)

#%%
# Start of the process
do_this = True
if do_this:
    for source in all_charts_mapping_files_dict.keys():
        print(f'Starting mapping for source: {source}')
        charts_mapping_dfs = all_charts_mapping_files_dict[source]
        for charts_mapping in charts_mapping_dfs:
            workbook, writer, colours_dict = workbook_creation_functions.create_sheets_from_mapping_df(workbook, charts_mapping, total_plotting_names, MIN_YEAR, colours_dict, patterns_dict,cell_format1, cell_format2, header_format, plotting_specifications, plotting_names_order, plotting_name_to_label_dict, writer, EXPECTED_COLS, ECONOMY_ID)

#%%
new_charts_dict = {
    #     'Refined products and crude supply': {
    #         'source': 'energy',
    #         'sheet_name': 'Refining_and_crude_supply',
    #         'function': extra_graphs_plotting_functions.create_refined_products_bar_and_net_imports_line,
    #         'chart_types': ['combined_line_bar'],
    #         'tables': ['refining_and_crude_supply']
    # },
    # 'Refining output - incl. low-carbon fuels': {
    #     'source': 'energy',
    #     'sheet_name': 'Refining_and_low_carbon_fuels',
    #     'function': extra_graphs_plotting_functions.create_refining_and_low_carbon_fuels,
    #     'chart_types': ['line','percentage_bar'],
    #     'tables': ['refining_and_low_carbon_fuels']
    # },
    'Bioenergy supply by fuel type': {
        'source': ['energy'],
        'sheet_name': 'bioenergy_supply_by_type',
        'function': extra_graphs_plotting_functions.create_bioenergy_supply_charts,
        'chart_types': ['bar'],
        'tables': ['bioenergy_supply']
    },
    'Natural gas, LNG and biogas supply': {
        'source': ['energy'],
        'sheet_name': 'Natural_gas_LNG_and_biogas',
        'function': extra_graphs_plotting_functions.create_natural_gas_LNG_and_biogas_supply_charts,
        'chart_types': ['bar'],
        'tables': ['natural_gas_LNG_and_biogas_supply', 'natural_gas_and_LNG_supply']
    },
    'crude_and_ngl_supply':{
        'source': ['energy'],
        'sheet_name': 'crude_and_ngl_supply',
        'function': extra_graphs_plotting_functions.create_crude_and_ngl_supply_charts,
        'chart_types': ['bar'],
        'tables': ['crude_and_ngl_supply']
    },
    'Coal_and_bioenergy':{
        'source': ['energy'],
        'sheet_name': 'coal_and_bioenergy_supply',
        'function': extra_graphs_plotting_functions.create_coal_and_biomass_supply_charts,
        'chart_types': ['bar'],
        'tables': ['coal_and_bioenergy_supply', 'coal_supply']
    },
    'refined_products_and_liquid_biofuels_supply':{
        'source': ['energy'],
        'sheet_name': 'refined_products_and_liq_bio',
        'function': extra_graphs_plotting_functions.create_refined_products_and_liquid_biofuels_supply_charts,
        'chart_types': ['line'],
        'tables': ['refined_products_and_liq_bio', 'refined_products']#'output']#'net_imports', 
    },
    # 'Liquid biofuels and bioenergy supply': {
    #     'source': ['energy'],
    #     'sheet_name': 'Liq_and_bioenergy_supply',
    #     'function': extra_graphs_plotting_functions.create_liquid_biofuels_and_bioenergy_supply_charts,
    #     'chart_types': ['bar'],
    #     'tables': ['liquid_biofuels_and_bioenergy_supply']
    # },
    'Buildings with elec from datacentres': {
        'source': ['energy'],
        'sheet_name': 'buildings_and_datacentre_demand',
        'function': extra_graphs_plotting_functions.create_buildings_with_electricity_from_datacentre_demand_charts,
        'chart_types': ['area'],
        'tables': ['buildings_and_datacentre_demand']
    },    

    'share_imports_within_TPES': {
        'source': ['energy'],
        'sheet_name': 'share_imports_within_TPES',
        'function': extra_graphs_plotting_functions.calc_share_imports_within_adjusted_TPES,
        'chart_types': ['bar'],#area doesnt work since there are negatives. and line doesnt show agregate as sum 
        'tables': ['share_imports_within_TPES',  'net_imports', 'import_dependency']#'share_imports_within_TPES_adjusted',, 'import_dependency_adjusted'
    },
    'co2_emissions_using_seaborn_plotting_library': {
        'source': ['emissions_co2'],
        'sheet_name': 'Emissions_co2_publication',
        'function': extra_graphs_plotting_functions.create_emissions_seaborn,
        'chart_types': ['seaborn', 'seaborn_wedge'],
        'tables': ['co2_emissions_by_sector', 'co2_emissions_by_fuel']
    },
    # 'double_axis_crude_supply_and_refining_capacity': {
    #     'source': ['energy', 'capacity'],
    #     'sheet_name': 'Ref_capacity_and_crude_supply',
    #     'function': extra_graphs_plotting_functions.create_double_axis_crude_supply_and_refining_capacity,
    #     'chart_types': ['double_axis_line_bar'],
    #     'tables': ['refining_capacity_and_crude_supply']
    # },
    'create_hydrogen_input_charts': {
        'source': ['energy'],
        'sheet_name': 'hydrogen_production_inputs',
        'function': extra_graphs_plotting_functions.create_hydrogen_input_charts,
        'chart_types': ['bar'],
        'tables': ['hydrogen_production_inputs']
    },
    
    # 'co2_emissions_wedge_using_seaborn_plotting_library': {
    #     'source': 'emissions_co2',
    #     'sheet_name': 'Emissions_co2_wedge',
    #     'function': extra_graphs_plotting_functions.create_emissions_wedge_seaborn,
    #     'chart_types': ['seaborn'],
    #     'tables': ['co2_emissions_by_sector_wedge', 'co2_emissions_by_fuel_scenario_wedge']
    # },
    # 'co2e_emissions_using_seaborn_plotting_library': {
    #     'source': 'emissions_co2e',
    #     'sheet_name': 'Emissions_co2e_publication',
    #     'function': extra_graphs_plotting_functions.create_emissions_seaborn,
    #     'chart_types': ['seaborn'],
    #     'tables': ['co2e_emissions_by_sector', 'co2e_emissions_by_fuel']
    # },#until we know we want to show co2e then we dont need this
}
#%%

workbook, writer, colours_dict = extra_graphs_plotting_functions.create_extra_graphs(workbook, all_charts_mapping_files_dict, total_plotting_names, MIN_YEAR,  plotting_specifications, plotting_names_order,plotting_name_to_label_dict, colours_dict, patterns_dict, cell_format1, cell_format2, new_charts_dict, header_format, writer, EXPECTED_COLS, ECONOMY_ID)

#%%

if ECONOMY_ID not in AGGREGATE_ECONOMY_MAPPING.keys():
    writer, workbook, table = create_table_handler(workbook, writer, ECONOMY_ID, OUTLOOK_BASE_YEAR, OUTLOOK_LAST_YEAR)
#%%
# Save the workbook
writer.close()
print("Workbook saved successfully.")

#%%