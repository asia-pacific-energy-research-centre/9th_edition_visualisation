import shutil
import time
import uuid
import pandas as pd
import workbook_creation_functions
from utility_functions import *
import numpy as np
import create_legend
import re, os, matplotlib.pyplot as plt, seaborn as sns
import pandas as pd
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['hatch.linewidth'] = 3   # default is 1.5

def create_extra_graphs(workbook, all_charts_mapping_files_dict, total_plotting_names, MIN_YEAR,  plotting_specifications, plotting_names_order,plotting_name_to_label_dict, colours_dict, patterns_dict, cell_format1, cell_format2, new_charts_dict, header_format, writer, EXPECTED_COLS,ECONOMY_ID):
    scenarios_list=['reference', 'target']
    #use this to create graphs that are a little more complex than the standard ones. tehse will be deisgned on a case by case basis, using explicit code.
            
    for new_chart in new_charts_dict.keys():
        sources = new_charts_dict[new_chart]['source']
        sheet_name = new_charts_dict[new_chart]['sheet_name']
        function = new_charts_dict[new_chart]['function']
        chart_types = new_charts_dict[new_chart]['chart_types']
        tables = new_charts_dict[new_chart]['tables']
            
        try:
            for source in sources:
                if len(all_charts_mapping_files_dict[source]) != 1:
                    breakpoint()
                    raise Exception(f'Expected exactly 1 charts mapping file for create_extra_graphs() for source {source}, but found {len(all_charts_mapping_files_dict[source])}')
        except:
            breakpoint()
        #check charttypes is  list
        if not isinstance(chart_types, list):
            chart_types = [chart_types]
        
        #concat the df for all soruces:
        charts_mapping = pd.DataFrame()
        for source in sources:
            charts_mapping = pd.concat([all_charts_mapping_files_dict[source][0], charts_mapping], ignore_index=True) 
        # charts_mapping
        #cols: source	table_number	sheet_name	chart_type	chart_title	plotting_name_column	plotting_name	aggregate_name_column	aggregate_name	scenario	year	table_id	value	unit	dimensions
        
        #drop percentage from the chart_type:
        charts_mapping = charts_mapping[~charts_mapping['chart_type'].isin(['percentage', 'percentage_bar'])]
        charts_mapping = charts_mapping[charts_mapping.year >= MIN_YEAR]
        
        #pivot the data so that we have one row per plotting_name, and one column per year
        EXPECTED_COLS_wide = EXPECTED_COLS.copy()
        EXPECTED_COLS_wide.remove('year')
        EXPECTED_COLS_wide.remove('value')
        
        charts_mapping = charts_mapping.pivot(index=EXPECTED_COLS_wide, columns='year', values='value').reset_index()  
        
        #ceck if sheet exists, if not create it, else just empty it
        if sheet_name in workbook.sheetnames:
            raise Exception(f'Sheet {sheet_name} already exists in workbook. Need to create a new sheet for extra graphs or remove the original sheet from the master_config.xlsx')
        workbook.add_worksheet(sheet_name)
        # breakpoint()
        scenario_num = 0
        current_row = 1
        for scenario in scenarios_list:
            NEW_SCENARIO = True
            worksheet = workbook.get_worksheet_by_name(sheet_name)
            charts_mapping_scenario = charts_mapping[charts_mapping.scenario == scenario]
            for original_table_id in tables:
                ##############
                if 'seaborn_wedge' in chart_types:#these need data from both scenarios
                    charts_mapping_scenario = charts_mapping.copy()

                try:
                    charts_to_plot, chart_positions, worksheet,current_row,colours_dict = function(charts_mapping_scenario, sheet_name,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict, cell_format1, cell_format2, scenario_num, scenarios_list, header_format, plotting_specifications, writer, chart_types,ECONOMY_ID, scenario, current_row, original_table_id,NEW_SCENARIO)
                except Exception as e:
                    breakpoint()
                    charts_to_plot, chart_positions, worksheet,current_row, colours_dict = function(charts_mapping_scenario, sheet_name,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict, cell_format1, cell_format2, scenario_num, scenarios_list, header_format, plotting_specifications, writer, chart_types,ECONOMY_ID, scenario, current_row, original_table_id,NEW_SCENARIO)
                    
                NEW_SCENARIO = False#wat is the chart pos and charts to plot when we are looking at imports
                if charts_to_plot is None:
                    continue
                worksheet = workbook_creation_functions.write_charts_to_sheet(charts_to_plot, chart_positions, worksheet)
                
            scenario_num+=1
        
            ###############
    workbook = workbook_creation_functions.order_sheets(workbook, plotting_specifications)
    return workbook, writer, colours_dict
        
def format_sheet_for_other_graphs(data,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet,workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict, cell_format1, cell_format2, max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID,unit_dict, current_scenario, current_row, original_table_id, NEW_SCENARIO,PLOTTING_SEABORN=False,plotting_name_to_chart_type=None):
    #########################
    
    table, chart_types_unused, table_id, plotting_name_column, year_cols_start,num_cols, chart_titles, first_year_col, sheet_name = workbook_creation_functions.format_table(data,plotting_names_order,plotting_name_to_label_dict)
    
    if len(chart_types) == 1 and 'bar' in chart_types and not sheet == 'CO2 emissions components':   
        table = workbook_creation_functions.create_bar_chart_table(table,year_cols_start,plotting_specifications['bar_years'], sheet_name)
    #########################
    column_row = 1
    space_under_tables = 1
    space_above_charts = 1
    space_under_charts = 1
    space_under_titles = 1
    
    table['scenario'] = current_scenario
    
    current_row, current_scenario, worksheet = workbook_creation_functions.add_section_titles(current_row, current_scenario, sheet, worksheet, cell_format1, cell_format2, space_under_titles, table, space_under_tables,unit_dict, ECONOMY_ID, NEW_SCENARIO)
    #drop the scenario column since we dont need it in the table
    table = table.drop(columns=['scenario'])
    
    if len(chart_types) > 0:
        current_row += plotting_specifications['height'] 
        
    worksheet.set_row(current_row, None, header_format)#21 for ref
    
    #write table to sheet
    table.to_excel(writer, sheet_name = sheet, index = False, startrow = current_row)
    current_row += len(table.index) + space_under_tables + column_row
    num_table_rows = len(table.index)
    # table
    # plotting_name_column
    # table_id
    # sheet
    # year_cols_start
    # num_cols
    # max_and_min_values_dict
    # chart_titles
    # first_year_col
    # sheet_name
    
    # #identify and format charts we need to create
    chart_positions = workbook_creation_functions.identify_chart_positions(current_row,num_table_rows,space_under_tables,column_row, space_above_charts, space_under_charts, plotting_specifications,chart_types)
    try:
        worksheet = create_legend.create_legend(colours_dict, patterns_dict, plotting_name_column, table,plotting_specifications, chart_positions, worksheet, ECONOMY_ID,total_plotting_names,chart_types, plotting_name_to_chart_type=plotting_name_to_chart_type)
    except:
        breakpoint()
    if not PLOTTING_SEABORN:
        charts_to_plot = workbook_creation_functions.create_charts(table, chart_types, plotting_specifications, workbook, num_table_rows, plotting_name_column, original_table_id, sheet, current_row, space_under_tables, column_row, year_cols_start, num_cols, colours_dict, patterns_dict,total_plotting_names, max_and_min_values_dict, chart_titles, first_year_col, sheet_name)
    else:
        return None, chart_positions, worksheet, current_scenario, current_row
    return charts_to_plot, chart_positions, worksheet, current_scenario, current_row

# def create_refined_products_bar_and_net_imports_line(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row, original_table_id, NEW_SCENARIO):
#     """    
#     # Add the new chart creation function to the new_charts_dict
#     new_charts_dict = {
#         'Refined products and crude oil net imports': {
#             'source': 'energy',
#             'sheet_name': 'Refined products and crude oil net imports',
#             'function': create_refined_products_bar_and_net_imports_line,
#             'chart_type': 'combined_line_bar'
#         }
#     }
#     """
#     if len(chart_types)!=1:
#         breakpoint()
#         raise Exception('Expected exactly 1 chart type in create_refined_products_bar_and_net_imports_line()')
    
#     #extract the data we want to use for the refined products graph, then do wahtever manipulations and calculations are needed to get it into the right format, then plotit
#     table_id = 'energy_Refining_3'#originally had the following specs in the master config:
# # energy	Refined products supply	Refining	3	bar	fuels_plotting	Refined products	Refining_output	Imports	Exports	Stock change	TPES

#     refined_products = charts_mapping[(charts_mapping.table_id == table_id)]
#     if len(refined_products) == 0:
#         breakpoint()
#         raise Exception(f'No data found for table {table_id} in create_refined_products_bar_and_crude_oil_supply_line()')
#     refined_products.loc[:, 'chart_title'] = 'Refined products and crude oil supply'
#     refined_products.loc[:, 'table_id'] = original_table_id
#     refined_products.loc[:, 'aggregate_name'] = 'Refined products'
#     refined_products.loc[:, 'sheet_name'] = sheet
#     refined_products.loc[:, 'chart_type'] = 'bar'
#     refined_products.loc[:, 'scenario'] = scenarios_list[scenario_num]
#     ######
#     table_id = 'energy_Refining_6'
#     aggregate_name = 'Crude oil & NGL'
    
#     crude_oil_supply_line_IMPORTS = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.plotting_name.isin(['Imports'])) & (charts_mapping.aggregate_name == aggregate_name)]
#     crude_oil_supply_line_EXPORTS = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.plotting_name.isin(['Exports'])) & (charts_mapping.aggregate_name == aggregate_name)]
    
#     crude_oil_supply_line_production = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.plotting_name.isin(['Production'])) & (charts_mapping.aggregate_name == aggregate_name)]
    
#     if len(crude_oil_supply_line_IMPORTS) == 0 or len(crude_oil_supply_line_EXPORTS) == 0 or len(crude_oil_supply_line_production) == 0:
#         breakpoint()
#         raise Exception(f'No data found for table {table_id} in create_refined_products_bar_and_crude_oil_supply_line()')
#     #extract the year cols forw hich we will calculate the net imports by finding 4 digits in the column name
#     year_cols = [col for col in crude_oil_supply_line_IMPORTS.columns if re.search(r'\d{4}', str(col))]
#     #calculate the net imports by taking the difference between imports and exports)
#     crude_oil_supply_line_net_imports = crude_oil_supply_line_IMPORTS.copy()
#     for year in year_cols:
#         if len(crude_oil_supply_line_IMPORTS[year].values) != 1 or len(crude_oil_supply_line_EXPORTS[year].values) != 1:
#             raise Exception(f'Expected exactly 1 value for imports and exports for year {year} in create_refined_products_bar_and_crude_oil_supply_line()')
#         crude_oil_supply_line_net_imports[year] = crude_oil_supply_line_IMPORTS[year].values[0] - crude_oil_supply_line_EXPORTS[year].values[0]
#     ######
#     # crude_oil_supply_line.loc[:, 'plotting_name'] = 'Net crude imports'
#     crude_oil_supply_line_IMPORTS.loc[:, 'plotting_name'] = 'Crude imports'
#     crude_oil_supply_line_EXPORTS.loc[:, 'plotting_name'] = 'Crude exports'
#     crude_oil_supply_line_production.loc[:, 'plotting_name'] = 'Crude production'
#     #add the IMPORTS and EXPORTS to the crude_oil_supply_line df
#     crude_oil_supply_line =pd.concat([crude_oil_supply_line_IMPORTS, crude_oil_supply_line_EXPORTS, crude_oil_supply_line_production])#crude_oil_supply_line_net_imports
#     crude_oil_supply_line.loc[:, 'chart_title'] = 'Refined products and crude oil supply'
#     crude_oil_supply_line.loc[:, 'table_id'] = sheet
#     crude_oil_supply_line.loc[:, 'aggregate_name'] = 'Crude oil & NGL'
#     crude_oil_supply_line.loc[:, 'sheet_name'] = sheet
#     crude_oil_supply_line.loc[:, 'chart_type'] = 'line'
#     crude_oil_supply_line.loc[:, 'scenario'] = scenarios_list[scenario_num]

#     #now concatenate the two dataframes
#     refined_products_and_net_imports = pd.concat([refined_products, crude_oil_supply_line])
    
#     #drop table_number since this is not needed
#     refined_products_and_net_imports = refined_products_and_net_imports.drop(columns=['table_number'])
    
#     ##################
#     max_and_min_values_dict = {}
#     #we woud be better of doing these max and min values manually here sincewe want them to match for the two chart types (and they wont if we use the funciton below)
#     #the max vlaue will ave to be the max betwene the sum of the postivie refined products and the max of the net imports:
#     postive_refined_products = refined_products_and_net_imports[refined_products_and_net_imports['plotting_name'].isin(['Domestic refining', 'Exports', 'Stock change', 'Imports'])]
#     postive_refined_products = refined_products[(refined_products[year_cols] > 0)]# & (refined_products['plotting_name'] != 'Total')]
#     max_value_refined = postive_refined_products[year_cols].sum(axis=0).max()
#     max_value_crude_oil_supply = refined_products_and_net_imports.loc[refined_products_and_net_imports.plotting_name.isin(['Crude production', 'Crude exports', 'Crude imports']), year_cols].max().max()
#     max_value = max(max_value_refined, max_value_crude_oil_supply) 
#     if pd.isna(max_value):
#         max_value = 0
#     max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
        
#     key_max_line = (sheet, 'line', original_table_id, "max")
#     key_max_bar = (sheet, 'bar', original_table_id, "max")
#     key_max_bar_line = (sheet, 'combined_line_bar', original_table_id, "max")
#     #the min value will be the min of the sum of the NEGATIVE refined products and the min of the net imports:#first melt, then filter and then group by and sum
    
#     negative_refined_products = refined_products_and_net_imports[refined_products_and_net_imports['plotting_name'].isin(['Domestic refining', 'Exports', 'Stock change', 'Imports'])]
#     negative_refined_products = negative_refined_products[(negative_refined_products[year_cols] < 0)]# & (refined_products['plotting_name'] != 'Total')]
#     min_value_refined = negative_refined_products[year_cols].sum(axis=0).min()
#     min_value_crude_oil_supply = refined_products_and_net_imports.loc[refined_products_and_net_imports.plotting_name.isin(['Crude production', 'Crude exports', 'Crude imports']), year_cols].min().min()
#     min_value = min(min_value_refined, min_value_crude_oil_supply) 
#     if pd.isna(min_value):
#         min_value = 0
#     min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
        
#     key_min_line = (sheet, 'line', original_table_id, "min")
#     key_min_bar = (sheet, 'bar', original_table_id, "min")
#     key_min_bar_line = (sheet, 'combined_line_bar', original_table_id, "min")
    
#     max_and_min_values_dict[key_max_line] = max_value
#     max_and_min_values_dict[key_max_bar] = max_value
#     max_and_min_values_dict[key_min_line] = min_value
#     max_and_min_values_dict[key_min_bar] = min_value
#     max_and_min_values_dict[key_max_bar_line] = max_value
#     max_and_min_values_dict[key_min_bar_line] = min_value
#     ##################
#     if refined_products_and_net_imports.empty:
#         return None, None, worksheet, current_row, colours_dict
    
#     colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(charts_mapping, colours_dict)
#     patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
#     plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)
    
#     unit_dict = {sheet: 'PJ'}
#     refined_products_and_net_imports.loc[:, 'table_id'] = original_table_id
#     #we should have the columns source	chart_type	plotting_name	plotting_name_column	aggregate_name	aggregate_name_column	scenario	unit	table_id	dimensions	chart_title	sheet_name + year_cols before we call this function
#     charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(refined_products_and_net_imports,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id,NEW_SCENARIO)
    
#     return charts_to_plot, chart_positions, worksheet,current_row

# def create_refining_and_low_carbon_fuels(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row,original_table_id, NEW_SCENARIO):
#     """    
#     # Add the new chart creation function to the new_charts_dict
#     new_charts_dict = {
#         'Refining output - incl. low-carbon fuels': {
#         'source': 'energy',
#         'sheet_name': 'Refining_and_low_carbon_fuels',
#         'function': workbook_creation_functions.create_refining_and_low_carbon_fuels,
#         'chart_type': 'percentage_bar'    
#     }

#     }
    
#     energy	Refining and other transformation	Refining	5	line	sectors_plotting	Refining_output	Other petroleum products	Jet fuel	Ethane	Refinery gas not liquefied	LPG	Fuel oil	Diesel	Kerosene	Naphtha	Aviation gasoline	Gasoline
#     """
#     final_table = pd.DataFrame()
#     for chart_type in chart_types:
#         #extract the data we want to use for the refined products graph, then do wahtever manipulations and calculations are needed to get it into the right format, then plotit
#         table_id = 'energy_Refining_5'
#         refined_products = charts_mapping[(charts_mapping.table_id == table_id)]
#         if len(refined_products) == 0:
#             breakpoint()
#             raise Exception(f'No data found for table {table_id}')
#         refined_products.loc[:, 'chart_title'] = 'Refining output - incl. low-carbon fuels'
#         refined_products.loc[:, 'table_id'] = original_table_id
#         refined_products.loc[:, 'aggregate_name'] = 'Refining and other transformation'
#         refined_products.loc[:, 'sheet_name'] = sheet
        
#         refined_products.loc[:, 'chart_type'] = chart_type
#         refined_products.loc[:, 'scenario'] = scenarios_list[scenario_num]
#         ######
#         table_id = 'energy_Low carbon fuels_1'
#         plotting_names = ['Hydrogen_transformation_output']
#         low_carbon_fuels_hydrogen = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.plotting_name.isin(plotting_names))]

#         if len(low_carbon_fuels_hydrogen) == 0:
#             breakpoint()
#             raise Exception(f'No data found for table {table_id} , plotting names {plotting_names} in create_refining_and_low_carbon_fuels()')
#         #biofuels are in production so charted separately to hydrogen
#         table_id = 'energy_Bioenergy_3'
#         plotting_names = ['Production']
#         low_carbon_fuels_biofuels = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.plotting_name.isin(plotting_names))]
#         if len(low_carbon_fuels_biofuels) == 0:
#             breakpoint()
#             raise Exception(f'No data found for table {table_id} , plotting names {plotting_names} in create_refining_and_low_carbon_fuels()')
#         low_carbon_fuels_hydrogen.loc[:, 'plotting_name'] = 'Hydrogen-based fuels'
#         low_carbon_fuels_biofuels.loc[:, 'plotting_name'] = 'Liquid biofuels'
        
#         #then combine the two dataframes
#         low_carbon_fuels = pd.concat([low_carbon_fuels_hydrogen, low_carbon_fuels_biofuels])
        
#         low_carbon_fuels.loc[:, 'chart_title'] = 'Refining output - incl. low-carbon fuels'
#         low_carbon_fuels.loc[:, 'table_id'] = original_table_id
#         low_carbon_fuels.loc[:, 'aggregate_name'] = 'Refining and other transformation'
#         low_carbon_fuels.loc[:, 'sheet_name'] = sheet
#         low_carbon_fuels.loc[:, 'chart_type'] = chart_type
#         low_carbon_fuels.loc[:, 'scenario'] = scenarios_list[scenario_num]
#         #now concatenate the two dataframes
#         refined_products_and_low_carbon_fuels = pd.concat([refined_products, low_carbon_fuels])
        
#         #drop table_number since this is not needed
#         refined_products_and_low_carbon_fuels = refined_products_and_low_carbon_fuels.drop(columns=['table_number'])
        
#         ##################
#         max_and_min_values_dict = {}
#         #we woud be better of doing these max and min values manually here sincewe want them to match for the two chart types (and they wont if we use the funciton below)
        
#         #extract the year cols forw hich we will calculate the net imports by finding 4 digits in the column name
#         year_cols = [col for col in refined_products_and_low_carbon_fuels.columns if re.search(r'\d{4}', str(col))]
        
#         max_value = refined_products_and_low_carbon_fuels[year_cols].sum(axis=0).max()
#         if pd.isna(max_value):
#             max_value = 0
#         max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
            
#         key_max = (sheet, chart_type, original_table_id, "max")
        
#         min_value = 0#refined_products_and_low_carbon_fuels[year_cols].min().min()
#         min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
            
#         key_min = (sheet, chart_type, original_table_id, "min")
        
#         max_and_min_values_dict[key_max] = max_value
#         max_and_min_values_dict[key_min] = min_value
        
#         ##################
#         final_table = pd.concat([final_table, refined_products_and_low_carbon_fuels])
#         ##################
#     if final_table.empty or final_table[year_cols].sum().sum() == 0:
#         breakpoint()
#         return None, None, worksheet, current_row, colours_dict
#     colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(refined_products_and_low_carbon_fuels, colours_dict)
#     patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
#     plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)
    
#     unit_dict = {sheet: 'PJ'}
#     refined_products_and_low_carbon_fuels.loc[:, 'table_id'] = original_table_id
#     #we should have the columns source	chart_type	plotting_name	plotting_name_column	aggregate_name	aggregate_name_column	scenario	unit	table_id	dimensions	chart_title	sheet_name + year_cols before we call this function
#     charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(refined_products_and_low_carbon_fuels,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id, NEW_SCENARIO)
    
#     return charts_to_plot, chart_positions, worksheet, current_row, colours_dict

# def create_liquid_biofuels_and_bioenergy_supply_charts(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row,original_table_id, NEW_SCENARIO):
#     """    
#     # Add the new chart creation function to the new_charts_dict
#     """
#     final_table = pd.DataFrame()
#     for chart_type in chart_types:
#         #extract the data we want to use for the refined products graph, then do wahtever manipulations and calculations are needed to get it into the right format, then plotit
#         table_id = 'energy_Bioenergy_3'
#         liquid_biofuels_supply = charts_mapping[(charts_mapping.table_id == table_id)]
#         if len(liquid_biofuels_supply) == 0:
#             breakpoint()
#             raise Exception(f'No data found for table {table_id}')
#         liquid_biofuels_supply.loc[:, 'chart_title'] = 'Bioenergy supply'
#         liquid_biofuels_supply.loc[:, 'table_id'] = original_table_id
#         liquid_biofuels_supply.loc[:, 'aggregate_name'] = 'Liquid biofuels'
#         liquid_biofuels_supply.loc[:, 'sheet_name'] = sheet
        
#         liquid_biofuels_supply.loc[:, 'chart_type'] = chart_type
#         liquid_biofuels_supply.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
#         #drop plpotting names = stock change, TPES and bunkers since we dont want to plot these with - LNG as they are for all natural gas (including LNG)
#         liquid_biofuels_supply = liquid_biofuels_supply[~liquid_biofuels_supply.plotting_name.isin(['Stock change', 'TPES', 'Bunkers'])]
#         ######
#         table_id = 'energy_Bioenergy_4'
#         bioenergy_supply = charts_mapping[(charts_mapping.table_id == table_id)]
#         if len(bioenergy_supply) == 0:
#             breakpoint()
#             raise Exception(f'No data found for table {table_id}')
#         bioenergy_supply.loc[:, 'chart_title'] = 'Bioenergy supply'
#         bioenergy_supply.loc[:, 'table_id'] = original_table_id
#         bioenergy_supply.loc[:, 'aggregate_name'] = 'Bioenergy'
#         bioenergy_supply.loc[:, 'sheet_name'] = sheet
        
#         bioenergy_supply.loc[:, 'chart_type'] = chart_type
#         bioenergy_supply.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
#         ##################
#         #join and then take liquid biofuels away from the bioenergy data to get the non-liquid biofuels data:
#         year_cols = [col for col in bioenergy_supply.columns if re.search(r'\d{4}', str(col))]
#         non_year_cols = [col for col in bioenergy_supply.columns if col not in year_cols + ['value']]
#         liquid_biofuels_supply_melt = liquid_biofuels_supply.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
#         bioenergy_supply_melt = bioenergy_supply.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
#         bioenergy_supply = pd.merge(liquid_biofuels_supply_melt, bioenergy_supply_melt, on=['plotting_name', 'year'], how='right', suffixes=('_liq', ''))
#         bioenergy_supply['value'] = bioenergy_supply['value'] - bioenergy_supply['value_liq'].replace(np.nan, 0)
#         bioenergy_supply = bioenergy_supply.drop(columns=[col for col in bioenergy_supply.columns if col.endswith('_liq')])
#         bioenergy_supply = bioenergy_supply.pivot(index=non_year_cols, columns='year', values='value').reset_index()
#         ##################        
#         #add '- LNG' to the plotting names for the LNG data
#         liquid_biofuels_supply.loc[:, 'plotting_name'] = liquid_biofuels_supply['plotting_name'] + ' - Liquid biofuels'
#         bioenergy_supply = pd.concat([bioenergy_supply, liquid_biofuels_supply])
        
#         #drop table_number since this is not needed
#         bioenergy_supply = bioenergy_supply.drop(columns=['table_number'])
        
#         ##################
#         max_and_min_values_dict = {}
        
#         #we woud be better of doing these max and min values manually here since we want them to match for the two chart types (and they wont if we use the funciton below)
        
#         #extract the year cols forw hich we will calculate the net imports by finding 4 digits in the column name
#         year_cols = [col for col in bioenergy_supply.columns if re.search(r'\d{4}', str(col))]
#         non_year_cols = [col for col in bioenergy_supply.columns if col not in year_cols]
#         #drop teh total, set any negative values to 0 and then sum the rest to get the max value
#         positives = bioenergy_supply[(bioenergy_supply['plotting_name']!='TPES')].copy()
#         #melt so we can filter out the negative values
#         positives = positives.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
#         #filter
#         positives = positives[(positives['value'] > 0)].copy()
#         #group by and sum
#         max_value = positives.groupby(['year'])['value'].sum().max()
#         if pd.isna(max_value):
#             max_value = 0
#         max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
            
#         key_max = (sheet, chart_type, original_table_id, "max")
        
#         #the min value will be the min of the sum of the NEGATIVE refined products and the min of the net imports:#first melt, then filter and then group by and sum
#         negatives = bioenergy_supply.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
#         #filter
#         negatives = negatives[(negatives['value'] < 0) & (negatives['plotting_name']!='TPES')].copy()
#         #group by and sum
#         negatives = negatives.groupby(['year'])['value'].sum().reset_index()
#         min_value = negatives.value.min()
#         #if there are no negative values, then the min value will be 0, so check for na
#         if pd.isna(min_value):
#             min_value = 0
#         min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
                    
#         key_min = (sheet, chart_type, original_table_id, "min")
        
#         max_and_min_values_dict[key_max] = max_value
#         max_and_min_values_dict[key_min] = min_value
        
#         ##################
#         final_table = pd.concat([final_table, bioenergy_supply])
#         ##################
#     #check if table is empty or all values are 0
#     if final_table.empty or final_table[year_cols].sum().sum() == 0:        
#         return None, None, worksheet, current_row, colours_dict
#     colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(bioenergy_supply, colours_dict)
#     patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
    
#     plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)
    
#     unit_dict = {sheet: 'PJ'}
#     bioenergy_supply.loc[:, 'table_id'] = original_table_id
#     #we should have the columns source	chart_type	plotting_name	plotting_name_column	aggregate_name	aggregate_name_column	scenario	unit	table_id	dimensions	chart_title	sheet_name + year_cols before we call this function
#     charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(bioenergy_supply,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id, NEW_SCENARIO)
#     return charts_to_plot, chart_positions, worksheet, current_row, colours_dict


def create_natural_gas_LNG_and_biogas_supply_charts(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row,original_table_id, NEW_SCENARIO):
    """    
    # Add the new chart creation function to the new_charts_dict
    new_charts_dict = {
        'Natural gas, LNG and biogas supply': {
        'source': 'energy',
        'sheet_name': 'natural_gas_and_lng_supply',
        'function': workbook_creation_functions.create_natural_gas_and_lng_supply_charts,
        'chart_type': 'bar'    
    }

    }
    
    energy	Refining and other transformation	Refining	5	line	sectors_plotting	Refining_output	Other petroleum products	Jet fuel	Ethane	Refinery gas not liquefied	LPG	Fuel oil	Diesel	Kerosene	Naphtha	Aviation gasoline	Gasoline
    """
    final_table = pd.DataFrame()
    for chart_type in chart_types:
        #extract the data we want to use for the refined products graph, then do wahtever manipulations and calculations are needed to get it into the right format, then plotit
        
        if original_table_id == 'natural_gas_LNG_and_biogas_supply':
            title =  'Figure 9-31. Natural gas, LNG and biogas supply'
        else:
            title = 'Figure 9-31. Natural gas and LNG supply'
        table_id = 'energy_Natural gas_4'
        lng_supply = charts_mapping[(charts_mapping.table_id == table_id)]
        if len(lng_supply) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        lng_supply.loc[:, 'chart_title'] = title
        lng_supply.loc[:, 'table_id'] = original_table_id
        lng_supply.loc[:, 'aggregate_name'] = 'LNG'
        lng_supply.loc[:, 'sheet_name'] = sheet
        
        lng_supply.loc[:, 'chart_type'] = chart_type
        lng_supply.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
        #drop plpotting names = stock change, production TPES and bunkers since we dont want to plot these with - LNG as they are for all natural gas (including LNG)
        lng_supply = lng_supply[~lng_supply.plotting_name.isin(['Stock change', 'TPES', 'Bunkers', 'Production'])]
        
        ######
        table_id = 'energy_Natural gas_3'
        nat_gas_supply = charts_mapping[(charts_mapping.table_id == table_id)]
        if len(nat_gas_supply) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        nat_gas_supply.loc[:, 'chart_title'] = title
        nat_gas_supply.loc[:, 'table_id'] = original_table_id
        nat_gas_supply.loc[:, 'aggregate_name'] = 'Natural gas'
        nat_gas_supply.loc[:, 'sheet_name'] = sheet
        
        nat_gas_supply.loc[:, 'chart_type'] = chart_type
        nat_gas_supply.loc[:, 'scenario'] = scenarios_list[scenario_num]
        ######
        if original_table_id == 'natural_gas_LNG_and_biogas_supply':
                
            table_id = 'energy_Bioenergy_5'
            biogas_supply = charts_mapping[(charts_mapping.table_id == table_id)]
            if len(nat_gas_supply) == 0:
                breakpoint()
                raise Exception(f'No data found for table {table_id}')
            biogas_supply.loc[:, 'chart_title'] = title
            biogas_supply.loc[:, 'table_id'] = original_table_id
            biogas_supply.loc[:, 'aggregate_name'] = 'biogas'
            biogas_supply.loc[:, 'sheet_name'] = sheet
            
            biogas_supply.loc[:, 'chart_type'] = chart_type
            biogas_supply.loc[:, 'scenario'] = scenarios_list[scenario_num]
            
            #drop TPES from plotting names
            biogas_supply = biogas_supply[biogas_supply.plotting_name!='TPES']
        
        ##################
        #join and then take LNG away from the Natural gas data to get the non-LNG data:
        year_cols = [col for col in nat_gas_supply.columns if re.search(r'\d{4}', str(col))]
        non_year_cols = [col for col in nat_gas_supply.columns if col not in year_cols + ['value']]
        lng_supply_melt = lng_supply.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        nat_gas_supply_melt = nat_gas_supply.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        nat_gas_supply = pd.merge(lng_supply_melt, nat_gas_supply_melt, on=['plotting_name', 'year'], how='right', suffixes=('_lng', ''))
        nat_gas_supply['value'] = nat_gas_supply['value'] - nat_gas_supply['value_lng'].replace(np.nan, 0)
        nat_gas_supply = nat_gas_supply.drop(columns=[col for col in nat_gas_supply.columns if col.endswith('_lng')])
        nat_gas_supply = nat_gas_supply.pivot(index=non_year_cols, columns='year', values='value').reset_index()
        ##################
        #add '- LNG' to the plotting names for the LNG data
        lng_supply.loc[:, 'plotting_name'] = lng_supply['plotting_name'] + ' - LNG'
        nat_gas_supply.loc[:, 'plotting_name'] = nat_gas_supply['plotting_name'] + ' - Gas'
        nat_gas_supply = pd.concat([nat_gas_supply, lng_supply])
        ###################
        #add in biogas
        
        if original_table_id == 'natural_gas_LNG_and_biogas_supply':
            biogas_supply.loc[:, 'plotting_name'] = biogas_supply['plotting_name'] + ' - Biogas'
            nat_gas_supply = pd.concat([nat_gas_supply, biogas_supply])
        
        ###################
        #drop table_number since this is not needed
        nat_gas_supply = nat_gas_supply.drop(columns=['table_number'])
        
        ##################
        max_and_min_values_dict = {}
        
        #we woud be better of doing these max and min values manually here since we want them to match for the two chart types (and they wont if we use the funciton below)
        
        #extract the year cols forw hich we will calculate the net imports by finding 4 digits in the column name
        year_cols = [col for col in nat_gas_supply.columns if re.search(r'\d{4}', str(col))]
        non_year_cols = [col for col in nat_gas_supply.columns if col not in year_cols]
        #the max value is the max of the sum of the positive refined products:
        positives = nat_gas_supply.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        #filter
        positives = positives[positives['value'] > 0]
        #group by and sum
        positives = positives.groupby(['year'])['value'].sum().reset_index()
        max_value = positives.value.max()
        if pd.isna(max_value):
            max_value = 0
        max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
            
        key_max = (sheet, chart_type, original_table_id, "max")
            
        #the min value will be the min of the sum of the NEGATIVE refined products and the min of the net imports:#first melt, then filter and then group by and sum
        negatives = nat_gas_supply.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        #filter
        negatives = negatives[negatives['value'] < 0]
        #group by and sum
        negatives = negatives.groupby(['year'])['value'].sum().reset_index()
        min_value = negatives.value.min()
        if pd.isna(min_value):
            min_value = 0
        min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
                    
        key_min = (sheet, chart_type, original_table_id, "min")
        
        max_and_min_values_dict[key_max] = max_value
        max_and_min_values_dict[key_min] = min_value
        
        ##################
        final_table = pd.concat([final_table, nat_gas_supply])
        ##################
    if final_table.empty or final_table[year_cols].sum().sum() == 0:
        breakpoint()
        return None, None, worksheet, current_row, colours_dict
    try:
        colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(nat_gas_supply, colours_dict)
    except:
        breakpoint()
    patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
    
    plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)
    
    unit_dict = {sheet: 'PJ'}
    nat_gas_supply.loc[:, 'table_id'] = original_table_id
    #we should have the columns source	chart_type	plotting_name	plotting_name_column	aggregate_name	aggregate_name_column	scenario	unit	table_id	dimensions	chart_title	sheet_name + year_cols before we call this function
    charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(nat_gas_supply,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id,NEW_SCENARIO)
    
    return charts_to_plot, chart_positions, worksheet, current_row, colours_dict

def create_buildings_with_electricity_from_datacentre_demand_charts(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row,original_table_id, NEW_SCENARIO):
    """    
    # Add the new chart creation function to the new_charts_dict
    new_charts_dict = {
        'Buildings': {
        'source': 'energy',
        'sheet_name': 'buildings_and_datacentre_demand',
        'function': workbook_creation_functions.create_buildings_with_electricity_from_datacentre_demand_charts,
        'chart_type': 'bar'    
    }    
    """
    final_table = pd.DataFrame()
    for chart_type in chart_types:
        #extract the data we want to use
        table_id = 'energy_Buildings_2'
        buildings_demand_by_fuel = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.chart_type == 'area') ]
        
        if len(buildings_demand_by_fuel) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        buildings_demand_by_fuel.loc[:, 'chart_title'] = 'Fig 9-9 Buildings energy demand by fuel'
        buildings_demand_by_fuel.loc[:, 'table_id'] = original_table_id
        buildings_demand_by_fuel.loc[:, 'aggregate_name'] = 'Buildings'
        buildings_demand_by_fuel.loc[:, 'sheet_name'] = sheet
        
        buildings_demand_by_fuel.loc[:, 'chart_type'] = chart_type
        buildings_demand_by_fuel.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
        # #extract order of plotting names from plotting_names_order or use origainl order?
        # breakpoint()
        ######
        table_id = 'energy_Buildings_1'
        
        #extract where plotting name is Data centres & AI. we will minus this from leectriicty in buildings_demand by fuel and show it as 'Electricity - data centres'
        data_centres = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.chart_type == 'area') & (charts_mapping['plotting_name'] == 'Data centres & AI')]
        if len(data_centres) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        data_centres.loc[:, 'chart_title'] = 'Fig 9-9 Buildings energy demand by fuel'
        data_centres.loc[:, 'table_id'] = original_table_id
        data_centres.loc[:, 'aggregate_name'] = 'Buildings'
        data_centres.loc[:, 'sheet_name'] = sheet
        
        data_centres.loc[:, 'chart_type'] = chart_type
        data_centres.loc[:, 'scenario'] = scenarios_list[scenario_num]
        #rename the plotting name to 'Electricity - data centres'
        data_centres.loc[:, 'plotting_name'] = 'Electricity - data centres'
        
        ##################
        #join and then take Data centres away from the buildings data to get the non-Data centres data:
        year_cols = [col for col in data_centres.columns if re.search(r'\d{4}', str(col))]
        non_year_cols = [col for col in data_centres.columns if col not in year_cols + ['value']]
        buildings_demand_by_fuel_melt = buildings_demand_by_fuel.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        data_centres_melt = data_centres.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        buildings_demand_by_fuel_melt = pd.merge(buildings_demand_by_fuel_melt, data_centres_melt, on=['year'], how='right', suffixes=('', '_datacentres'))
        #where plotting_name is electricity, take away the data centres value
        buildings_demand_by_fuel_melt.loc[buildings_demand_by_fuel_melt['plotting_name'] == 'Electricity', 'value'] = buildings_demand_by_fuel_melt['value'] - buildings_demand_by_fuel_melt['value_datacentres'].replace(np.nan, 0)
        buildings_demand_by_fuel_melt = buildings_demand_by_fuel_melt.drop(columns=[col for col in buildings_demand_by_fuel_melt.columns if col.endswith('_datacentres')])
        #then concatenate the two dataframes
        buildings_demand_by_fuel_melt = pd.concat([buildings_demand_by_fuel_melt, data_centres_melt])
        # breakpoint()
        buildings_demand_by_fuel_wide = buildings_demand_by_fuel_melt.pivot(index=non_year_cols, columns='year', values='value').reset_index()
        #make table number 1, chart_type to area, aggregate name to buildings, chart title to Buildings, aggregate_name_column to sectors_plotting
        
        #drop table_number since this is not needed
        buildings_demand_by_fuel_wide = buildings_demand_by_fuel_wide.drop(columns=['table_number'])
        buildings_demand_by_fuel_wide.loc[:, 'chart_type'] = 'area'
        buildings_demand_by_fuel_wide.loc[:, 'aggregate_name'] = 'Buildings'
        buildings_demand_by_fuel_wide.loc[:, 'chart_title'] = 'Fig 9-9 Buildings energy demand by fuel'
        buildings_demand_by_fuel_wide.loc[:, 'aggregate_name_column'] = 'sectors_plotting'
        
        ##################
        max_and_min_values_dict = {}
        #we woud be better of doing these max and min values manually here since we want them to match for the two chart types (and they wont if we use the funciton below)
        
        #extract the year cols forw hich we will calculate the net imports by finding 4 digits in the column name
        year_cols = [col for col in buildings_demand_by_fuel_wide.columns if re.search(r'\d{4}', str(col))]
        non_year_cols = [col for col in buildings_demand_by_fuel_wide.columns if col not in year_cols]
        #the max value is the max of the sum of the positive refined products:
        positives = buildings_demand_by_fuel_melt.copy()
        #filter
        positives = positives[positives['value'] > 0]
        #group by and sum, excet exclude the total
        positives = positives[positives['plotting_name'] != 'TFEC']
        positives = positives.groupby(['year'])['value'].sum().reset_index()
        max_value = positives.value.max()
        if pd.isna(max_value):
            max_value = 0
        max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
            
        key_max = (sheet, chart_type, original_table_id, "max")
        
            
        #the min value will be the min of the sum of the NEGATIVE refined products and the min of the net imports:#first melt, then filter and then group by and sum
        negatives = buildings_demand_by_fuel_melt.copy()
        #filter
        negatives = negatives[(negatives['value'] < 0) & (negatives['plotting_name'] != 'TFEC')]
        #group by and sum
        negatives = negatives.groupby(['year'])['value'].sum().reset_index()
        min_value = negatives.value.min()
        if pd.isna(min_value):
            min_value = 0
        min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
                    
        key_min = (sheet, chart_type, original_table_id, "min")
        
        max_and_min_values_dict[key_max] = max_value
        max_and_min_values_dict[key_min] = min_value
        
        ##################
        final_table = pd.concat([final_table, buildings_demand_by_fuel_wide])
        ##################
    if final_table.empty or final_table[year_cols].sum().sum() == 0:
        breakpoint()
        return None, None, worksheet, current_row, colours_dict
    
    #set the order of the plotting names in the table so that data centres and electricity are plotted at the top of the cahrt.
    plotting_names = final_table.plotting_name.unique()
    order_1 = [pn for pn in plotting_names_order['energy_Buildings_2'] if pn in plotting_names]
    plotting_names_order[original_table_id] = [pn for pn in order_1 if pn != 'Electricity'] + ['Electricity', 'Electricity - data centres']
    
    #add the datacentres pattern to patterns_dict:
    patterns_dict['Electricity - data centres'] = 'wide_downward_diagonal'
    
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(data_centres, colours_dict)
    patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
    
    plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)
    
    unit_dict = {sheet: 'PJ'}
    final_table.loc[:, 'table_id'] = original_table_id
    
    #we should have the columns source	chart_type	plotting_name	plotting_name_column	aggregate_name	aggregate_name_column	scenario	unit	table_id	dimensions	chart_title	sheet_name + year_cols before we call this function
    expected_cols = ['source', 'chart_type', 'plotting_name', 'plotting_name_column', 'aggregate_name', 'aggregate_name_column', 'scenario', 'unit', 'table_id', 'dimensions', 'chart_title', 'sheet_name']
    if not all([col in final_table.columns for col in expected_cols]):
        breakpoint()
        raise Exception(f'Not all expected columns found in final_table: {expected_cols}')
    # breakpoint()
    charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(final_table,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id,NEW_SCENARIO)
    
    return charts_to_plot, chart_positions, worksheet, current_row, colours_dict

def calc_share_imports_within_adjusted_TPES(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row, original_table_id, NEW_SCENARIO):
    """    
    # Add the new chart creation function to the new_charts_dict
    new_charts_dict = {
        'share_imports_within_TPES': {
        'source': 'energy',
        'sheet_name': 'share_imports_within_TPES',
        'function': extra_graphs_plotting_functions.calc_share_imports_within_TPES_adjusted,
        'chart_type': 'bar'    
    }    
    
    #NOTE THIS IS A BIT DIFFERENT TO THE OTHER PLOTTING SCRIPTS SINCE IT IS MEANT TO RUN FOR TWO TALBE ID'S. IT WILL IDENTIFY WAHT ONEIS BEING USED AND CHANGE A FEW THINGS ACCORDINGLY
    """
    # breakpoint()
    #times the TPES by ADJUSMTENT_FACTOR to account ofr renewables being 1-1 with their electricity production but other fuels being less efficient
    ADJUSTMENT_FACTOR = 2.5
    ONE_HUNDRED_PERCENT_EFF_RENEWABLES = [
        '09_nuclear',
        '10_hydro',
        '12_01_of_which_photovoltaics',
        '12_solar_unallocated',
        '13_tide_wave_ocean',
        '14_wind'
    ]
    bar_years = plotting_specifications['bar_years']
    net_imports_final_table = pd.DataFrame()
    import_share_of_tpes_final_table = pd.DataFrame()
    max_and_min_values_dict_net_imports={}
    max_and_min_values_dict_tpes = {}
    for chart_type in chart_types:
        # breakpoint()
        #extract the data we want to use for calcaulting net imports by major fuel type and then sum up total tpes then calcualte the share of tehse. Then create a graph for the share by fuel as well as a graph for total imports. and within, do wahtever manipulations and calculations are needed to get it into the right format, then plotit
        table_id = 'energy_Supply & production_4'
        imports = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.chart_type == 'line') ]
        if len(imports) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        imports.loc[:, 'chart_title'] = 'Net imports adjusted'
        imports.loc[:, 'aggregate_name'] = 'Net imports adjusted'
        imports.loc[:, 'sheet_name'] = sheet
        imports.loc[:, 'table_id'] = original_table_id
        imports.loc[:, 'chart_type'] = chart_type
        imports.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
        ######
        table_id = 'energy_Supply & production_5'
        
        exports = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.chart_type == 'line')]
        year_cols = [col for col in exports.columns if re.search(r'\d{4}', str(col))]
        if exports.aggregate_name.nunique() > 1:
            raise Exception(f'Found more than one aggregate name in table {table_id}')        
        elif exports.aggregate_name.unique()[0] == 'Exports_positive':
            #make it negative so we can calcautle the net imports
            exports.loc[:, year_cols] = exports[year_cols] * -1
        elif exports.aggregate_name.unique()[0] != 'Exports':
            raise Exception(f'Found aggregate name in table {table_id} that is not Exports or Exports_positive')
        
        if len(exports) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        
        exports.loc[:, 'chart_title'] = 'Net imports adjusted'
        exports.loc[:, 'aggregate_name'] = 'Net imports adjusted'
        exports.loc[:, 'sheet_name'] = sheet
        exports.loc[:, 'table_id'] = original_table_id
        exports.loc[:, 'chart_type'] = chart_type
        exports.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
        #concat the two dataframes since we'lll jsut sum up their values to get the total TPES
        net_imports = pd.concat([imports, exports])
        
        # breakpoint()#need ti di this
        #get all the plotting names. they should be fuels. and map them to more simple categories:
        unique_plotting_names = net_imports['plotting_name'].unique()
        
        #     array(['Aviation gasoline', 'Biofuels', 'Coal', 'Crude oil & NGL',
        #    'Diesel', 'Ethane', 'Fuel oil', 'Gas', 'Gasoline',
        #    'Hydrogen-based fuels', 'Jet fuel', 'Kerosene', 'LPG', 'Naphtha',
        #    'Other petroleum products', 'Others_tpes',
        #    'Refinery gas not liquefied', 'Total_fuels'], dtype=object)

        # breakpoint()
        plotting_names_mapping = {'Aviation gasoline':'Refined fuels', 'Biofuels':'Others', 'Coal':'Coal', 'Crude oil & NGL':'Crude', 'Diesel':'Refined fuels', 'Ethane':'Natural gas', 'Fuel oil':'Refined fuels', 'Gas':'Natural gas', 'Gasoline':'Refined fuels', 'Hydrogen-based fuels':'Others', 'Jet fuel':'Refined fuels', 'Kerosene':'Refined fuels', 'LPG':'Refined fuels', 'Naphtha':'Refined fuels', 'Other petroleum products':'Refined fuels', 'Others_tpes':'Others', 'Refinery gas not liquefied':'Natural gas', 'Total_fuels':'Total'}
        #where something doesnt map to seomthing in the plotting_names_mapping create an error so we know to add it and then adjsut colors too.
        unmapped_values = net_imports['plotting_name'][~net_imports['plotting_name'].isin(plotting_names_mapping.keys())]
        if not unmapped_values.empty:
            breakpoint()
            raise ValueError(f"Unmapped plotting names found: {unmapped_values.unique()}")
        net_imports.loc[:, 'plotting_name'] = net_imports['plotting_name'].map(plotting_names_mapping)
        
        #melt the data so we can sum up the values by year
        net_imports = net_imports.melt(id_vars=[col for col in net_imports.columns if col not in year_cols], value_vars=year_cols, var_name='year', value_name='value').copy()
        # breakpoint()
        #sum up the values to get the total net imports
        net_imports = net_imports.groupby(['year', 'source', 'plotting_name_column', 'dimensions', 'plotting_name', 'aggregate_name', 'aggregate_name_column', 'scenario', 'unit', 'table_id', 'chart_title', 'sheet_name'])['value'].sum(numeric_only=True).reset_index()
        #drop years not in bar_years or the int version of bar_years
        
        net_imports = net_imports[net_imports['year'].isin(bar_years) | net_imports['year'].isin([int(year) for year in bar_years])]  
        ##################
        
        #now grab the total TPES:
        table_id = 'energy_Supply & production_3'
        TPES = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.chart_type == 'line') & (charts_mapping['plotting_name'] == 'TPES')]
        if len(TPES) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        #melt tpes
        TPES = TPES.melt(id_vars=[col for col in TPES.columns if col not in year_cols], value_vars=year_cols, var_name='year', value_name='value').copy()
        #times the TPES by ADJUSMTENT_FACTOR to account ofr renewables being 1-1 with their electricity production but other fuels being less efficient
        ADJUSTMENT_FACTOR = 2.5
        
        #firslty we need to be sure that there are the folowing fuels in the TPES plotting names, otherwise we may be missing something
        #Nuclear	Hydro	Geothermal	Wind/Solar
        #we will then multiply these by 2.5 to account for the inefficiencies of other fuels
        TPES['value'] = np.where(TPES['plotting_name'].isin(ONE_HUNDRED_PERCENT_EFF_RENEWABLES), TPES['value'] * ADJUSTMENT_FACTOR, TPES['value'])
        
        ######
        
        #now calculate the share of net imports by fuel type. since there is no fuel type within the total TPES, we will have to do this using a left join on the net imports table
        import_share_of_tpes = pd.merge(net_imports, TPES, on=['year', 'scenario'], how='left', suffixes=('', '_TPES'))
        import_share_of_tpes['value'] = import_share_of_tpes['value'] / import_share_of_tpes['value_TPES'] * 100
        
        #and make the cols different:
        import_share_of_tpes.loc[:, 'chart_title'] = 'Fig 9-2. Net imports share of adjusted TPES (%)'
        import_share_of_tpes.loc[:, 'aggregate_name'] = 'Net imports share of adjusted TPES (%)'
        exports.loc[:, 'table_id'] = original_table_id
        import_share_of_tpes.loc[:, 'sheet_name'] = sheet
        import_share_of_tpes.loc[:, 'chart_type'] = chart_type
        import_share_of_tpes.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
        net_imports.loc[:, 'chart_title'] = 'Net imports (PJ)'
        net_imports.loc[:, 'aggregate_name'] = 'Net imports (PJ)'
        exports.loc[:, 'table_id'] = original_table_id
        net_imports.loc[:, 'sheet_name'] = sheet
        net_imports.loc[:, 'chart_type'] = chart_type
        net_imports.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
        import_share_of_tpes = import_share_of_tpes.drop(columns=['table_number', 'value_TPES'] + [col for col in import_share_of_tpes.columns if col.endswith('_TPES')])        
        
        ##################
        
        #we woud be better of doing these max and min values manually here since we want them to match for the two chart types (and they wont if we use the funciton below)
        new_dfs_and_other_vars = {'net_imports': {'df': net_imports, 'max_and_min_values_dict': max_and_min_values_dict_net_imports}, 'import_share_of_tpes': {'df': import_share_of_tpes, 'max_and_min_values_dict': max_and_min_values_dict_tpes}}
        for df_name, df_dict in new_dfs_and_other_vars.items():
            df = df_dict['df']
            max_and_min_values_dict = df_dict['max_and_min_values_dict']
            
            maximum = df.copy()
            #filter
            
            if chart_type == 'line':
                maximum = maximum[(maximum['plotting_name'] != 'Total')]
            else:
                maximum = maximum[(maximum['plotting_name'] != 'Total') & (maximum['value'] > 0)]
                maximum = maximum.groupby(['year'])['value'].sum().reset_index()
                
            max_value = maximum.value.max()
            if pd.isna(max_value):
                max_value = 0
            max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
                
            key_max = (sheet, chart_type, original_table_id, "max")
                
            #the min value will be the min of the sum of the NEGATIVE refined products and the min of the net imports:#first melt, then filter and then group by and sum
            minimum = df.copy()
            #filter
            if chart_type == 'line':
                minimum = minimum[(minimum['plotting_name'] != 'Total')]
            else:
                minimum = minimum[(minimum['plotting_name'] != 'Total') & (minimum['value'] < 0)]
                minimum = minimum.groupby(['year'])['value'].sum().reset_index()
            #group by and sum
            min_value = minimum.value.min()
            if pd.isna(min_value):
                min_value = 0
            min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
                        
            key_min = (sheet, chart_type, original_table_id, "min")
            
            if df_name == 'import_share_of_tpes':
                if max_value < 110:
                    max_value = 100
            if min_value > 0:#i think this would already be don e but ok
                min_value = 0
            max_and_min_values_dict[key_max] = max_value
            max_and_min_values_dict[key_min] = min_value
            
            #add them to the list
            new_dfs_and_other_vars[df_name]['max_and_min_values_dict'] = max_and_min_values_dict
            new_dfs_and_other_vars[df_name]['df'] = df
        ##################
        # breakpoint()
        net_imports_final_table = pd.concat([net_imports_final_table, new_dfs_and_other_vars['net_imports']['df']])
        import_share_of_tpes_final_table = pd.concat([import_share_of_tpes_final_table, new_dfs_and_other_vars['import_share_of_tpes']['df']])
        
        max_and_min_values_dict_net_imports = new_dfs_and_other_vars['net_imports']['max_and_min_values_dict']
        max_and_min_values_dict_tpes = new_dfs_and_other_vars['import_share_of_tpes']['max_and_min_values_dict']
        ##################
    # breakpoint()
    if net_imports_final_table.empty or net_imports_final_table.value.sum() == 0 or import_share_of_tpes_final_table.empty or import_share_of_tpes_final_table.value.sum() == 0:
        breakpoint()
        return None, None, worksheet, current_row, colours_dict
    # breakpoint()
    #double check the columns are: year, plotting_name, aggregate_name, aggregate_name_column, scenario, unit, table_id, chart_title, sheet_name, value
    #make the yearsinto columns
    net_imports_final_table = net_imports_final_table.pivot(values='value', index=[col for col in net_imports_final_table.columns if col not in ['value', 'year']], columns='year').reset_index()  
    import_share_of_tpes_final_table = import_share_of_tpes_final_table.pivot(values='value', index=[col for col in import_share_of_tpes_final_table.columns if col not in ['value', 'year']], columns='year').reset_index()
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(import_share_of_tpes_final_table, colours_dict)
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(net_imports_final_table, colours_dict)
    patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
    
    plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)
    
    unit_dict = {sheet: 'PJ'}
    #we should have the columns source	chart_type	plotting_name	plotting_name_column	aggregate_name	aggregate_name_column	scenario	unit	table_id	dimensions	chart_title	sheet_name + year_cols before we call this function
    
    expected_cols = ['source', 'chart_type', 'plotting_name', 'plotting_name_column', 'aggregate_name', 'aggregate_name_column', 'scenario', 'unit', 'table_id', 'dimensions', 'chart_title', 'sheet_name']
    if not all([col in import_share_of_tpes_final_table.columns for col in expected_cols]) or not all([col in net_imports_final_table.columns for col in expected_cols]):
        missing_cols = [col for col in expected_cols if col not in import_share_of_tpes_final_table.columns] + [col for col in expected_cols if col not in net_imports_final_table.columns]
        breakpoint()
        raise Exception(f'Not all expected columns found in final_table: {expected_cols}')
    
    if original_table_id == 'share_imports_within_TPES':
        
        import_share_of_tpes_final_table.loc[:, 'table_id'] = original_table_id
        charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(import_share_of_tpes_final_table,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict_tpes, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id,NEW_SCENARIO)
    elif original_table_id == 'net_imports':
        
        net_imports_final_table.loc[:, 'table_id'] = original_table_id
        charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(net_imports_final_table,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict_net_imports, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id,NEW_SCENARIO)
    else:
        raise ValueError(f'CHART_TO_PLOT must be either share_imports_within_TPES or net_imports')
    return charts_to_plot, chart_positions, worksheet, current_row, colours_dict


def create_emissions_seaborn(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row, original_table_id, NEW_SCENARIO):
    """    
    """
    if 'co2e' in original_table_id:
        #use the co2e version of emissions
        if 'sector' in original_table_id:
            table_id = 'emissions_co2e_Emissions_co2e_2'
            title = f'CO2e Combustion Emissions by sector - {current_scenario}'
            plotting_name_column_name = 'Sector'
        else:
            table_id = 'emissions_co2e_Emissions_co2e_1'
            title = f'CO2e Combustion Emissions by fuel - {current_scenario}'
            plotting_name_column_name = 'Fuel'
    else:
        #use the co2 version of emissions
        if 'sector' in original_table_id:
            table_id = 'emissions_co2_Emissions_co2_2'
            title = f'CO2 Combustion Emissions by sector - {current_scenario}'
            plotting_name_column_name = 'Sector'
        else:
            table_id = 'emissions_co2_Emissions_co2_1'
            title = f'CO2 Combustion Emissions by fuel - {current_scenario}'
            plotting_name_column_name = 'Fuel'           
        
    emissions = charts_mapping[(charts_mapping.table_id == table_id)].copy()
    #filter for the current scenario since we get data from both scenarios in this function
    emissions = emissions[emissions['scenario'] == scenarios_list[scenario_num]]
    if len(emissions) == 0:
        breakpoint()
        raise Exception(f'No data found for table {table_id}')
    emissions.loc[:, 'chart_title'] = title
    emissions.loc[:, 'aggregate_name'] = 'Total combustion emissions'
    emissions.loc[:, 'sheet_name'] = sheet
    emissions.loc[:, 'table_id'] = original_table_id
    emissions.loc[:, 'chart_type'] = chart_types[0]
    emissions.loc[:, 'scenario'] = scenarios_list[scenario_num]
    emissions.rename(columns={'plotting_name':plotting_name_column_name}, inplace=True)
    # breakpoint()
    ###################################
    #START PLOTTING
    ###################################
    LINE_WIDTH = 3
    FONTSIZE = 10
    
    #extract the cols which have years in them
    year_cols = [col for col in emissions.columns if re.search(r'\d{4}', str(col))]
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    # Plot each unique fuel with its corresponding color
    # breakpoint()#whats going wrong here
    #order them using the plotting_names_order dict
    # breakpoint()#do we need to do it this way?
    # unique_plotting_names = plotting_names_order[table_id] 
    
    unique_plotting_names =[
        plotting_name for plotting_name in emissions[plotting_name_column_name].unique()
    ]
    
    # we need to make sure we have all of them in the right order
    ordered_plotting_names = [pn for pn in plotting_names_order[table_id] if pn in unique_plotting_names]    
    unordered = [pn for pn in unique_plotting_names if pn not in ordered_plotting_names]
    
    ordered_plotting_names = ordered_plotting_names + unordered
    
    unique_plotting_names = list(dict.fromkeys(ordered_plotting_names))
    
    #unique_plotting_names + [plotting_name for plotting_name in emissions[plotting_name_column_name].unique() if plotting_name not in plotting_names_order[table_id]]
    #double check for duplicates:
    # unique_plotting_names = list(dict.fromkeys(unique_plotting_names))
    # Identify CCUS-related plotting names
    ccus_keywords = ['carbon capture', 'captured_emissions']
    ccus_plotting_names = [
        plotting_name for plotting_name in unique_plotting_names
        if any(keyword in plotting_name.lower() for keyword in ccus_keywords)
    ]
    # # Initialize a variable to keep track of the cumulative values for stacking
    # cumulative_values = pd.Series([0] * len(year_cols), index=year_cols)

    # #set all values for ccus_plotting_names to -100?
    # # breakpoint()
    # # for plotting_name in ccus_plotting_names:
    # #     emissions.loc[emissions[plotting_name_column_name] == plotting_name, year_cols] = -100
    # for plotting_name in unique_plotting_names:
    #     plotting_data = emissions[emissions[plotting_name_column_name] == plotting_name].copy()
    #     if plotting_data.empty:
    #         continue
    #     for i, row in plotting_data.iterrows():
    #         values = row[year_cols]
    #         color = colours_dict.get(plotting_name, 'gray')
            
    #         # Plot net emissions as its own value, not cumulative
    #         if plotting_name == 'Net emissions':
    #             ax.plot(year_cols, values, color=color, label=plotting_name, linewidth=LINE_WIDTH)
    #         elif plotting_name in ccus_plotting_names:
    #             # ax.fill_between(year_cols, cumulative_values.values.astype(float), (cumulative_values.values + values.values).astype(float), color=color, label=plotting_name, hatch='//')
    #             # hatch overlay
    #             ax.fill_between(year_cols,
    #                             cumulative_values.values.astype(float),
    #                             (cumulative_values.values + values.values).astype(float),
    #                             facecolor='none',
    #                             edgecolor=colours_dict.get(plotting_name, 'gray'),
    #                             hatch='\\\\\\\\',  # Use double backslashes for backward slashes
    #                             linewidth=0.0,
    #                             label=plotting_name,
    #                             zorder=2)
    #             cumulative_values += values
    #         else:
    #             ax.fill_between(year_cols, cumulative_values.values.astype(float), (cumulative_values.values + values.values).astype(float), color=color, label=plotting_name)
    #             cumulative_values += values
    # before the loop:
    pos_cum = pd.Series(0, index=year_cols)
    neg_cum = pd.Series(0, index=year_cols)
    # breakpoint()#why is color of ccus weird for fuels
    for plotting_name in unique_plotting_names:
        plotting_data = emissions[emissions[plotting_name_column_name] == plotting_name]
        if plotting_data.empty: 
            continue

        values = plotting_data.iloc[0][year_cols]
        color  = colours_dict.get(plotting_name, 'gray')

        if plotting_name == 'Net emissions':
            ax.plot(year_cols, values, color=color, label=plotting_name, linewidth=LINE_WIDTH, linestyle='--')

        elif plotting_name in ccus_plotting_names:
            # CCUS goes below zero
            
            v = values.abs().values.astype(float)
            ax.fill_between(
                year_cols,
                neg_cum.values.astype(float),
                (neg_cum.values - v).astype(float),
                facecolor='none',
                edgecolor=color,
                hatch='\\\\',
                linewidth=0.0,
                label=plotting_name,
                zorder=2
            )
            neg_cum -= v

        else:
            # everything else stacks above zero
            v = values.values.astype(float)
            ax.fill_between(
                year_cols,
                pos_cum.values,
                (pos_cum.values + v),
                color=color,
                label=plotting_name
            )
            pos_cum += v
    # breakpoint()#why is net emissions not being added to leegend?
    # CCUS goes below zero
    # breakpoint()#not  seeing any emissions from ccs
    ax.set_ylim( neg_cum.min()*1.1,  pos_cum.max()*1.1 )
    # breakpoint()#how to make power look ok?
    #COMMON PARAMETERS:
    # Draw a horizontal line at y=0 for a clear baseline
    ax.axhline(0, color='black', linewidth=1)
    #draw a dotten vertline at 2022
    ax.axvline(OUTLOOK_BASE_YEAR, color='black', linewidth=1, linestyle='--')
    #make the size of axis font to same
    ax.tick_params(axis='both', which='major', labelsize=FONTSIZE)
    # Set titles and labels using a font similar to Excel (Calibri)
    ax.set_title(title, fontsize=FONTSIZE, fontname='Calibri', pad=20)
    # Add legend off teh chart
    # ax.legend(loc='center left', bbox_to_anchor=(1.4, 0.5), fontsize=FONTSIZE)
    # Set gridlines to appear behind the charted colors
    # breakpoint()#trying to get consistent grid lines
    ax.grid(visible=False, which='major', axis='x')  #
    ax.grid(visible=True, which='major', axis='y')  # only horizontal gridlines
    ax.set_axisbelow(True)
    #make the chart show no gaps after  max and min years
    ax.set_xlim(min(year_cols), max(year_cols))
    # #drop border around the chart
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    #set size of chart image using plotting_specs . width_inches and height_inches

    # Adjust the size of the figure to ensure everything remains visible
    fig.set_size_inches(plotting_specifications['width_inches'], plotting_specifications['height_inches'])#make width 1/3 larger to allow for legend which will be cropped out
    
    # plt.tight_layout()
    #SAVE THE CHART TO THE WORKSHEET
    # breakpoint()
    
    if 'code' in os.getcwd():
        #check file exists
        file_path = f'../intermediate_data/charts/{original_table_id}_{current_scenario}.png'
    else:
        #check file exists
        file_path = f'intermediate_data/charts/{original_table_id}_{current_scenario}.png'
    
    legend = ax.get_legend()
    if legend:
        legend.remove()
    # Save the figure with tight bounding box
    plt.savefig(file_path, dpi=300, bbox_inches='tight')
    ax.set_title('', fontsize=0, fontname='Calibri', pad=0) 
    # for label in ax.get_xticklabels() + ax.get_yticklabels():
    #     label.set_fontsize(FONTSIZE/2)
        
    fig.set_size_inches(plotting_specifications['bar_width_inches'], plotting_specifications['bar_height_inches'])
    plt.savefig(file_path.replace('.png', '_small.png'), dpi=300, bbox_inches='tight')
    # breakpoint()
    plt.close(fig)
    plt.clf()
    plt.close('all')
    # breakpoint()#check the ahtches work
    #create plotting_name_to_chart_type based on the different kinds of charts for each plotting name so our labels match them e.g. lines for line, boxes for area or bar
    # breakpoint()#check order o f legend
    plotting_name_to_chart_type = {}
    for plotting_name in unique_plotting_names:
        plotting_name = plotting_name_to_label_dict.get(plotting_name, plotting_name)
        # Plot net emissions as its own value, not cumulative
        if plotting_name == 'Net emissions':
            plotting_name_to_chart_type[plotting_name] = 'line'
        else:
            plotting_name_to_chart_type[plotting_name] = 'bar'
    # breakpoint()  
    
    ############################################
    #Extract chart positions and add to worksheet
    ############################################
    # # Default values for variables
    # plotting_names_order[original_table_id] = emissions[;plotting_name].unique().tolist()#dont think im needed
    # plotting_name_to_label_dict = {plotting_name: plotting_name for plotting_name in plotting_names_order}#dont think im needed
    max_and_min_values_dict_net_imports = {}
    unit_dict = {}
    #rename plotting_name_column to 'plotting_name'
    emissions.rename(columns={plotting_name_column_name:'plotting_name'}, inplace=True)
    # breakpoint()
    charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(
        emissions,
        plotting_names_order,
        plotting_name_to_label_dict,
        scenario_num,
        scenarios_list,
        header_format,
        worksheet,
        workbook,
        plotting_specifications,
        writer,
        sheet,
        colours_dict,
        patterns_dict,
        cell_format1,
        cell_format2,
        max_and_min_values_dict_net_imports,
        total_plotting_names,
        chart_types,
        ECONOMY_ID,
        unit_dict,
        current_scenario,
        current_row,
        original_table_id,
        NEW_SCENARIO,
        PLOTTING_SEABORN=True,
        plotting_name_to_chart_type=plotting_name_to_chart_type
    )
    # breakpoint()
    # Add the image to the worksheet..
    worksheet.insert_image(chart_positions[0], file_path)
    # Add the small image to the worksheet.. 
    worksheet.insert_image(chart_positions[0], file_path.replace('.png', '_small.png'))
    
    if scenario_num == 0: #we will create an emissions wedge as well as the normal emissions chart 
        #run the wedge chart function instead, sicne most of it requries different processes but we want it in the same sheet
        charts_to_plot, chart_positions, worksheet, current_row, colours_dict = create_emissions_wedge_seaborn(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row, original_table_id, NEW_SCENARIO, charts_to_plot, chart_positions)
        
    return charts_to_plot, chart_positions, worksheet, current_row, colours_dict

def create_emissions_wedge_seaborn(charts_mapping, sheet,
                           plotting_names_order,
                           plotting_name_to_label_dict,
                           worksheet, workbook,
                           colours_dict, patterns_dict,
                           cell_format1, cell_format2,
                           scenario_num, scenarios_list,
                           header_format, plotting_specifications,
                           writer, chart_types, ECONOMY_ID,
                           current_scenario, current_row,
                           original_table_id, NEW_SCENARIO, charts_to_plot=None, chart_positions=None):
    """
    Creates a wedge chart showing the difference between two emissions scenarios.
    Uses similar parameters and helper functions as create_emissions_seaborn.
    Even though it runs at the end of create_emissions_seaborn, it is designed to run just like it, even if that means redoing some of the same work.
    
    Please note that if the emissions are nhigher in target than in ref then the cahrt can look a bit funky. this can happen. luckily it happens mostly when welook at  emissions by fuel, not by sector which is the preferred chart
    """
    # Set Seaborn theme to emulate Excel styling with Calibri font
    sns.set_theme(style="whitegrid", font="Calibri", context="notebook")
    
    # Determine table_id, title, and plotting name column based on original_table_id
    if 'co2e' in original_table_id:
        if 'sector' in original_table_id:
            table_id = 'emissions_co2e_Emissions_co2e_2'
            title = 'CO2e Combustion Emissions by sector'
            plotting_name_column_name = 'Sector'
        else:
            table_id = 'emissions_co2e_Emissions_co2e_1'
            title = 'CO2e Combustion Emissions by fuel'
            plotting_name_column_name = 'Fuel'
    else:
        if 'sector' in original_table_id:
            table_id = 'emissions_co2_Emissions_co2_2'
            title = 'CO2 Combustion Emissions by sector'
            plotting_name_column_name = 'Sector'
        else:
            table_id = 'emissions_co2_Emissions_co2_1'
            title = 'CO2 Combustion Emissions by fuel'
            plotting_name_column_name = 'Fuel'
    
    # Extract emissions data for both sceanrios in scenarios_list if tehre are two:
    if len(scenarios_list) != 2:
        raise ValueError(f"Expected exactly two scenarios in scenarios_list, found {len(scenarios_list)}")
    
    base_scenario = scenarios_list[0]
    NEW_SCENARIO = scenarios_list[1]
    emissions_base = charts_mapping[(charts_mapping.table_id == table_id) &
                                    (charts_mapping['scenario'] == base_scenario)].copy()
    emissions_new = charts_mapping[(charts_mapping.table_id == table_id) &
                                   (charts_mapping['scenario'] == NEW_SCENARIO)].copy()

    # Identify the year columns (e.g., 2020, 2021, …) based on a regex match
    year_cols = [col for col in emissions_base.columns if re.search(r'\d{4}', str(col))]
    
    #double check that sum of emissions in emisisons new is lower than in emissions base
    if emissions_base[year_cols].sum().sum() < emissions_new[year_cols].sum().sum():
        breakpoint()
        raise ValueError(f"Sum of emissions in {NEW_SCENARIO} is higher than in {base_scenario}. the wedge graph will look weird. just change the order of the scenarios in the scenarios_list")
    
    if emissions_base.empty or emissions_new.empty:
        breakpoint()
        raise Exception(f'No data found for table {table_id} for one or both scenarios')
    # breakpoint()#where is power here?
    # Add common meta-data for each (using base for formatting later)
    for df in [emissions_base, emissions_new]:
        df.loc[:, 'chart_title'] = title
        df.loc[:, 'aggregate_name'] = 'Total combustion emissions'
        df.loc[:, 'sheet_name'] = sheet
        df.loc[:, 'table_id'] = original_table_id
        df.loc[:, 'chart_type'] = chart_types[0]
    
    # Rename the plotting column to match our expected column name
    emissions_base.rename(columns={'plotting_name': plotting_name_column_name}, inplace=True)
    emissions_new.rename(columns={'plotting_name': plotting_name_column_name}, inplace=True)
    
    #drop net emissions from both, but check its there first#and same for Total combustion emissions
    for plotting_name in total_plotting_names:
        if plotting_name in emissions_base[plotting_name_column_name].values:
            emissions_base = emissions_base[emissions_base[plotting_name_column_name] != plotting_name]
        if plotting_name in emissions_new[plotting_name_column_name].values:
            emissions_new = emissions_new[emissions_new[plotting_name_column_name] != plotting_name]
    #also drop Net emissions since that isnt in total_plotting anmes
    emissions_base = emissions_base[emissions_base[plotting_name_column_name] != 'Net emissions']
    emissions_new = emissions_new[emissions_new[plotting_name_column_name] != 'Net emissions']
    
    # else:
    #     breakpoint()
    #     raise ValueError(f"Net emissions not found in emissions data. Need to update the code")
    
    # Compute total emissions per year for both scenarios (summing across sectors/fuels)
    total_base = emissions_base[year_cols].sum()
    total_new = emissions_new[year_cols].sum()

    # there's a slight change we have different plotting names in the two scenarios. 
    # unique_plotting_names_base = plotting_names_order[table_id] + [
    #     plotting_name for plotting_name in emissions_base[plotting_name_column_name].unique() 
    #     if plotting_name not in plotting_names_order[table_id]
    # ]
    # unique_plotting_names_new = plotting_names_order[table_id] + [
    #     plotting_name for plotting_name in emissions_new[plotting_name_column_name].unique() 
    #     if plotting_name not in plotting_names_order[table_id]
    # ]
    
    
    unique_plotting_names_base =[
        plotting_name for plotting_name in emissions_base[plotting_name_column_name].unique() 
    ]
    unique_plotting_names_new =[
        plotting_name for plotting_name in emissions_new[plotting_name_column_name].unique() 
    ]
    
    # we need to make sure we have all of them in the right order
    ordered_plotting_names_base = [pn for pn in plotting_names_order[table_id] if pn in unique_plotting_names_base]
    ordered_plotting_names_new = [pn for pn in plotting_names_order[table_id] if pn in unique_plotting_names_new]
    
    unordered_base = [pn for pn in unique_plotting_names_base if pn not in ordered_plotting_names_base]
    unordered_new = [pn for pn in unique_plotting_names_new if pn not in ordered_plotting_names_new]
    
    ordered_plotting_names_base = ordered_plotting_names_base + unordered_base
    ordered_plotting_names_new = ordered_plotting_names_new + unordered_new
    
    unique_plotting_names = list(dict.fromkeys(ordered_plotting_names_base + ordered_plotting_names_new))

    # Instead of a single wedge fill from 0, fill from the NEW scenario line upward.
    # Group emissions data by the plotting name for each scenario:
    base_by_category = emissions_base.groupby(plotting_name_column_name)[year_cols].sum()
    new_by_category = emissions_new.groupby(plotting_name_column_name)[year_cols].sum()

    # Calculate difference in energy use for each plotting name.
    # For plotting names containing ccus/ccs/captured emissions we want to treat them differently.
    
    ccus_keywords = ['carbon capture', 'captured_emissions']
    ccus_plotting_names = [
        plotting_name for plotting_name in unique_plotting_names
        if any(keyword in plotting_name.lower() for keyword in ccus_keywords)
    ]
    # breakpoint()#check order o f legend
    # breakpoint()#where is power here? how can we add the effects of ccs
    #set those in ccus plotting names to -100 and see how it changes hte graph
    # for plotting_name in ccus_plotting_names:

    #     emissions_new.loc[emissions_new[plotting_name_column_name] == plotting_name, year_cols] = -100
    # Create an empty DataFrame to hold differences.
    diff_df = pd.DataFrame()    
    # breakpoint()#TESTING
    for plotting_name in unique_plotting_names:
        # Process only if the plotting name exists in base; and skip ccus here so we can handle them specially.
        if plotting_name in base_by_category.index and plotting_name not in ccus_plotting_names:
            base_vals = base_by_category.loc[plotting_name]
            if plotting_name not in new_by_category.index:
                raise ValueError(f"Plotting name {plotting_name} not found in {NEW_SCENARIO} scenario")
            new_vals = new_by_category.loc[plotting_name]
            diff_series = base_vals - new_vals
            diff_df = pd.concat([diff_df, diff_series], axis=1)
        elif plotting_name in ccus_plotting_names:
            if plotting_name in base_by_category.index:
                base_vals = base_by_category.loc[plotting_name]
            else:
                base_vals = 0
            if plotting_name not in new_by_category.index:
                raise ValueError(f"Plotting name {plotting_name} not found in {NEW_SCENARIO} scenario")
            new_vals = new_by_category.loc[plotting_name]
            diff_series = base_vals - new_vals
            diff_df = pd.concat([diff_df, diff_series], axis=1)
        else:
            #Plotting name {plotting_name} not found in REF and is not related to carbon caputre.")
            base_vals = 0
            new_vals = new_by_category.loc[plotting_name]
            diff_series = base_vals - new_vals
            diff_df = pd.concat([diff_df, diff_series], axis=1)
    #check emissions wedge for ccus
    # breakpoint()
    #make sure that for all ears, the sum of diffs is equal to the difference in total emissionsbetween the two scenarios
    diff_df['wedge'] = diff_df.sum(axis=1)
    diff_df['line_diff'] = total_base - total_new
    
    if not np.allclose(diff_df['wedge'], diff_df['line_diff'], rtol=1e-2):
        breakpoint()
        # raise ValueError(f"Sum of differences in emissions does not match total difference between scenarios")
    
    #if the line_diff is ever negative then we cannot use a wedge chart and will have to do a stacked bar chart showing the difference.
    if (diff_df['line_diff'] < 0).any():

        BAR_CHART=True
    else:
        BAR_CHART=False
    
    #drop the line_diff and wedge cols
    diff_df = diff_df.drop(columns=['wedge', 'line_diff'])
    
    # Ensure the columns are in the desired order (using unique_plotting_names order)
    diff_df = diff_df.reindex(columns=unique_plotting_names, fill_value=0)
    

    # if BAR_CHART:    
    #     breakpoint()#how to extract the economy from df so we can identify if phl is the current one. want to figure out how to clean up the wedge charts for phl
    #     # file_path = plot_emissions_stacked_bar(
    #     #     year_cols, total_base, total_new, unique_plotting_names, ccus_plotting_names,
    #     #     plotting_name_column_name, plotting_name_to_label_dict, colours_dict, OUTLOOK_BASE_YEAR,
    #     #     plotting_specifications, base_scenario, NEW_SCENARIO, diff_df, original_table_id)
    #     return charts_to_plot, chart_positions, worksheet, current_row, colours_dict
    # breakpoint()#wats going wrong with fuels. not showing ccus
    # else:
    # breakpoint()#check order o f legend
    file_path = plot_emissions_wedge(
            year_cols, total_base, total_new, unique_plotting_names, ccus_plotting_names, plotting_name_column_name, plotting_name_to_label_dict, colours_dict, OUTLOOK_BASE_YEAR, plotting_specifications, base_scenario, NEW_SCENARIO, diff_df,original_table_id)

    #create plotting_name_to_chart_type
    plotting_name_to_chart_type = {}
    plotting_name_to_chart_type[base_scenario] = 'line'
    plotting_name_to_chart_type[NEW_SCENARIO] = 'line'
    
    for plotting_name in unique_plotting_names:
        if plotting_name in diff_df.columns:
            #if need be rename the plotting name in diff_df:
            if plotting_name in diff_df.columns:
                diff_df.rename(columns={plotting_name: plotting_name_to_label_dict.get(plotting_name, plotting_name)}, inplace=True)
            #then set it in plotting_name_to_chart_type
            plotting_name = plotting_name_to_label_dict.get(plotting_name, plotting_name)
            plotting_name_to_chart_type[plotting_name] = 'area' 
            
    # breakpoint()#do we need to adjust the plotting names in diff df?
    ############################################
    # Prepare to format the worksheet with the new chart
    ############################################
    
    if charts_to_plot==None and chart_positions==None:
        breakpoint()
        raise ValueError(f"INSERT_TABLE is True. This function is not designed to insert a table yet..")
        # Update the base dataframe to reflect that this chart shows a wedge comparison
        # emissions_base.loc[:, 'chart_title'] = f"Wedge: {NEW_SCENARIO} vs {base_scenario}"
        # emissions_base.loc[:, 'scenario'] = f"{base_scenario} & {NEW_SCENARIO}"
        #replace the emissions data with the diff data. note that diff data needs to be transposed and had the year cols added
        # diff_df['year'] = year_cols #?
        # diff_df_t = diff_df.T.reset_index()
        # #make year cols the columns
        # # diff_df_t.columns = diff_df_t.loc[0]
        # # diff_df_t = diff_df_t.drop(0, axis=0)
        # diff_df_t = diff_df_t.rename(columns={'index': plotting_name_column_name})
        # diff_df_t = diff_df_t.melt(id_vars=[plotting_name_column_name], value_vars=year_cols, var_name='year', value_name='value').copy()
        # max_and_min_values_dict_net_imports = {}
        # unit_dict = {}
        # total_plotting_names = emissions_base[plotting_name_column_name].unique().tolist()
        
        # #rename plotting_name_column to 'plotting_name'
        # emissions_base.rename(columns={plotting_name_column_name:'plotting_name'}, inplace=True)
        # # Call the common formatting function (same as in your original function)
        # breakpoint()
        #     charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(
        #     emissions_base,
        #     plotting_names_order,
        #     plotting_name_to_label_dict,
        #     scenario_num,
        #     scenarios_list,
        #     header_format,
        #     worksheet,
        #     workbook,
        #     plotting_specifications,
        #     writer,
        #     sheet,
        #     colours_dict,
        #     patterns_dict,
        #     cell_format1,
        #     cell_format2,
        #     max_and_min_values_dict_net_imports,
        #     total_plotting_names,
        #     chart_types,
        #     ECONOMY_ID,
        #     unit_dict,
        #     current_scenario,
        #     current_row,
        #     original_table_id,
        #     NEW_SCENARIO,
        #     PLOTTING_SEABORN=True
        # )
        # worksheet.insert_image(chart_positions[0], file_path)
    
    elif chart_positions != None:
        
        plotting_name_column = 'plotting_name'
        year_cols = [year for year in range(MIN_YEAR, OUTLOOK_LAST_YEAR + 1)]
        #add the base_scenario and NEW_SCENARIO lines to the diff df
        # breakpoint()
        diff_df[base_scenario] = total_base.values
        diff_df[NEW_SCENARIO] = total_new.values
        
        diff_df_transposed = diff_df.T.reset_index()
        diff_df_transposed.columns = [plotting_name_column] + year_cols
        # breakpoint()
        #drop net emissions from te table
        
        #add about 10 rows to chart_postiions so it doesnt directly overlap with the ones below it. CHart opsitions will have something like B4 in it. # Assuming chart_positions[0] is like 'B4'
        new_chart_pos = f"{chart_positions[0][0]}{int(chart_positions[0][1:]) + 10}"
        new_chart_pos_in_list = [new_chart_pos]
        
        diff_df_transposed = diff_df_transposed.loc[diff_df_transposed[plotting_name_column]!='Net emissions']
        # breakpoint()#whats goin on with patterns
        # breakpoint()#check the plotting names
        # breakpoint()#check order o f legend
        
        worksheet = create_legend.create_legend(colours_dict, patterns_dict, plotting_name_column, diff_df_transposed, plotting_specifications, new_chart_pos_in_list, worksheet, ECONOMY_ID, total_plotting_names, chart_types, plotting_name_to_chart_type=plotting_name_to_chart_type)
        # breakpoint()
        # Insert the saved image into the worksheet in the second place returned by format_sheet_for_other_graphs
        worksheet.insert_image(new_chart_pos, file_path)
        # Insert the smaller image into the worksheet in the same place returned by format_sheet_for_other_graphs
        worksheet.insert_image(new_chart_pos, file_path.replace('.png', '_small.png'))
    else:
        raise ValueError(f"charts_to_plot and chart_positions are not both None. This function is not designed for this yet..")
        
    return charts_to_plot, chart_positions, worksheet, current_row, colours_dict

def plot_emissions_wedge(
    year_cols, total_base, total_new, unique_plotting_names, ccus_plotting_names, plotting_name_column_name, plotting_name_to_label_dict, colours_dict, OUTLOOK_BASE_YEAR, plotting_specifications, base_scenario, NEW_SCENARIO, diff_df,original_table_id):
    
    ##############
    #START PLOTTING
    ##############
    # breakpoint()#waht happens to emissions caputre in these charts?
    # Plotting parameters
    # Plotting parameters
    LINE_WIDTH = 2
    FONTSIZE = 10

    # Create the plot with Seaborn styling
    fig, ax = plt.subplots(figsize=(10, 6))

    # Retrieve colors (or fallback to default colors)
    color_base = colours_dict.get(base_scenario, 'steelblue')
    color_new = colours_dict.get(NEW_SCENARIO, 'orange')

    # Plot total emissions curves using Seaborn lineplot for consistency with Excel styling
    # Give them a higher zorder so the lines appear on top
    sns.lineplot(x=year_cols, y=total_base.values, ax=ax, color=color_base,
                label=base_scenario, linewidth=LINE_WIDTH, zorder=3)
    sns.lineplot(x=year_cols, y=total_new.values, ax=ax, color=color_new,
                label=NEW_SCENARIO, linewidth=LINE_WIDTH, zorder=3)

    # --- 1) Fill under the NEW scenario line with fully transparent white ---
    #     This hides anything visually below that line (but remains transparent).
    ax.fill_between(
        year_cols,
        0,                      # from 0
        total_new.values,       # up to the new scenario line
        color='white',
        alpha=0,                # fully transparent
        zorder=1
    )

    # --- Now, build the wedge fill starting at the NEW scenario line.
    # We set a cumulative line starting from total_new.
    cumulative_line = total_new.copy()
    unique_plotting_names_rev = unique_plotting_names
    unique_plotting_names_rev.reverse()
    # Loop over each plotting name (in the desired order) and fill the wedge.
    for plotting_name in unique_plotting_names_rev:
        if plotting_name in diff_df.columns:
            diff_series = diff_df[plotting_name]
            y1 = cumulative_line
            y2 = cumulative_line + diff_series
            
            #if it sone of the ccus ones then use a stripey pattern on the fill as well
            if plotting_name in ccus_plotting_names:
                #we can probably assume the ccus is in the tgt scneario so we can just make it add to the cumulative effect. 
                # if plotting_name =='Gas_captured_emissions' or plotting_name == 'Coal_captured_emissions':
                #     breakpoint()#color is weird for fuels
                ax.fill_between(
                    year_cols,
                    y1,
                    y2,
                    facecolor='none',
                    edgecolor=colours_dict.get(plotting_name, 'gray'),     # color of the hatch lines
                    hatch='\\\\',            # your dot pattern
                    linewidth=0.0,         # no extra border
                    label=plotting_name_to_label_dict.get(plotting_name, plotting_name),
                    zorder=2
                )
                
            else:
                ax.fill_between(
                    year_cols,
                    y1,
                    y2,
                    color=colours_dict.get(plotting_name, 'gray'),
                    alpha=1,  # 100% opaque
                    label=plotting_name_to_label_dict.get(plotting_name, plotting_name),
                    zorder=2
                )
            cumulative_line += diff_series

    # Common formatting: horizontal baseline and vertical marker at OUTLOOK_BASE_YEAR
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(OUTLOOK_BASE_YEAR, color='black', linewidth=1, linestyle='--')
    ax.tick_params(axis='both', which='major', labelsize=FONTSIZE)
    ax.set_title(f'Change in gross co2 emissions by {plotting_name_column_name} (million tonnes)', fontsize=FONTSIZE, fontname='Calibri', pad=20)
    # ax.legend(loc='center left', bbox_to_anchor=(1.2, 0.5), fontsize=FONTSIZE)
    ax.grid(visible=False, which='major', axis='x')  #
    ax.grid(visible=True, which='major', axis='y')  # only horizontal gridlines
    ax.set_axisbelow(True)
    ax.set_xlim(min(year_cols), max(year_cols))

    # Remove chart borders for a clean, Excel-like look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Adjust the figure size (enlarged width to allow space for the legend)
    fig.set_size_inches(plotting_specifications['width_inches'],
                        plotting_specifications['height_inches'])

    
    # Determine file path and save the chart
    if 'code' in os.getcwd():
        file_path = f'../intermediate_data/charts/{original_table_id}_wedge.png'
    else:
        file_path = f'intermediate_data/charts/{original_table_id}_wedge.png'

    #remove the legend
    legend = ax.get_legend()
    if legend:
        legend.remove()
    # breakpoint()#check the wedges
    plt.savefig(file_path, dpi=300, bbox_inches='tight')   
    ax.set_title('', fontsize=0, fontname='Calibri', pad=0) 
    # for label in ax.get_xticklabels() + ax.get_yticklabels():
    #     label.set_fontsize(FONTSIZE/2)
        
    fig.set_size_inches(plotting_specifications['bar_width_inches'], plotting_specifications['bar_height_inches'])
    # Save the figure with tight bounding box
    plt.savefig(file_path.replace('.png', '_small.png'), dpi=300, bbox_inches='tight')
    
    plt.close(fig)
    plt.clf()
    plt.close('all')
    #double check the order of plotting naems:
    return file_path

# def plot_emissions_stacked_bar(
#     year_cols, total_base, total_new, unique_plotting_names, ccus_plotting_names,
#     plotting_name_column_name, plotting_name_to_label_dict, colours_dict, OUTLOOK_BASE_YEAR,
#     plotting_specifications, base_scenario, NEW_SCENARIO, diff_df, original_table_id):

#     import matplotlib.pyplot as plt
#     import os
#     import numpy as np

#     # Plotting parameters
#     FONTSIZE = 10
#     BAR_WIDTH = 1  # Adjust as needed depending on your x-values

#     # Create the plot
#     fig, ax = plt.subplots(figsize=(10, 6))

#     # Create an initial baseline of zeros (one for each year)
#     cumulative = np.zeros(len(year_cols))
#     diff_df['year'] = year_cols

#     # Filter for only every 5-year (plus 2022) and remove 2020
#     filtered_years = [year for year in year_cols if (year % 5 == 0 or year == 2022)]
#     if 2020 in filtered_years:
#         filtered_years.remove(2020)
#     diff_df = diff_df[diff_df['year'].isin(filtered_years)]
#     # Reset cumulative to match the filtered data length
#     cumulative = np.zeros(len(filtered_years))

#     # Loop over each plotting name and stack the diff_df values.
#     for plotting_name in unique_plotting_names:
#         if plotting_name in diff_df.columns:
#             diff_series = diff_df[plotting_name]
#             common_bar_kwargs = {
#                 'width': BAR_WIDTH,
#                 'bottom': cumulative,
#                 'align': 'edge',
#                 'zorder': 2,
#                 'linewidth': 0,         # eliminate border width
#                 'edgecolor': 'none',    # no edge color to remove borders
#                 'antialiased': False    # disable anti-aliasing
#             }
#             if plotting_name in ccus_plotting_names:
#                 ax.bar(
#                     filtered_years,
#                     diff_series,
#                     color=colours_dict.get(plotting_name, 'gray'),
#                     label=plotting_name_to_label_dict.get(plotting_name, plotting_name),
#                     hatch='..',
#                     **common_bar_kwargs
#                 )
#             else:
#                 ax.bar(
#                     filtered_years,
#                     diff_series,
#                     color=colours_dict.get(plotting_name, 'gray'),
#                     label=plotting_name_to_label_dict.get(plotting_name, plotting_name),
#                     **common_bar_kwargs
#                 )
#             # Update the cumulative sum for stacking
#             cumulative += diff_series

#     # Optional reference lines
#     ax.axhline(0, color='black', linewidth=1)
#     ax.axvline(OUTLOOK_BASE_YEAR, color='black', linewidth=1, linestyle='--')

#     # Formatting: set discrete ticks for the x-axis
#     ax.set_xticks(filtered_years)
#     ax.set_xticklabels(filtered_years, fontsize=FONTSIZE)

#     ax.tick_params(axis='both', which='major', labelsize=FONTSIZE)
#     ax.set_title(
#         f'Change in gross CO₂ emissions by {plotting_name_column_name} (million tonnes)',
#         fontsize=FONTSIZE, fontname='Calibri', pad=20
#     )
#     # Remove the legend if you plan to handle it externally.
#     legend = ax.get_legend()
#     if legend:
#         legend.remove()

#     # Set grid lines and axis limits
#     ax.grid(False, which='major', axis='x')
#     ax.grid(True, which='major', axis='y')
#     ax.set_axisbelow(True)
#     ax.set_xlim(min(filtered_years), max(filtered_years))

#     # Remove chart borders for a cleaner look
#     for spine in ['top', 'right', 'bottom', 'left']:
#         ax.spines[spine].set_visible(False)

#     # Adjust figure size based on plotting specifications.
#     fig.set_size_inches(
#         plotting_specifications['width_inches'],
#         plotting_specifications['height_inches']
#     )

#     # Determine file path and save the chart
#     if 'code' in os.getcwd():
#         file_path = f'../intermediate_data/charts/{original_table_id}_stacked_bar.png'
#     else:
#         file_path = f'intermediate_data/charts/{original_table_id}_stacked_bar.png'
    
#     plt.savefig(file_path, dpi=300, bbox_inches='tight')
    
#     # Optionally, adjust for a smaller version
#     ax.set_title('', fontsize=0, fontname='Calibri', pad=0)
#     fig.set_size_inches(
#         plotting_specifications['bar_width_inches'],
#         plotting_specifications['bar_height_inches']
#     )
#     plt.savefig(file_path.replace('.png', '_small.png'), dpi=300, bbox_inches='tight')

#     # Cleanup: close figures to free memory
#     plt.close(fig)
#     plt.clf()
#     plt.close('all')

#     return file_path



# def plot_emissions_stacked_bar(
#     year_cols, total_base, total_new, unique_plotting_names, ccus_plotting_names,
#     plotting_name_column_name, plotting_name_to_label_dict, colours_dict, OUTLOOK_BASE_YEAR,
#     plotting_specifications, base_scenario, NEW_SCENARIO, diff_df, original_table_id):
#  # Plotting parameters
#     LINE_WIDTH = 1.5
#     FONTSIZE = 10
#     BAR_WIDTH = 1  # Set bar width explicitly

#     # Create the plot with Seaborn styling
#     fig, ax = plt.subplots(figsize=(10, 6))

#     # Retrieve colors (or fallback to default colors)
#     color_base = colours_dict.get(base_scenario, 'steelblue')
#     color_new = colours_dict.get(NEW_SCENARIO, 'orange')

#     # Plot total emissions curves using Seaborn lineplot for context.
#     sns.lineplot(x=year_cols, y=total_base.values, ax=ax, color=color_base,
#                  label=base_scenario, linewidth=LINE_WIDTH, zorder=3)
#     sns.lineplot(x=year_cols, y=total_new.values, ax=ax, color=color_new,
#                  label=NEW_SCENARIO, linewidth=LINE_WIDTH, zorder=3)

#     # Begin stacked bar chart plotting.
#     # We start stacking from the NEW scenario totals.
#     cumulative_line = total_new.copy()

#     # Loop over each plotting name and add a bar segment for each category.
#     for plotting_name in unique_plotting_names:
#         if plotting_name in diff_df.columns:
#             diff_series = diff_df[plotting_name]
#             # Draw a bar for each year. The bar's bottom is the current cumulative_line,
#             # and its height is the diff_series for that category.
#             if plotting_name in ccus_plotting_names:
#                 # If the category requires a hatch pattern, include it.
#                 ax.bar(year_cols, diff_series, bottom=cumulative_line,
#                        width=BAR_WIDTH,
#                        color=colours_dict.get(plotting_name, 'gray'),
#                        label=plotting_name_to_label_dict.get(plotting_name, plotting_name),
#                        hatch='..', zorder=2,
#                        edgecolor=None)  # Remove edge to avoid visible gaps
#             else:
#                 ax.bar(year_cols, diff_series, bottom=cumulative_line,
#                        width=BAR_WIDTH,
#                        color=colours_dict.get(plotting_name, 'gray'),
#                        label=plotting_name_to_label_dict.get(plotting_name, plotting_name),
#                        zorder=2,
#                        edgecolor=None)  # Remove edge to avoid visible gaps
#             # Update cumulative_line so that the next bar stacks on top.
#             cumulative_line += diff_series

#     # Add formatting elements:
#     ax.axhline(0, color='black', linewidth=1)
#     ax.axvline(OUTLOOK_BASE_YEAR, color='black', linewidth=1, linestyle='--')
#     ax.tick_params(axis='both', which='major', labelsize=FONTSIZE)
#     ax.set_title(f'Change in gross CO₂ emissions by {plotting_name_column_name} (million tonnes)',
#                  fontsize=FONTSIZE, fontname='Calibri', pad=20)
    
#     # Optionally, remove the legend if handling externally.
#     legend = ax.get_legend()
#     if legend:
#         legend.remove()
    
#     # Set grid lines
#     ax.grid(visible=False, which='major', axis='x')
#     ax.grid(visible=True, which='major', axis='y')
#     ax.set_axisbelow(True)
#     ax.set_xlim(min(year_cols), max(year_cols))

#     # Remove chart borders for a cleaner appearance
#     for spine in ['top', 'right', 'bottom', 'left']:
#         ax.spines[spine].set_visible(False)

#     # Adjust figure size based on plotting specifications.
#     fig.set_size_inches(plotting_specifications['width_inches'],
#                         plotting_specifications['height_inches'])

#     # Determine file path and save the chart
#     if 'code' in os.getcwd():
#         file_path = f'../intermediate_data/charts/{original_table_id}_stacked_bar.png'
#     else:
#         file_path = f'intermediate_data/charts/{original_table_id}_stacked_bar.png'
    
#     # Save the figure with a tight bounding box
#     plt.savefig(file_path, dpi=300, bbox_inches='tight')
#     breakpoint()
#     # Optionally, adjust for a smaller version
#     ax.set_title('', fontsize=0, fontname='Calibri', pad=0)
#     fig.set_size_inches(plotting_specifications['bar_width_inches'],
#                         plotting_specifications['bar_height_inches'])
#     plt.savefig(file_path.replace('.png', '_small.png'), dpi=300, bbox_inches='tight')

#     # Cleanup: close figures to free memory
#     plt.close(fig)
#     plt.clf()
#     plt.close('all')

#     return file_path
    # # Plotting parameters
    # LINE_WIDTH = 1.5
    # FONTSIZE = 10

    # # Create the plot with Seaborn styling
    # fig, ax = plt.subplots(figsize=(10, 6))

    # # Retrieve colors (or fallback to default colors)
    # color_base = colours_dict.get(base_scenario, 'steelblue')
    # color_new = colours_dict.get(NEW_SCENARIO, 'orange')

    # # Plot total emissions curves using Seaborn lineplot for context
    # # These lines help the viewer compare the overall trends.
    # sns.lineplot(x=year_cols, y=total_base.values, ax=ax, color=color_base,
    #              label=base_scenario, linewidth=LINE_WIDTH, zorder=3)
    # sns.lineplot(x=year_cols, y=total_new.values, ax=ax, color=color_new,
    #              label=NEW_SCENARIO, linewidth=LINE_WIDTH, zorder=3)

    # # Begin stacked bar chart plotting.
    # # We start stacking from the NEW scenario totals.
    # cumulative_line = total_new.copy()

    # # Loop over each plotting name and add a bar segment for each category.
    # for plotting_name in unique_plotting_names:
    #     if plotting_name in diff_df.columns:
    #         diff_series = diff_df[plotting_name]
    #         # Draw a bar for each year. The bar's bottom is the current cumulative_line,
    #         # and its height is the diff_series for that category.
    #         if plotting_name in ccus_plotting_names:
    #             # If the category requires a hatch pattern, include it.
    #             ax.bar(year_cols, diff_series, bottom=cumulative_line,
    #                    color=colours_dict.get(plotting_name, 'gray'),
    #                    label=plotting_name_to_label_dict.get(plotting_name, plotting_name),
    #                    hatch='..', zorder=2)
    #         else:
    #             ax.bar(year_cols, diff_series, bottom=cumulative_line,
    #                    color=colours_dict.get(plotting_name, 'gray'),
    #                    label=plotting_name_to_label_dict.get(plotting_name, plotting_name),
    #                    zorder=2)
    #         # Update cumulative_line so that the next bar stacks on top.
    #         cumulative_line += diff_series

    # # Add formatting elements:
    # # Horizontal line at y=0
    # ax.axhline(0, color='black', linewidth=1)
    # # Vertical marker at the outlook base year
    # ax.axvline(OUTLOOK_BASE_YEAR, color='black', linewidth=1, linestyle='--')
    # ax.tick_params(axis='both', which='major', labelsize=FONTSIZE)
    # ax.set_title(f'Change in gross CO₂ emissions by {plotting_name_column_name} (million tonnes)',
    #              fontsize=FONTSIZE, fontname='Calibri', pad=20)
    # # Optionally, you can remove the legend if you plan to handle it externally.
    # legend = ax.get_legend()
    # if legend:
    #     legend.remove()
    # # Set grid lines
    # ax.grid(visible=False, which='major', axis='x')
    # ax.grid(visible=True, which='major', axis='y')
    # ax.set_axisbelow(True)
    # ax.set_xlim(min(year_cols), max(year_cols))

    # # Remove chart borders for a cleaner, Excel-like appearance
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    # ax.spines['left'].set_visible(False)

    # # Adjust figure size based on plotting specifications.
    # fig.set_size_inches(plotting_specifications['width_inches'],
    #                     plotting_specifications['height_inches'])

    # # Determine file path and save the chart
    # if 'code' in os.getcwd():
    #     file_path = f'../intermediate_data/charts/{original_table_id}_stacked_bar.png'
    # else:
    #     file_path = f'intermediate_data/charts/{original_table_id}_stacked_bar.png'
    # breakpoint()
    # # Save the figure with a tight bounding box
    # plt.savefig(file_path, dpi=300, bbox_inches='tight')
    # # Optionally, clear the title or adjust for a smaller version
    # ax.set_title('', fontsize=0, fontname='Calibri', pad=0)
    # fig.set_size_inches(plotting_specifications['bar_width_inches'],
    #                     plotting_specifications['bar_height_inches'])
    # plt.savefig(file_path.replace('.png', '_small.png'), dpi=300, bbox_inches='tight')

    # # Cleanup: close figures to free memory
    # plt.close(fig)
    # plt.clf()
    # plt.close('all')

    # return file_path

def create_double_axis_crude_supply_and_refining_capacity(charts_mapping, sheet,
                           plotting_names_order,
                           plotting_name_to_label_dict,
                           worksheet, workbook,
                           colours_dict, patterns_dict,
                           cell_format1, cell_format2,
                           scenario_num, scenarios_list,
                           header_format, plotting_specifications,
                           writer, chart_types, ECONOMY_ID,
                           current_scenario, current_row,
                           original_table_id, NEW_SCENARIO, charts_to_plot=None, chart_positions=None):
    """
    Creates a wedge chart showing the difference between two emissions scenarios.
    Uses similar parameters and helper functions as create_emissions_seaborn.
    Even though it runs at the end of create_emissions_seaborn, it is designed to run just like it, even if that means redoing some of the same work.
    """
    # Set Seaborn theme to emulate Excel styling with Calibri font
    sns.set_theme(style="whitegrid", font="Calibri", context="notebook")
    breakpoint()#can we keep only the crude and ignore the gas liquids?
    #extract the tables for crude oil supply and refining capacity
    table_id = 'energy_Refining_5'
    table_id2 = 'capacity_Total refining capacity_1'
    title = 'Crude oil supply and refining capacity'
    crude = charts_mapping[(charts_mapping.table_id == table_id) &
                                    (charts_mapping['scenario'] == current_scenario)].copy()
    refining_cap = charts_mapping[(charts_mapping.table_id == table_id2) &
                                   (charts_mapping['scenario'] == current_scenario)].copy()

    if crude.empty or refining_cap.empty:
        breakpoint()
        return None, None, worksheet, current_row, colours_dict #since we need refining cap data for this we sometimes need to return None
        # raise Exception(f'No data found for table {table_id} for one or both scenarios')
    
    # Add common meta-data for each (using base for formatting later)
    for df in [crude, refining_cap]:
        df.loc[:, 'chart_title'] = title
        df.loc[:, 'sheet_name'] = sheet
        df.loc[:, 'table_id'] = original_table_id
        
    #sicne chart type is double_axis_line_bar, we need to set the chart type for each of the two dataframes
    crude.loc[:, 'chart_type'] = 'bar'
    #drop plottingname = total
    crude = crude[crude['plotting_name'] != 'TPES']
    #for crude, keep only the years in plotting_specificaitons bar_years which should be something like:	['2010', '2022', '2030','2040', '2050','2060']
    #make all year cols into strs
    crude.columns = crude.columns.astype(str)
    refining_cap.columns = refining_cap.columns.astype(str)
    years = plotting_specifications['bar_years']
    # Identify the year columns (e.g., 2020, 2021, …) based on a regex match
    year_cols = [col for col in crude.columns if re.search(r'\d{4}', col)]
    year_cols_to_remove = [col for col in year_cols if col not in years]
    if len(year_cols_to_remove) > 0:
        crude.drop(columns=year_cols_to_remove, inplace=True)
        refining_cap.drop(columns=year_cols_to_remove, inplace=True)
    # breakpoint()
    refining_cap.loc[:, 'chart_type'] = 'line'        
    plotting_name_column_name = 'plotting_name'#set this to teh default
    
    unique_plotting_names = list(dict.fromkeys(list(crude.plotting_name.unique()) + list(refining_cap.plotting_name.unique())))
    
    if len(refining_cap.plotting_name.unique()) > 1:
        raise ValueError(f"Expected only one plotting name in refining_cap, found {len(refining_cap.plotting_name.unique())}")
    else:
        refining_plotting_name = refining_cap.plotting_name.unique()[0] 
    
    # To help avoid values that are very small and only increase the range of the graph, 
    # we will remove them if they make up <5% of the total supply in that year:
    total_supply = crude[years].sum(axis=0)
    threshold = 0.05 * total_supply

    for year in years:
        for plotting_name in crude[plotting_name_column_name].unique():
            # Get the value for the current plotting name and year
            value = crude.loc[crude[plotting_name_column_name] == plotting_name, year]
            # Check if the value is less than the threshold for the year
            if not value.empty and abs(value.iloc[0]) < threshold[year]:
                # Set the value to 0 if it is below the threshold
                crude.loc[crude[plotting_name_column_name] == plotting_name, year] = 0
    
        
    breakpoint()
    CONVERT_CAPACITY_TO_PJ_PA = True   
    if CONVERT_CAPACITY_TO_PJ_PA:
        refining_cap[years] = (refining_cap[years] *  2226.5)/1000
    ##############
    # START PLOTTING
    #############
    
    
    # Plotting parameters
    LINE_WIDTH = 3
    FONTSIZE = 10

    # Create the plot with Seaborn styling
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # --- 1) Create a stacked bar chart for crude oil supply ---
    # Pivot the crude DataFrame so that the index is the year and the columns are the plotting names.
    # (Assumes each row in crude corresponds to a unique plotting category.)
    crude_pivot = crude.set_index(plotting_name_column_name)[years].T
    # Determine the desired order for crude categories using the provided plotting_names_order if available.
    crude_categories = list(crude[plotting_name_column_name].unique())
    if table_id in plotting_names_order:
        ordered_categories = plotting_names_order[table_id] + [cat for cat in crude_categories if cat not in plotting_names_order[table_id]]
    else:
        ordered_categories = crude_categories
    # breakpoint()
    # Plot the crude data as a stacked bar chart.\
    # breakpoint()
    cumulative_positive = np.zeros(len(years))
    cumulative_negative = np.zeros(len(years))
    for cat in ordered_categories:
        if cat in crude_pivot.columns:
            values = crude_pivot[cat].values
            # Separate positive and negative values
            positive_values = np.where(values > 0, values, 0)
            negative_values = np.where(values < 0, values, 0)
            
            # Plot positive values
            ax.bar(years, positive_values, bottom=cumulative_positive,
                    label=plotting_name_to_label_dict.get(cat, cat),
                    color=colours_dict.get(cat, None),
                    width=0.8)
            cumulative_positive += positive_values
            
            # Plot negative values
            ax.bar(years, negative_values, bottom=cumulative_negative,
                    label=plotting_name_to_label_dict.get(cat, cat),
                    color=colours_dict.get(cat, None),
                    width=0.8)
            cumulative_negative += negative_values
    # breakpoint()
    # --- 2) Create a line plot for refining capacity on a secondary y-axis ---
    ax2 = ax.twinx()
    # Since refining_cap is expected to be a single row, extract the values for the years.
    refining_vals = refining_cap.iloc[0][years].values
    ax2.plot(years, refining_vals, color=colours_dict.get(refining_plotting_name, 'black'), linewidth=LINE_WIDTH, label=refining_plotting_name)
    
    # --- 3) Formatting ---    
    ax.set_title(title, fontsize=FONTSIZE, fontname='Calibri', pad=20)
    # ax.set_xlabel('Year', fontsize=FONTSIZE)
    ax.set_ylabel('Crude Oil Supply (PJ)', fontsize=FONTSIZE)
    if CONVERT_CAPACITY_TO_PJ_PA:
        ax2.set_ylabel('Refining Capacity (PJ/year)', fontsize=FONTSIZE)
    else:
        ax2.set_ylabel('Refining Capacity (MBd)', fontsize=FONTSIZE)
    # Set x-axis ticks and rotate tick labels if needed
    ax.set_xticks(years)
    # plt.setp(ax.get_xticklabels())#, rotation=45)
    
    # Calculate the max and min values for both axes
    max_crude = crude[crude[years] > 0].sum().max() 
    max_refining = refining_cap[years].max().max()
    min_crude = crude[crude[years] < 0].sum().min()
    min_refining = 0
    breakpoint()#why does korea end up with such a weird scale for refining capcity?
    # Ensure minimum values are not above zero
    if min_crude > 0:
        min_crude = 0
    if min_refining > 0:
        min_refining = 0
    #if there is a min value below the y axis, we should find the portion of that axes max y that is below the y axis and apply that to the max y of the second axes: *note that we can assume it is only min_crude that would be negative sincew refiing acpaity is always postive
    if min_crude < 0:
        portion_below_y_axis = min_crude / max_crude
        min_refining = max_refining * portion_below_y_axis
        
    # --- Adjust positive maximum values so that both axes use the same target ---
    # Calculate the magnitude for each positive maximum. (Avoid division by zero.)
    mag_crude = 10 ** math.floor(math.log10(max_crude)) if max_crude != 0 else 1
    mag_refining = 10 ** math.floor(math.log10(max_refining)) if max_refining != 0 else 1

    #if one is half the other or more, set them to the largest magnitude*
    max_mag = max(mag_crude, mag_refining)
    if max_crude * 2 >= max_refining or max_refining * 2 >= max_crude:
        mag_crude = max_mag 
        mag_refining = max_mag 
    # Normalize the positive maximum values by dividing by their magnitude.
    norm_crude = max_crude / mag_crude
    norm_refining = max_refining / mag_refining

    # Choose the target positive maximum based on the larger normalized value.
    # (This ensures that if one axis has a "rounder" or higher max when adjusted for magnitude,
    #  that value is used for both axes.)
    if norm_crude >= norm_refining:
        max_refining = norm_crude * mag_refining
    else:
        max_crude = norm_refining * mag_crude

    # Set the limits for both axes
    ax.set_ylim(min_crude, max_crude)
    ax2.set_ylim(min_refining, max_refining)
    def calculate_regular_ticks(min_val, max_val, num_ticks):
        """
        Calculate regular tick intervals based on the magnitude of the range.
        Ensures that tick marks are multiples of a power of 10, and that 0 is included
        if it falls within the data range.
        """
        # Calculate the raw range of the data
        raw_range = max_val - min_val
        if raw_range == 0:
            return [min_val]

        # Determine the order of magnitude
        magnitude = 10 ** math.floor(math.log10(raw_range))
        
        # Determine a preliminary tick interval. We want num_ticks intervals, but also a "nice" number.
        tick_interval = magnitude
        # Increase tick interval until the number of ticks is less than or equal to the desired number.
        while True:
            # Adjust the rounded boundaries to be multiples of tick_interval
            rounded_min = tick_interval * math.floor(min_val / tick_interval)
            rounded_max = tick_interval * math.ceil(max_val / tick_interval)
            ticks = np.arange(rounded_min, rounded_max + tick_interval, tick_interval)
            
            # Check if we have too many ticks; if so, increase the interval
            if len(ticks) <= num_ticks:
                break
            tick_interval *= 2  # or adjust by another factor if needed
        
        # If 0 is within the bounds, ensure it is in the tick list. (It should be because of rounding.)
        if rounded_min < 0 < rounded_max and 0 not in ticks:
            ticks = np.sort(np.append(ticks, 0))
        
        # Return the tick list as a Python list
        return ticks.tolist()

    # Generate tick marks for the primary axis (crude supply)
    NUM_TICKS = 10  # Adjust this for more or fewer ticks
    ticks_crude = calculate_regular_ticks(min_crude, max_crude, NUM_TICKS)
    ax.set_yticks(ticks_crude)
    
    # --- Adjust secondary axis limits to align the 0 line with the primary axis ---

    # 1. Compute the fraction f at which 0 appears on the primary axis.
    #    f = (distance from min_crude to 0) / (total range of primary axis)
    f = (0 - min_crude) / (max_crude - min_crude)

    # 2. For the secondary axis, we want 0 to be at the same fraction f between its limits.
    #    Let new_min_refining be the new lower limit while keeping max_refining unchanged.
    #    The equation is:
    #         (0 - new_min_refining) / (max_refining - new_min_refining) = f
    #    Solving for new_min_refining gives:
    new_min_refining = - (f * max_refining) / (1 - f)

    # 3. Set the new limits for the secondary axis.
    ax2.set_ylim(new_min_refining, max_refining)

    # 4. Generate tick marks for the secondary axis using your custom tick function.
    ticks_refining = calculate_regular_ticks(new_min_refining, max_refining, NUM_TICKS)

    # 5. Force inclusion of 0 in the tick list if it isn’t already there.
    if 0 not in ticks_refining:
        ticks_refining = np.sort(np.append(ticks_refining, 0))
        
    ax2.set_yticks(ticks_refining)
    # # Generate tick marks for the secondary axis (refining capacity)
    # num_ticks_refining = 6  # Adjust this for more or fewer ticks
    # ticks_refining = calculate_regular_ticks(min_refining, max_refining, num_ticks_refining)
    # ax2.set_yticks(ticks_refining)
    # # Combine legends from both axes so that both crude categories and refining capacity appear
    # handles1, labels1 = ax.get_legend_handles_labels()
    # handles2, labels2 = ax2.get_legend_handles_labels()
    #drop duplicates in handles 1 and labels 1
    # new_labels1 = []
    # handles1_to_remove = []
    # for l in labels1:
    #     if l not in new_labels1:
    #         new_labels1.append(l)
    #     else:
    #         handles1_to_remove.append(handles1[labels1.index(l)])
    # for h in handles1_to_remove:
    #     handles1.remove(h)
    # ax.legend(handles1 + handles2, new_labels1 + labels2,
    #           loc='center left', bbox_to_anchor=(1.4, 0.5), fontsize=FONTSIZE)
    
    #only show grid lines for x axis
    
    ax.grid(visible=False, which='major', axis='x')  #
    ax.grid(visible=True, which='major', axis='y')  # only horizontal gridlines
    
    ax2.grid(visible=False, which='major', axis='x')  #
    ax2.grid(visible=True, which='major', axis='y')  # only horizontal gridlines
    # ax.grid(axis='y', color='lightgray', linestyle='-', linewidth=0.5, zorder=0)
    # ax2.grid(axis='y', color='lightgray', linestyle='-', linewidth=0.5, zorder=0) ##this doesnt seem to get the grid lines behind the bars. i dont know how to fix this
    # #drop grid lines for x axis
    # ax2.xaxis.grid(False)
    # ax.xaxis.grid(False)
    #remove the lines around the border of the chart
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    
    # Adjust the figure size based on plotting specifications (optionally applying a width multiplier)
    fig.set_size_inches(plotting_specifications['width_inches'],
                        plotting_specifications['height_inches'])
    
    # --- 4) Save and insert the chart ---
    unique_id = uuid.uuid4()
    if 'code' in os.getcwd():
        file_path = f'../intermediate_data/charts/{original_table_id}_double_axis_{unique_id}.png'
        file_path_temp = f'../intermediate_data/temp/{original_table_id}_double_axis_{unique_id}.png'
    else:
        file_path = f'intermediate_data/charts/{original_table_id}_double_axis_{unique_id}.png'
        file_path_temp = f'../intermediate_data/temp/{original_table_id}_double_axis_{unique_id}.png'

    plt.savefig(file_path, dpi=300, bbox_inches='tight')   
    breakpoint()#get this one working right.. its not!
    #remove the legend and create a very small one
    # legend = ax.get_legend()
    # if legend:
    #     legend.remove()
    ax.set_title('', fontsize=0, fontname='Calibri', pad=0) 
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(FONTSIZE/1.5)
    for label in ax2.get_xticklabels() + ax2.get_yticklabels():
        label.set_fontsize(FONTSIZE/1.5)
    #make x axis labels rotate 180
    for label in ax.get_xticklabels():
        label.set_rotation(90)
        
    #also if scenario is reference, drop the second y axis labels, and if scenario is target, drop the frist y axis labels
    # breakpoint()#why does it resut in same one being lost in both scenarios
    if current_scenario == 'reference':
        # ax2.set_yticks([])
        ax2.set_ylabel('')
        # ax2.spines['right'].set_visible(False)
        # ax2.set_visible(False)  # Completely disables the twin axis
        # ax.set_visible(True)  
    elif current_scenario == 'target':
        # ax.set_yticks([])
        ax.set_ylabel('')
        # ax.spines['left'].set_visible(False)
        # ax2.set_visible(True)  # Completely disables the twin axis
        # ax.set_visible(False)  
    fig.set_size_inches(plotting_specifications['bar_width_inches']/2, plotting_specifications['bar_height_inches'])
    # Save the figure with tight bounding box
    
    plt.savefig(file_path.replace('.png', '_small.png'), dpi=300, bbox_inches='tight')
    #also save it to a folder where i can look at them all
    SAVE_TO_TEMP_FOLDER = True
    if SAVE_TO_TEMP_FOLDER:
        breakpoint()#want to test how i can change the axis to remove ticks as well
        plt.savefig(file_path_temp, dpi=300, bbox_inches='tight')   
    plt.close(fig)
    plt.clf()
    plt.close('all')
    #clear axes too
    ax.clear()
    ax2.clear()
    
    #create chart_type_to_label for the creation of legend, so we can have different label types based on chart type:
    plotting_name_to_chart_type = {
        refining_plotting_name: 'line',
    }
    for cat in ordered_categories:
        plotting_name_to_chart_type[cat] = 'bar'
        
    ############################################
    #Extract chart positions and add to worksheet
    ############################################
    
    # # Default values for variables
    # plotting_names_order[original_table_id] = emissions[;plotting_name].unique().tolist()#dont think im needed
    # plotting_name_to_label_dict = {plotting_name: plotting_name for plotting_name in plotting_names_order}#dont think im needed
    max_and_min_values_dict_net_imports = {}
    unit_dict = {}
    
    #concat refining_cap and crude to get the plotting names in the right order
    crude_and_refining_cap = pd.concat([crude, refining_cap], axis=0)
    
    charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(
        crude_and_refining_cap,
        plotting_names_order,
        plotting_name_to_label_dict,
        scenario_num,
        scenarios_list,
        header_format,
        worksheet,
        workbook,
        plotting_specifications,
        writer,
        sheet,
        colours_dict,
        patterns_dict,
        cell_format1,
        cell_format2,
        max_and_min_values_dict_net_imports,
        total_plotting_names,
        chart_types,
        ECONOMY_ID,
        unit_dict,
        current_scenario,
        current_row,
        original_table_id,
        NEW_SCENARIO,
        PLOTTING_SEABORN=True,
        plotting_name_to_chart_type=plotting_name_to_chart_type
    )
    
    # Add the image to the worksheet.. but first work out where to put it:
    worksheet.insert_image(chart_positions[0], file_path)

    # Insert the smaller image into the worksheet in the same place returned by format_sheet_for_other_graphs
    worksheet.insert_image(chart_positions[0], file_path.replace('.png', '_small.png'))
    
    return charts_to_plot, chart_positions, worksheet, current_row, colours_dict

def create_coal_and_biomass_supply_charts(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row,original_table_id, NEW_SCENARIO):
    """    
    # Add the new chart creation function to the new_charts_dict
    new_charts_dict = {
        'Natural gas, LNG and biogas supply': {
        'source': 'energy',
        'sheet_name': 'natural_gas_and_lng_supply',
        'function': workbook_creation_functions.create_natural_gas_and_lng_supply_charts,
        'chart_type': 'bar'    
    }

    }
    
    energy	Refining and other transformation	Refining	5	line	sectors_plotting	Refining_output	Other petroleum products	Jet fuel	Ethane	Refinery gas not liquefied	LPG	Fuel oil	Diesel	Kerosene	Naphtha	Aviation gasoline	Gasoline
    """
    final_table = pd.DataFrame()
    for chart_type in chart_types:
        #extract the data we want to use for the refined products graph, then do wahtever manipulations and calculations are needed to get it into the right format, then plotit
        table_id = 'energy_Coal_3'
        coal = charts_mapping[(charts_mapping.table_id == table_id)]
        if len(coal) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        coal.loc[:, 'chart_title'] = 'Figure 9-29. Coal and biomass supply'
        coal.loc[:, 'table_id'] = original_table_id
        coal.loc[:, 'aggregate_name'] = 'Coal'
        coal.loc[:, 'sheet_name'] = sheet
        
        coal.loc[:, 'chart_type'] = chart_type
        coal.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
        coal = coal[~coal.plotting_name.isin(['Stock change', 'TPES', 'Bunkers'])]
        ######Figure 9-29. 
        table_id = 'energy_Bioenergy_6'
        bioenergy_supply = charts_mapping[(charts_mapping.table_id == table_id)]
        if len(bioenergy_supply) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        bioenergy_supply.loc[:, 'chart_title'] = 'Figure 9-29. Coal and biomass supply'
        bioenergy_supply.loc[:, 'table_id'] = original_table_id
        bioenergy_supply.loc[:, 'aggregate_name'] = 'Biomass'
        bioenergy_supply.loc[:, 'sheet_name'] = sheet
        
        bioenergy_supply.loc[:, 'chart_type'] = chart_type
        bioenergy_supply.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
        bioenergy_supply = bioenergy_supply[bioenergy_supply.plotting_name!='TPES']
        ##################
        #add '- NAME' to the plotting names for the data
        coal.loc[:, 'plotting_name'] = coal['plotting_name'] + ' - Coal'
        bioenergy_supply.loc[:, 'plotting_name'] = bioenergy_supply['plotting_name'] + ' - Biomass'
        bioenergy_supply = pd.concat([bioenergy_supply, coal])
        
        #drop table_number since this is not needed
        bioenergy_supply = bioenergy_supply.drop(columns=['table_number'])
        
        ##################
        max_and_min_values_dict = {}
        
        #we woud be better of doing these max and min values manually here since we want them to match for the two chart types (and they wont if we use the funciton below)
        
        #extract the year cols forw hich we will calculate the net imports by finding 4 digits in the column name
        year_cols = [col for col in bioenergy_supply.columns if re.search(r'\d{4}', str(col))]
        non_year_cols = [col for col in bioenergy_supply.columns if col not in year_cols]
        #drop teh total, set any negative values to 0 and then sum the rest to get the max value
        positives = bioenergy_supply[(bioenergy_supply['plotting_name']!='TPES')].copy()
        #melt so we can filter out the negative values
        positives = positives.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        #filter
        positives = positives[(positives['value'] > 0)].copy()
        #group by and sum
        max_value = positives.groupby(['year'])['value'].sum().max()
        if pd.isna(max_value):
            max_value = 0
        max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
            
        key_max = (sheet, chart_type, original_table_id, "max")
        
        #the min value will be the min of the sum of the NEGATIVE refined products and the min of the net imports:#first melt, then filter and then group by and sum
        negatives = bioenergy_supply.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        #filter
        negatives = negatives[(negatives['value'] < 0) & (negatives['plotting_name']!='TPES')].copy()
        #group by and sum
        negatives = negatives.groupby(['year'])['value'].sum().reset_index()
        min_value = negatives.value.min()
        #if there are no negative values, then the min value will be 0, so check for na
        if pd.isna(min_value):
            min_value = 0
        min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
                    
        key_min = (sheet, chart_type, original_table_id, "min")
        
        max_and_min_values_dict[key_max] = max_value
        max_and_min_values_dict[key_min] = min_value
        
        ##################
        final_table = pd.concat([final_table, bioenergy_supply])
        ##################
    #check if table is empty or all values are 0
    if final_table.empty or final_table[year_cols].sum().sum() == 0:        
        return None, None, worksheet, current_row, colours_dict
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(bioenergy_supply, colours_dict)
    patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
    
    plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)
    
    unit_dict = {sheet: 'PJ'}
    bioenergy_supply.loc[:, 'table_id'] = original_table_id
    #we should have the columns source	chart_type	plotting_name	plotting_name_column	aggregate_name	aggregate_name_column	scenario	unit	table_id	dimensions	chart_title	sheet_name + year_cols before we call this function
    charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(bioenergy_supply,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id, NEW_SCENARIO)
    return charts_to_plot, chart_positions, worksheet, current_row, colours_dict


def create_refined_products_and_liquid_biofuels_supply_charts(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row,original_table_id, NEW_SCENARIO):
    """    
    # Add the new chart creation function to the new_charts_dict
    new_charts_dict = {
        'Natural gas, LNG and biogas supply': {
        'source': 'energy',
        'sheet_name': 'natural_gas_and_lng_supply',
        'function': workbook_creation_functions.create_natural_gas_and_lng_supply_charts,
        'chart_type': 'bar'    
    }

    }
    
    energy	Refining and other transformation	Refining	5	line	sectors_plotting	Refining_output	Other petroleum products	Jet fuel	Ethane	Refinery gas not liquefied	LPG	Fuel oil	Diesel	Kerosene	Naphtha	Aviation gasoline	Gasoline
    """
    final_table = pd.DataFrame()
    for chart_type in chart_types:
        # if original_table_id == 'net_imports':#we will extract data for net imports as opposed to output
        #     table_id1 = 'energy_Refining_3'
        #     table_id2 = 'energy_Bioenergy_3'
        #     bioenergy_plotting_name= 'Net imports'
        #     chart_title = 'Net imports of refined products and liquid biofuels'
        if original_table_id == 'output':
            
            table_id1 = 'energy_Refining_3'
            table_id2 = 'energy_Bioenergy_4'
            table_id3 = 'energy_Hydrogen_6'
            efuels_plotting_name='Production'
            bioenergy_plotting_name = 'Production'
            chart_title = 'Figure 9-34. Refined products and liquid biofuels output'
        else: 
            breakpoint()
            raise Exception("Invalid original_table_id")
        #extract the data we want to use for the refined products graph, then do wahtever manipulations and calculations are needed to get it into the right format, then plotit
        refining = charts_mapping[(charts_mapping.table_id == table_id1)]
        if len(refining) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id1}')
        refining.loc[:, 'chart_title'] = chart_title
        refining.loc[:, 'table_id'] = original_table_id
        refining.loc[:, 'aggregate_name'] = 'Refined products'
        refining.loc[:, 'sheet_name'] = sheet
        
        refining.loc[:, 'chart_type'] = chart_type
        refining.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
        refining = refining[~refining.plotting_name.isin(['Stock change', 'TPES', 'Bunkers'])]
        ######        
        efuels_supply = charts_mapping[(charts_mapping.table_id == table_id3) & (charts_mapping.plotting_name == efuels_plotting_name)]
        if len(efuels_supply) == 0:
            breakpoint()
            # raise Exception(f'No data found for table {table_id2}')
            #create empty df
            efuels_supply = refining.copy()
        else:
            efuels_supply.loc[:, 'chart_title'] = chart_title
            efuels_supply.loc[:, 'table_id'] = original_table_id
            efuels_supply.loc[:, 'aggregate_name'] = 'Efuels'
            efuels_supply.loc[:, 'sheet_name'] = sheet
            
            efuels_supply.loc[:, 'chart_type'] = chart_type
            efuels_supply.loc[:, 'scenario'] = scenarios_list[scenario_num]
            
            efuels_supply.loc[:, 'plotting_name'] = 'Efuels'
            efuels_supply = pd.concat([efuels_supply, refining])
        #drop table_number since this is not needed
        efuels_supply = efuels_supply.drop(columns=['table_number'])
        ##################
        bioenergy_supply = charts_mapping[(charts_mapping.table_id == table_id2) & (charts_mapping.plotting_name == bioenergy_plotting_name)]
        if len(bioenergy_supply) == 0:
            breakpoint()
            # raise Exception(f'No data found for table {table_id2}')
            #create empty df
            bioenergy_supply = efuels_supply.copy()
        else:
            bioenergy_supply.loc[:, 'chart_title'] = chart_title
            bioenergy_supply.loc[:, 'table_id'] = original_table_id
            bioenergy_supply.loc[:, 'aggregate_name'] = 'Liquid biofuels'
            bioenergy_supply.loc[:, 'sheet_name'] = sheet
            
            bioenergy_supply.loc[:, 'chart_type'] = chart_type
            bioenergy_supply.loc[:, 'scenario'] = scenarios_list[scenario_num]
            
            ##################
            #add '- NAME' to the plotting names for the data
            bioenergy_supply.loc[:, 'plotting_name'] = 'Liquid biofuels'
            bioenergy_supply = pd.concat([bioenergy_supply, efuels_supply])
        
        ##################
        max_and_min_values_dict = {}
        
        #we woud be better of doing these max and min values manually here since we want them to match for the two chart types (and they wont if we use the funciton below)
        
        #extract the year cols forw hich we will calculate the net imports by finding 4 digits in the column name
        year_cols = [col for col in bioenergy_supply.columns if re.search(r'\d{4}', str(col))]
        non_year_cols = [col for col in bioenergy_supply.columns if col not in year_cols]
        #drop teh total, set any negative values to 0 and then sum the rest to get the max value
        positives = bioenergy_supply[(~bioenergy_supply['plotting_name'].isin(total_plotting_names))]
        #melt 
        positives = positives.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        
        max_value = positives['value'].max()
        if pd.isna(max_value):
            max_value = 0
        max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
            
        key_max = (sheet, chart_type, original_table_id, "max")
        negatives = bioenergy_supply[(~bioenergy_supply['plotting_name'].isin(total_plotting_names))]
        #the min value will be the min of the sum of the NEGATIVE refined products and the min of the net imports:#first melt
        negatives = negatives.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        #filter
        negatives = negatives[(negatives['value'] < 0)].copy()
        #group by and sum
        min_value = negatives.value.min()
        #if there are no negative values, then the min value will be 0, so check for na
        if pd.isna(min_value):
            min_value = 0
        min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
                    
        key_min = (sheet, chart_type, original_table_id, "min")
        
        max_and_min_values_dict[key_max] = max_value
        max_and_min_values_dict[key_min] = min_value
        
        ##################
        final_table = pd.concat([final_table, bioenergy_supply])
        ##################
    #check if table is empty or all values are 0
    if final_table.empty or final_table[year_cols].sum().sum() == 0:        
        return None, None, worksheet, current_row, colours_dict
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(bioenergy_supply, colours_dict)
    patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
    
    plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)
    
    unit_dict = {sheet: 'PJ'}
    bioenergy_supply.loc[:, 'table_id'] = original_table_id
    #we should have the columns source	chart_type	plotting_name	plotting_name_column	aggregate_name	aggregate_name_column	scenario	unit	table_id	dimensions	chart_title	sheet_name + year_cols before we call this function
    charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(bioenergy_supply,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id, NEW_SCENARIO)
    return charts_to_plot, chart_positions, worksheet, current_row, colours_dict

def create_hydrogen_input_charts(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row,original_table_id, NEW_SCENARIO):
    """    
    # Add the new chart creation function to the new_charts_dict
    new_charts_dict = {
        'Natural gas, LNG and biogas supply': {
        'source': 'energy',
        'sheet_name': 'natural_gas_and_lng_supply',
        'function': workbook_creation_functions.create_natural_gas_and_lng_supply_charts,
        'chart_type': 'bar'    
    }

    }
    
    energy	Refining and other transformation	Refining	5	line	sectors_plotting	Refining_output	Other petroleum products	Jet fuel	Ethane	Refinery gas not liquefied	LPG	Fuel oil	Diesel	Kerosene	Naphtha	Aviation gasoline	Gasoline
    """
    chart_title = 'Fig 9-39. Inputs for hydrogen production'
    final_table = pd.DataFrame()
    for chart_type in chart_types:
        #extract the data we want to use for the refined products graph, then do wahtever manipulations and calculations are needed to get it into the right format, then plotit
        table_id = 'energy_Hydrogen_3'
        electricity_for_hydrogen_production = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.plotting_name == 'Green electricity generation for hydrogen')]
        if len(electricity_for_hydrogen_production) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        electricity_for_hydrogen_production.loc[:, 'chart_title'] = chart_title
        electricity_for_hydrogen_production.loc[:, 'table_id'] = original_table_id
        electricity_for_hydrogen_production.loc[:, 'aggregate_name'] = 'electricity'
        electricity_for_hydrogen_production.loc[:, 'sheet_name'] = sheet
        
        electricity_for_hydrogen_production.loc[:, 'chart_type'] = chart_type
        electricity_for_hydrogen_production.loc[:, 'scenario'] = scenarios_list[scenario_num]
        #make sur value's negatove:
        # breakpoint()
        year_cols = [col for col in electricity_for_hydrogen_production.columns if re.search(r'\d{4}', str(col))]
        electricity_for_hydrogen_production.loc[:, year_cols] = -electricity_for_hydrogen_production.loc[:, year_cols].abs()
        #rename Green electricity input for hydrogen to 'Green electricity'
         
        # electricity_for_hydrogen_production.loc[electricity_for_hydrogen_production['plotting_name'] == 'Green electricity input for hydrogen', 'plotting_name'] = 'Green electricity for electrolysis'
        ######
        #now do gas for hydrogen production
        gas_df = pd.DataFrame()
        table_id = 'energy_Hydrogen_5'
        
        gas = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.plotting_name == 'Hydrogen_input_ccs')]
        if len(gas) != 0:
            # breakpoint()
            # raise Exception(f'No data found for table {table_id}')
            gas.loc[:, 'chart_title'] = chart_title
            gas.loc[:, 'table_id'] = original_table_id
            gas.loc[:, 'aggregate_name'] = 'gas'
            gas.loc[:, 'sheet_name'] = sheet
            
            gas.loc[:, 'chart_type'] = chart_type
            gas.loc[:, 'scenario'] = scenarios_list[scenario_num]
            # breakpoint()#this doesnt seem to be passing any data
            #make sure value's negative:
            gas.loc[:, year_cols] = -gas.loc[:, year_cols].abs()
            #rename to 'Gas for hydrogen production'
            gas.loc[:, 'plotting_name'] = 'Gas for steam methane reforming with CCS'
            table_id = 'energy_Hydrogen_3'
            gas_df = pd.concat([gas_df, gas])
        ######
        gas = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.plotting_name == 'Hydrogen_input_no_ccs')]
        if len(gas) != 0:
            # breakpoint()
            # raise Exception(f'No data found for table {table_id}')
            gas.loc[:, 'chart_title'] = chart_title
            gas.loc[:, 'table_id'] = original_table_id
            gas.loc[:, 'aggregate_name'] = 'gas'
            gas.loc[:, 'sheet_name'] = sheet
            
            gas.loc[:, 'chart_type'] = chart_type
            gas.loc[:, 'scenario'] = scenarios_list[scenario_num]
            # breakpoint()#this doesnt seem to be passing any data
            #make sure value's negative:
            gas.loc[:, year_cols] = -gas.loc[:, year_cols].abs()
            #rename to 'Gas for hydrogen production'
            gas.loc[:, 'plotting_name'] = 'Gas for steam methane reforming'
            gas_df = pd.concat([gas_df, gas])
        # #######
        # #now do hydrogen supply, including production types:
        # table_id = 'energy_Hydrogen_2'
        # hydrogen_supply = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.plotting_name != 'TPES')]
        # if len(hydrogen_supply) == 0:
        #     breakpoint()
        #     raise Exception(f'No data found for table {table_id}')
        # hydrogen_supply.loc[:, 'chart_title'] = chart_title
        # hydrogen_supply.loc[:, 'table_id'] = original_table_id
        # hydrogen_supply.loc[:, 'aggregate_name'] = 'hydrogen'
        # hydrogen_supply.loc[:, 'sheet_name'] = sheet
        
        # hydrogen_supply.loc[:, 'chart_type'] = chart_type
        # hydrogen_supply.loc[:, 'scenario'] = scenarios_list[scenario_num]
        # #make sure value's positive:
        # hydrogen_supply.loc[:, year_cols] = hydrogen_supply.loc[:, year_cols].abs()
        # #rename Imports to 'Hydrogen-based fuel imports'
        # hydrogen_supply.loc[hydrogen_supply['plotting_name'] == 'Imports', 'plotting_name'] = 'Hydrogen-based fuel imports'
        # #rename Electrolysis to 'Hydrogen Electrolysis'
        # hydrogen_supply.loc[hydrogen_supply['plotting_name'] == 'Electrolysis', 'plotting_name'] = 'Electrolysis output'

        # hydrogen_supply.loc[hydrogen_supply['plotting_name'] == 'Steam methane reforming CCS', 'plotting_name'] = 'Steam methane reforming output'
        
        # ##################
        # #add '- NAME' to the plotting names for the data
        # coal.loc[:, 'plotting_name'] = coal['plotting_name'] + ' - Coal'
        # bioenergy_supply.loc[:, 'plotting_name'] = bioenergy_supply['plotting_name'] + ' - Bioenergy'
        hydrogen_supply = pd.concat([gas_df, electricity_for_hydrogen_production])#hydrogen_supply, 
        
        #drop table_number since this is not needed
        hydrogen_supply = hydrogen_supply.drop(columns=['table_number'])
        
        ##################
        max_and_min_values_dict = {}
        
        #we woud be better of doing these max and min values manually here since we want them to match for the two chart types (and they wont if we use the funciton below)
        
        #extract the year cols forw hich we will calculate the net imports by finding 4 digits in the column name
        year_cols = [col for col in hydrogen_supply.columns if re.search(r'\d{4}', str(col))]
        non_year_cols = [col for col in hydrogen_supply.columns if col not in year_cols]
        #drop teh total, set any negative values to 0 and then sum the rest to get the max value
        positives = hydrogen_supply.copy()
        #melt so we can filter out the negative values
        positives = positives.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        #filter
        positives = positives[(positives['value'] > 0)].copy()
        #group by and sum
        max_value = positives.groupby(['year'])['value'].sum().max()
        if pd.isna(max_value):
            max_value = 0
        max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
            
        key_max = (sheet, chart_type, original_table_id, "max")
        
        #the min value will be the min of the sum of the NEGATIVE refined products and the min of the net imports:#first melt, then filter and then group by and sum
        negatives = hydrogen_supply.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        #filter
        negatives = negatives[(negatives['value'] < 0)].copy()
        #group by and sum
        negatives = negatives.groupby(['year'])['value'].sum().reset_index()
        min_value = negatives.value.min()
        #if there are no negative values, then the min value will be 0, so check for na
        if pd.isna(min_value):
            min_value = 0
        min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
                    
        key_min = (sheet, chart_type, original_table_id, "min")
        
        max_and_min_values_dict[key_max] = max_value
        max_and_min_values_dict[key_min] = min_value
        
        ##################
        final_table = pd.concat([final_table, hydrogen_supply])
        ##################
    #check if table is empty or all values are 0
    if final_table.empty or final_table[year_cols].sum().sum() == 0:        
        return None, None, worksheet, current_row, colours_dict
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(hydrogen_supply, colours_dict)
    patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
    
    plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)
    
    unit_dict = {sheet: 'PJ'}
    hydrogen_supply.loc[:, 'table_id'] = original_table_id
    #we should have the columns source	chart_type	plotting_name	plotting_name_column	aggregate_name	aggregate_name_column	scenario	unit	table_id	dimensions	chart_title	sheet_name + year_cols before we call this function
    charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(hydrogen_supply,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id, NEW_SCENARIO)
    return charts_to_plot, chart_positions, worksheet, current_row, colours_dict


# def create_hydrogen_production_input_vs_output_charts(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row,original_table_id, NEW_SCENARIO):
#     """    
#     # Add the new chart creation function to the new_charts_dict
#     new_charts_dict = {
#         'Natural gas, LNG and biogas supply': {
#         'source': 'energy',
#         'sheet_name': 'natural_gas_and_lng_supply',
#         'function': workbook_creation_functions.create_natural_gas_and_lng_supply_charts,
#         'chart_type': 'bar'    
#     }

#     }
    
#     energy	Refining and other transformation	Refining	5	line	sectors_plotting	Refining_output	Other petroleum products	Jet fuel	Ethane	Refinery gas not liquefied	LPG	Fuel oil	Diesel	Kerosene	Naphtha	Aviation gasoline	Gasoline
#     """
#     chart_title = ''
#     final_table = pd.DataFrame()
#     for chart_type in chart_types:
#         #extract the data we want to use for the refined products graph, then do wahtever manipulations and calculations are needed to get it into the right format, then plotit
#         table_id = 'energy_Hydrogen_4'
#         electricity_for_hydrogen_production = charts_mapping[(charts_mapping.table_id == table_id)]
#         if len(electricity_for_hydrogen_production) == 0:
#             breakpoint()
#             raise Exception(f'No data found for table {table_id}')
#         electricity_for_hydrogen_production.loc[:, 'chart_title'] = chart_title
#         electricity_for_hydrogen_production.loc[:, 'table_id'] = original_table_id
#         electricity_for_hydrogen_production.loc[:, 'aggregate_name'] = 'electricity'
#         electricity_for_hydrogen_production.loc[:, 'sheet_name'] = sheet
        
#         electricity_for_hydrogen_production.loc[:, 'chart_type'] = chart_type
#         electricity_for_hydrogen_production.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
#         #we want to group and sum similar elec types so we have the categories:
#         #         'Renewable capacity for electrolysis', 'Solar and wind capacity', 'Other capacity'
#         #from the categories: Green electricity input for hydrogen
#         #  Electricity output coal	Electricity output gas	Electricity output other	Electricity output solar	Electricity output wind	Electricity output nuclear	Electricity output hydro

#         mapping_dict = {
            
#             'Green electricity input for hydrogen': 'Renewable capacity for electrolysis',
#             'Electricity output coal': 'Other capacity',
#             'Electricity output gas': 'Other capacity',
#             'Electricity output other': 'Other capacity',
#             'Electricity output solar': 'Solar and wind capacity',
#             'Electricity output wind': 'Solar and wind capacity',
#             'Electricity output nuclear': 'Other capacity',
#             'Electricity output hydro': 'Other capacity'
            
#         }
#         electricity_for_hydrogen_production.loc[:, 'plotting_name'] = electricity_for_hydrogen_production['plotting_name'].replace(mapping_dict)
        
#         electricity_for_hydrogen_production = electricity_for_hydrogen_production.drop(columns=['table_number'])
        
#         #extract the year cols for which we will calculate the net imports by finding 4 digits in the column name
#         year_cols = [col for col in electricity_for_hydrogen_production.columns if re.search(r'\d{4}', str(col))]
#         non_year_cols = [col for col in electricity_for_hydrogen_production.columns if col not in year_cols]
#         #sum by non year cols
        
#         electricity_for_hydrogen_production = electricity_for_hydrogen_production.groupby(non_year_cols).sum().reset_index()
#         ##################
#         max_and_min_values_dict = {}
        
#         #we would be better off doing these max and min values manually here since we want them to match for the two chart types (and they won't if we use the function below)
        
#         #drop teh total, set any negative values to 0 and then sum the rest to get the max value
#         positives = electricity_for_hydrogen_production.copy()
#         #melt so we can filter out the negative values
#         positives = positives.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
#         #filter
#         positives = positives[(positives['value'] > 0)].copy()
#         #group by and sum
#         max_value = positives.groupby(['year'])['value'].sum().max()
#         if pd.isna(max_value):
#             max_value = 0
#         max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
            
#         key_max = (sheet, chart_type, original_table_id, "max")
        
#         #the min value will be the min of the sum of the NEGATIVE refined products and the min of the net imports:#first melt, then filter and then group by and sum
#         negatives = electricity_for_hydrogen_production.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
#         #filter
#         negatives = negatives[(negatives['value'] < 0)].copy()
#         #group by and sum
#         negatives = negatives.groupby(['year'])['value'].sum().reset_index()
#         min_value = negatives.value.min()
#         #if there are no negative values, then the min value will be 0, so check for na
#         if pd.isna(min_value):
#             min_value = 0
#         min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
                    
#         key_min = (sheet, chart_type, original_table_id, "min")
        
#         max_and_min_values_dict[key_max] = max_value
#         max_and_min_values_dict[key_min] = min_value
        
#         ##################
#         final_table = pd.concat([final_table, electricity_for_hydrogen_production])
#         ##################
#     #check if table is empty or all values are 0
#     if final_table.empty or final_table[year_cols].sum().sum() == 0:        
#         return None, None, worksheet, current_row, colours_dict
#     colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(electricity_for_hydrogen_production, colours_dict)
#     patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
    
#     plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)
    
#     unit_dict = {sheet: 'PJ'}
#     electricity_for_hydrogen_production.loc[:, 'table_id'] = original_table_id
#     #we should have the columns source	chart_type	plotting_name	plotting_name_column	aggregate_name	aggregate_name_column	scenario	unit	table_id	dimensions	chart_title	sheet_name + year_cols before we call this function
#     charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(electricity_for_hydrogen_production,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id, NEW_SCENARIO)
#     return charts_to_plot, chart_positions, worksheet, current_row, colours_dict

def create_crude_and_ngl_supply_charts(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row,original_table_id, NEW_SCENARIO):
    """    
    # Add the new chart creation function to the new_charts_dict
    new_charts_dict = {
        'Natural gas, LNG and biogas supply': {
        'source': 'energy',
        'sheet_name': 'natural_gas_and_lng_supply',
        'function': workbook_creation_functions.create_natural_gas_and_lng_supply_charts,
        'chart_type': 'bar'    
    }

    }
    
    energy	Refining and other transformation	Refining	5	line	sectors_plotting	Refining_output	Other petroleum products	Jet fuel	Ethane	Refinery gas not liquefied	LPG	Fuel oil	Diesel	Kerosene	Naphtha	Aviation gasoline	Gasoline
    """
    final_table = pd.DataFrame()
    for chart_type in chart_types:
        #extract the data we want to use for the refined products graph, then do wahtever manipulations and calculations are needed to get it into the right format, then plotit
        table_id = 'energy_Refining_5'
        crude = charts_mapping[(charts_mapping.table_id == table_id)]
        if len(crude) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        crude.loc[:, 'chart_title'] = 'Figure 9-32. Crude oil and NGL supply'
        crude.loc[:, 'table_id'] = original_table_id
        crude.loc[:, 'aggregate_name'] = 'Crude oil'
        crude.loc[:, 'sheet_name'] = sheet
        
        crude.loc[:, 'chart_type'] = chart_type
        crude.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
        crude = crude[~crude.plotting_name.isin(['Stock change', 'TPES', 'Bunkers'])]
        ######
        table_id = 'energy_Refining_6'
        ngls = charts_mapping[(charts_mapping.table_id == table_id)]
        if len(ngls) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        ngls.loc[:, 'chart_title'] = 'Figure 9-32. Crude oil and NGL supply'
        ngls.loc[:, 'table_id'] = original_table_id
        ngls.loc[:, 'aggregate_name'] = 'NGLs'
        ngls.loc[:, 'sheet_name'] = sheet
        
        ngls.loc[:, 'chart_type'] = chart_type
        ngls.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
        ngls = ngls[~ngls.plotting_name.isin(['Stock change', 'TPES', 'Bunkers'])]
        ##################
        #add '- NAME' to the plotting names for the data
        ngls.loc[:, 'plotting_name'] = ngls['plotting_name'] + ' - NGL'
        crude.loc[:, 'plotting_name'] = crude['plotting_name'] + ' - Crude'
        crude_and_ngls = pd.concat([crude, ngls])
        
        #drop table_number since this is not needed
        crude_and_ngls = crude_and_ngls.drop(columns=['table_number'])
        
        ##################
        max_and_min_values_dict = {}
        
        #we woud be better of doing these max and min values manually here since we want them to match for the two chart types (and they wont if we use the funciton below)
        
        #extract the year cols forw hich we will calculate the net imports by finding 4 digits in the column name
        year_cols = [col for col in crude_and_ngls.columns if re.search(r'\d{4}', str(col))]
        non_year_cols = [col for col in crude_and_ngls.columns if col not in year_cols]
        #drop teh total, set any negative values to 0 and then sum the rest to get the max value
        positives = crude_and_ngls[(crude_and_ngls['plotting_name']!='TPES')].copy()
        #melt so we can filter out the negative values
        positives = positives.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        #filter
        positives = positives[(positives['value'] > 0)].copy()
        #group by and sum
        max_value = positives.groupby(['year'])['value'].sum().max()
        if pd.isna(max_value):
            max_value = 0
        max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
            
        key_max = (sheet, chart_type, original_table_id, "max")
        
        #the min value will be the min of the sum of the NEGATIVE refined products and the min of the net imports:#first melt, then filter and then group by and sum
        negatives = crude_and_ngls.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        #filter
        negatives = negatives[(negatives['value'] < 0) & (negatives['plotting_name']!='TPES')].copy()
        #group by and sum
        negatives = negatives.groupby(['year'])['value'].sum().reset_index()
        min_value = negatives.value.min()
        #if there are no negative values, then the min value will be 0, so check for na
        if pd.isna(min_value):
            min_value = 0
        min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
                    
        key_min = (sheet, chart_type, original_table_id, "min")
        
        max_and_min_values_dict[key_max] = max_value
        max_and_min_values_dict[key_min] = min_value
        
        ##################
        final_table = pd.concat([final_table, crude_and_ngls])
        ##################
    #check if table is empty or all values are 0
    if final_table.empty or final_table[year_cols].sum().sum() == 0:        
        return None, None, worksheet, current_row, colours_dict
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(crude_and_ngls, colours_dict)
    patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
    
    plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)
    
    unit_dict = {sheet: 'PJ'}
    crude_and_ngls.loc[:, 'table_id'] = original_table_id
    #we should have the columns source	chart_type	plotting_name	plotting_name_column	aggregate_name	aggregate_name_column	scenario	unit	table_id	dimensions	chart_title	sheet_name + year_cols before we call this function
    charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(crude_and_ngls,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id, NEW_SCENARIO)
    return charts_to_plot, chart_positions, worksheet, current_row, colours_dict
