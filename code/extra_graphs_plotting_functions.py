
import pandas as pd
import workbook_creation_functions
from utility_functions import *
import numpy as np

import re, os, matplotlib.pyplot as plt, seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

def create_extra_graphs(workbook, all_charts_mapping_files_dict, total_plotting_names, MIN_YEAR,  plotting_specifications, plotting_names_order,plotting_name_to_label_dict, colours_dict, patterns_dict, cell_format1, cell_format2, new_charts_dict, header_format, writer, EXPECTED_COLS,ECONOMY_ID):
    scenarios_list=['reference', 'target']
    #use this to create graphs that are a little more complex than the standard ones. tehse will be deisgned on a case by case basis, using explicit code.
            
    for new_chart in new_charts_dict.keys():
        source = new_charts_dict[new_chart]['source']
        sheet_name = new_charts_dict[new_chart]['sheet_name']
        function = new_charts_dict[new_chart]['function']
        chart_types = new_charts_dict[new_chart]['chart_types']
        tables = new_charts_dict[new_chart]['tables']
        try:
            if len(all_charts_mapping_files_dict[source]) != 1:
                breakpoint()
                raise Exception(f'Expected exactly 1 charts mapping file for create_extra_graphs() for source {source}, but found {len(all_charts_mapping_files_dict[source])}')
        except:
            breakpoint()
        #check charttypes is  list
        if not isinstance(chart_types, list):
            chart_types = [chart_types]
            
        charts_mapping = all_charts_mapping_files_dict[source][0]
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
                charts_to_plot, chart_positions, worksheet,current_row = function(charts_mapping_scenario, sheet_name,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict, cell_format1, cell_format2, scenario_num, scenarios_list, header_format, plotting_specifications, writer, chart_types,ECONOMY_ID, scenario, current_row, original_table_id,NEW_SCENARIO)
                NEW_SCENARIO = False#wat is the chart pos and charts to plot when we are looking at imports
                if charts_to_plot is None:
                    continue
                worksheet = workbook_creation_functions.write_charts_to_sheet(charts_to_plot, chart_positions, worksheet)
                
            scenario_num+=1
        
            ###############
    workbook = workbook_creation_functions.order_sheets(workbook, plotting_specifications)
    return workbook, writer
        
def format_sheet_for_other_graphs(data,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet,workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict, cell_format1, cell_format2, max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID,unit_dict, current_scenario, current_row, original_table_id, NEW_SCENARIO,PLOTTING_SEABORN=False):
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
    if not PLOTTING_SEABORN:
        charts_to_plot = workbook_creation_functions.create_charts(table, chart_types, plotting_specifications, workbook, num_table_rows, plotting_name_column, original_table_id, sheet, current_row, space_under_tables, column_row, year_cols_start, num_cols, colours_dict, patterns_dict,total_plotting_names, max_and_min_values_dict, chart_titles, first_year_col, sheet_name)
    else:
        return None, chart_positions, worksheet, current_scenario, current_row
    return charts_to_plot, chart_positions, worksheet, current_scenario, current_row

def create_refined_products_bar_and_net_imports_line(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row, original_table_id, NEW_SCENARIO):
    """    
    # Add the new chart creation function to the new_charts_dict
    new_charts_dict = {
        'Refined products and crude oil net imports': {
            'source': 'energy',
            'sheet_name': 'Refined products and crude oil net imports',
            'function': create_refined_products_bar_and_net_imports_line,
            'chart_type': 'combined_line_bar'
        }
    }
    """
    if len(chart_types)!=1:
        breakpoint()
        raise Exception('Expected exactly 1 chart type in create_refined_products_bar_and_net_imports_line()')
    
    #extract the data we want to use for the refined products graph, then do wahtever manipulations and calculations are needed to get it into the right format, then plotit
    table_id = 'energy_Refining_3'
    refined_products = charts_mapping[(charts_mapping.table_id == table_id)]
    if len(refined_products) == 0:
        breakpoint()
        raise Exception(f'No data found for table {table_id} in create_refined_products_bar_and_crude_oil_supply_line()')
    refined_products.loc[:, 'chart_title'] = 'Refined products and crude oil supply'
    refined_products.loc[:, 'table_id'] = original_table_id
    refined_products.loc[:, 'aggregate_name'] = 'Refined products'
    refined_products.loc[:, 'sheet_name'] = sheet
    refined_products.loc[:, 'chart_type'] = 'bar'
    refined_products.loc[:, 'scenario'] = scenarios_list[scenario_num]
    ######
    table_id = 'energy_Refining_7'
    aggregate_name = 'Crude oil & NGL'
    
    crude_oil_supply_line_IMPORTS = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.plotting_name.isin(['Imports'])) & (charts_mapping.aggregate_name == aggregate_name)]
    crude_oil_supply_line_EXPORTS = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.plotting_name.isin(['Exports'])) & (charts_mapping.aggregate_name == aggregate_name)]
    
    crude_oil_supply_line_production = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.plotting_name.isin(['Production'])) & (charts_mapping.aggregate_name == aggregate_name)]
    
    if len(crude_oil_supply_line_IMPORTS) == 0 or len(crude_oil_supply_line_EXPORTS) == 0 or len(crude_oil_supply_line_production) == 0:
        breakpoint()
        raise Exception(f'No data found for table {table_id} in create_refined_products_bar_and_crude_oil_supply_line()')
    #extract the year cols forw hich we will calculate the net imports by finding 4 digits in the column name
    year_cols = [col for col in crude_oil_supply_line_IMPORTS.columns if re.search(r'\d{4}', str(col))]
    #calculate the net imports by taking the difference between imports and exports)
    crude_oil_supply_line_net_imports = crude_oil_supply_line_IMPORTS.copy()
    for year in year_cols:
        if len(crude_oil_supply_line_IMPORTS[year].values) != 1 or len(crude_oil_supply_line_EXPORTS[year].values) != 1:
            raise Exception(f'Expected exactly 1 value for imports and exports for year {year} in create_refined_products_bar_and_crude_oil_supply_line()')
        crude_oil_supply_line_net_imports[year] = crude_oil_supply_line_IMPORTS[year].values[0] - crude_oil_supply_line_EXPORTS[year].values[0]
    ######
    # crude_oil_supply_line.loc[:, 'plotting_name'] = 'Net crude imports'
    crude_oil_supply_line_IMPORTS.loc[:, 'plotting_name'] = 'Crude imports'
    crude_oil_supply_line_EXPORTS.loc[:, 'plotting_name'] = 'Crude exports'
    crude_oil_supply_line_production.loc[:, 'plotting_name'] = 'Crude production'
    #add the IMPORTS and EXPORTS to the crude_oil_supply_line df
    crude_oil_supply_line =pd.concat([crude_oil_supply_line_IMPORTS, crude_oil_supply_line_EXPORTS, crude_oil_supply_line_production])#crude_oil_supply_line_net_imports
    crude_oil_supply_line.loc[:, 'chart_title'] = 'Refined products and crude oil supply'
    crude_oil_supply_line.loc[:, 'table_id'] = sheet
    crude_oil_supply_line.loc[:, 'aggregate_name'] = 'Crude oil & NGL'
    crude_oil_supply_line.loc[:, 'sheet_name'] = sheet
    crude_oil_supply_line.loc[:, 'chart_type'] = 'line'
    crude_oil_supply_line.loc[:, 'scenario'] = scenarios_list[scenario_num]

    #now concatenate the two dataframes
    refined_products_and_net_imports = pd.concat([refined_products, crude_oil_supply_line])
    
    #drop table_number since this is not needed
    refined_products_and_net_imports = refined_products_and_net_imports.drop(columns=['table_number'])
    
    ##################
    max_and_min_values_dict = {}
    #we woud be better of doing these max and min values manually here sincewe want them to match for the two chart types (and they wont if we use the funciton below)
    #the max vlaue will ave to be the max betwene the sum of the postivie refined products and the max of the net imports:
    postive_refined_products = refined_products_and_net_imports[refined_products_and_net_imports['plotting_name'].isin(['Domestic refining', 'Exports', 'Stock change', 'Imports'])]
    postive_refined_products = refined_products[(refined_products[year_cols] > 0)]# & (refined_products['plotting_name'] != 'Total')]
    max_value_refined = postive_refined_products[year_cols].sum(axis=0).max()
    max_value_crude_oil_supply = refined_products_and_net_imports.loc[refined_products_and_net_imports.plotting_name.isin(['Crude production', 'Crude exports', 'Crude imports']), year_cols].max().max()
    max_value = max(max_value_refined, max_value_crude_oil_supply) 
    if pd.isna(max_value):
        max_value = 0
    max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
        
    key_max_line = (sheet, 'line', original_table_id, "max")
    key_max_bar = (sheet, 'bar', original_table_id, "max")
    key_max_bar_line = (sheet, 'combined_line_bar', original_table_id, "max")
    #the min value will be the min of the sum of the NEGATIVE refined products and the min of the net imports:#first melt, then filter and then group by and sum
    
    negative_refined_products = refined_products_and_net_imports[refined_products_and_net_imports['plotting_name'].isin(['Domestic refining', 'Exports', 'Stock change', 'Imports'])]
    negative_refined_products = negative_refined_products[(negative_refined_products[year_cols] < 0)]# & (refined_products['plotting_name'] != 'Total')]
    min_value_refined = negative_refined_products[year_cols].sum(axis=0).min()
    min_value_crude_oil_supply = refined_products_and_net_imports.loc[refined_products_and_net_imports.plotting_name.isin(['Crude production', 'Crude exports', 'Crude imports']), year_cols].min().min()
    min_value = min(min_value_refined, min_value_crude_oil_supply) 
    if pd.isna(min_value):
        min_value = 0
    min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
        
    key_min_line = (sheet, 'line', original_table_id, "min")
    key_min_bar = (sheet, 'bar', original_table_id, "min")
    key_min_bar_line = (sheet, 'combined_line_bar', original_table_id, "min")
    
    max_and_min_values_dict[key_max_line] = max_value
    max_and_min_values_dict[key_max_bar] = max_value
    max_and_min_values_dict[key_min_line] = min_value
    max_and_min_values_dict[key_min_bar] = min_value
    max_and_min_values_dict[key_max_bar_line] = max_value
    max_and_min_values_dict[key_min_bar_line] = min_value
    ##################
    if refined_products_and_net_imports.empty:
        return None, None, worksheet
    
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(charts_mapping, colours_dict)
    patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
    plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)
    
    unit_dict = {sheet: 'PJ'}
    refined_products_and_net_imports.loc[:, 'table_id'] = original_table_id
    #we should have the columns source	chart_type	plotting_name	plotting_name_column	aggregate_name	aggregate_name_column	scenario	unit	table_id	dimensions	chart_title	sheet_name + year_cols before we call this function
    charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(refined_products_and_net_imports,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id,NEW_SCENARIO)
    
    return charts_to_plot, chart_positions, worksheet,current_row

def create_refining_and_low_carbon_fuels(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row,original_table_id, NEW_SCENARIO):
    """    
    # Add the new chart creation function to the new_charts_dict
    new_charts_dict = {
        'Refining output - incl. low-carbon fuels': {
        'source': 'energy',
        'sheet_name': 'Refining_and_low_carbon_fuels',
        'function': workbook_creation_functions.create_refining_and_low_carbon_fuels,
        'chart_type': 'percentage_bar'    
    }

    }
    
    energy	Refining and other transformation	Refining	5	line	sectors_plotting	Refining_output	Other petroleum products	Jet fuel	Ethane	Refinery gas not liquefied	LPG	Fuel oil	Diesel	Kerosene	Naphtha	Aviation gasoline	Gasoline
    """
    final_table = pd.DataFrame()
    for chart_type in chart_types:
        #extract the data we want to use for the refined products graph, then do wahtever manipulations and calculations are needed to get it into the right format, then plotit
        table_id = 'energy_Refining_5'
        refined_products = charts_mapping[(charts_mapping.table_id == table_id)]
        if len(refined_products) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        refined_products.loc[:, 'chart_title'] = 'Refining output - incl. low-carbon fuels'
        refined_products.loc[:, 'table_id'] = original_table_id
        refined_products.loc[:, 'aggregate_name'] = 'Refining and other transformation'
        refined_products.loc[:, 'sheet_name'] = sheet
        
        refined_products.loc[:, 'chart_type'] = chart_type
        refined_products.loc[:, 'scenario'] = scenarios_list[scenario_num]
        ######
        table_id = 'energy_Low carbon fuels_1'
        plotting_names = ['Hydrogen_transformation_output']
        low_carbon_fuels_hydrogen = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.plotting_name.isin(plotting_names))]

        if len(low_carbon_fuels_hydrogen) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id} , plotting names {plotting_names} in create_refining_and_low_carbon_fuels()')
        #biofuels are in production so charted separately to hydrogen
        table_id = 'energy_Bioenergy_3'
        plotting_names = ['Production']
        low_carbon_fuels_biofuels = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.plotting_name.isin(plotting_names))]
        if len(low_carbon_fuels_biofuels) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id} , plotting names {plotting_names} in create_refining_and_low_carbon_fuels()')
        low_carbon_fuels_hydrogen.loc[:, 'plotting_name'] = 'Hydrogen-based fuels'
        low_carbon_fuels_biofuels.loc[:, 'plotting_name'] = 'Liquid biofuels'
        
        #then combine the two dataframes
        low_carbon_fuels = pd.concat([low_carbon_fuels_hydrogen, low_carbon_fuels_biofuels])
        
        low_carbon_fuels.loc[:, 'chart_title'] = 'Refining output - incl. low-carbon fuels'
        low_carbon_fuels.loc[:, 'table_id'] = original_table_id
        low_carbon_fuels.loc[:, 'aggregate_name'] = 'Refining and other transformation'
        low_carbon_fuels.loc[:, 'sheet_name'] = sheet
        low_carbon_fuels.loc[:, 'chart_type'] = chart_type
        low_carbon_fuels.loc[:, 'scenario'] = scenarios_list[scenario_num]
        #now concatenate the two dataframes
        refined_products_and_low_carbon_fuels = pd.concat([refined_products, low_carbon_fuels])
        
        #drop table_number since this is not needed
        refined_products_and_low_carbon_fuels = refined_products_and_low_carbon_fuels.drop(columns=['table_number'])
        
        ##################
        max_and_min_values_dict = {}
        #we woud be better of doing these max and min values manually here sincewe want them to match for the two chart types (and they wont if we use the funciton below)
        
        #extract the year cols forw hich we will calculate the net imports by finding 4 digits in the column name
        year_cols = [col for col in refined_products_and_low_carbon_fuels.columns if re.search(r'\d{4}', str(col))]
        
        max_value = refined_products_and_low_carbon_fuels[year_cols].sum(axis=0).max()
        if pd.isna(max_value):
            max_value = 0
        max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
            
        key_max = (sheet, chart_type, original_table_id, "max")
        
        min_value = 0#refined_products_and_low_carbon_fuels[year_cols].min().min()
        min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
            
        key_min = (sheet, chart_type, original_table_id, "min")
        
        max_and_min_values_dict[key_max] = max_value
        max_and_min_values_dict[key_min] = min_value
        
        ##################
        final_table = pd.concat([final_table, refined_products_and_low_carbon_fuels])
        ##################
    if final_table.empty or final_table[year_cols].sum().sum() == 0:
        breakpoint()
        return None, None, worksheet
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(refined_products_and_low_carbon_fuels, colours_dict)
    patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
    plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)
    
    unit_dict = {sheet: 'PJ'}
    refined_products_and_low_carbon_fuels.loc[:, 'table_id'] = original_table_id
    #we should have the columns source	chart_type	plotting_name	plotting_name_column	aggregate_name	aggregate_name_column	scenario	unit	table_id	dimensions	chart_title	sheet_name + year_cols before we call this function
    charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(refined_products_and_low_carbon_fuels,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id, NEW_SCENARIO)
    
    return charts_to_plot, chart_positions, worksheet, current_row

def create_liquid_biofuels_and_bioenergy_supply_charts(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row,original_table_id, NEW_SCENARIO):
    """    
    # Add the new chart creation function to the new_charts_dict
    new_charts_dict = {
        'Natural gas and LNG supply': {
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
        table_id = 'energy_Bioenergy_3'
        liquid_biofuels_supply = charts_mapping[(charts_mapping.table_id == table_id)]
        if len(liquid_biofuels_supply) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        liquid_biofuels_supply.loc[:, 'chart_title'] = 'Bioenergy supply'
        liquid_biofuels_supply.loc[:, 'table_id'] = original_table_id
        liquid_biofuels_supply.loc[:, 'aggregate_name'] = 'Liquid biofuels'
        liquid_biofuels_supply.loc[:, 'sheet_name'] = sheet
        
        liquid_biofuels_supply.loc[:, 'chart_type'] = chart_type
        liquid_biofuels_supply.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
        #drop plpotting names = stock change, TPES and bunkers since we dont want to plot these with - LNG as they are for all natural gas (including LNG)
        liquid_biofuels_supply = liquid_biofuels_supply[~liquid_biofuels_supply.plotting_name.isin(['Stock change', 'TPES', 'Bunkers'])]
        ######
        table_id = 'energy_Bioenergy_4'
        bioenergy_supply = charts_mapping[(charts_mapping.table_id == table_id)]
        if len(bioenergy_supply) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        bioenergy_supply.loc[:, 'chart_title'] = 'Bioenergy supply'
        bioenergy_supply.loc[:, 'table_id'] = original_table_id
        bioenergy_supply.loc[:, 'aggregate_name'] = 'Bioenergy'
        bioenergy_supply.loc[:, 'sheet_name'] = sheet
        
        bioenergy_supply.loc[:, 'chart_type'] = chart_type
        bioenergy_supply.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
        ##################
        #join and then take liquid biofuels away from the bioenergy data to get the non-liquid biofuels data:
        year_cols = [col for col in bioenergy_supply.columns if re.search(r'\d{4}', str(col))]
        non_year_cols = [col for col in bioenergy_supply.columns if col not in year_cols + ['value']]
        liquid_biofuels_supply_melt = liquid_biofuels_supply.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        bioenergy_supply_melt = bioenergy_supply.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        bioenergy_supply = pd.merge(liquid_biofuels_supply_melt, bioenergy_supply_melt, on=['plotting_name', 'year'], how='right', suffixes=('_liq', ''))
        bioenergy_supply['value'] = bioenergy_supply['value'] - bioenergy_supply['value_liq'].replace(np.nan, 0)
        bioenergy_supply = bioenergy_supply.drop(columns=[col for col in bioenergy_supply.columns if col.endswith('_liq')])
        bioenergy_supply = bioenergy_supply.pivot(index=non_year_cols, columns='year', values='value').reset_index()
        ##################        
        #add '- LNG' to the plotting names for the LNG data
        liquid_biofuels_supply.loc[:, 'plotting_name'] = liquid_biofuels_supply['plotting_name'] + ' - Liquid biofuels'
        bioenergy_supply = pd.concat([bioenergy_supply, liquid_biofuels_supply])
        
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
        return None, None, worksheet
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(bioenergy_supply, colours_dict)
    patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
    
    plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)
    
    unit_dict = {sheet: 'PJ'}
    bioenergy_supply.loc[:, 'table_id'] = original_table_id
    #we should have the columns source	chart_type	plotting_name	plotting_name_column	aggregate_name	aggregate_name_column	scenario	unit	table_id	dimensions	chart_title	sheet_name + year_cols before we call this function
    charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(bioenergy_supply,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id, NEW_SCENARIO)
    return charts_to_plot, chart_positions, worksheet, current_row


def create_natural_gas_and_lng_supply_charts(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row,original_table_id, NEW_SCENARIO):
    """    
    # Add the new chart creation function to the new_charts_dict
    new_charts_dict = {
        'Natural gas and LNG supply': {
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
        table_id = 'energy_Natural gas_4'
        lng_supply = charts_mapping[(charts_mapping.table_id == table_id)]
        if len(lng_supply) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        lng_supply.loc[:, 'chart_title'] = 'Natural gas and LNG supply'
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
        nat_gas_supply.loc[:, 'chart_title'] = 'Natural gas and LNG supply'
        nat_gas_supply.loc[:, 'table_id'] = original_table_id
        nat_gas_supply.loc[:, 'aggregate_name'] = 'Natural gas'
        nat_gas_supply.loc[:, 'sheet_name'] = sheet
        
        nat_gas_supply.loc[:, 'chart_type'] = chart_type
        nat_gas_supply.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
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
        nat_gas_supply = pd.concat([nat_gas_supply, lng_supply])
        
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
        return None, None, worksheet
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(nat_gas_supply, colours_dict)
    patterns_dict = workbook_creation_functions.check_plotting_names_in_patterns_dict(patterns_dict)
    
    plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)
    
    unit_dict = {sheet: 'PJ'}
    nat_gas_supply.loc[:, 'table_id'] = original_table_id
    #we should have the columns source	chart_type	plotting_name	plotting_name_column	aggregate_name	aggregate_name_column	scenario	unit	table_id	dimensions	chart_title	sheet_name + year_cols before we call this function
    charts_to_plot, chart_positions, worksheet, current_scenario, current_row = format_sheet_for_other_graphs(nat_gas_supply,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict, patterns_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict, current_scenario, current_row, original_table_id,NEW_SCENARIO)
    
    return charts_to_plot, chart_positions, worksheet, current_row

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
        #extract the data we want to use for the refined products graph, then do wahtever manipulations and calculations are needed to get it into the right format, then plotit
        table_id = 'energy_Buildings_1'
        buildings_demand_by_fuel = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.chart_type == 'area') ]
        if len(buildings_demand_by_fuel) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        buildings_demand_by_fuel.loc[:, 'chart_title'] = 'Buildings'
        buildings_demand_by_fuel.loc[:, 'table_id'] = original_table_id
        buildings_demand_by_fuel.loc[:, 'aggregate_name'] = 'Buildings'
        buildings_demand_by_fuel.loc[:, 'sheet_name'] = sheet
        
        buildings_demand_by_fuel.loc[:, 'chart_type'] = chart_type
        buildings_demand_by_fuel.loc[:, 'scenario'] = scenarios_list[scenario_num]
        
        ######
        table_id = 'energy_Buildings_2'
        
        #extract where plotting name is Data centres & AI. we will minus this from leectriicty in buildings_demand by fuel and show it as 'Electricity - data centres'
        data_centres = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.chart_type == 'area') & (charts_mapping['plotting_name'] == 'Data centres & AI')]
        if len(data_centres) == 0:
            breakpoint()
            raise Exception(f'No data found for table {table_id}')
        data_centres.loc[:, 'chart_title'] = 'Buildings'
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
        buildings_demand_by_fuel_wide.loc[:, 'chart_title'] = 'Buildings'
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
        return None, None, worksheet
    
    #set the order of the plotting names in the table so that data centres and electricity are plotted at the top of the cahrt.
    
    plotting_names = final_table.plotting_name.unique()
    plotting_names_order[original_table_id] =  [plotting_name for plotting_name in plotting_names if plotting_name not in ['Electricity', 'Electricity - data centres']] + ['Electricity', 'Electricity - data centres'] 
    
    
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
    
    return charts_to_plot, chart_positions, worksheet, current_row

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
    
    net_imports_final_table = pd.DataFrame()
    import_share_of_tpes_final_table = pd.DataFrame()
    max_and_min_values_dict_net_imports={}
    max_and_min_values_dict_tpes = {}
    for chart_type in chart_types:
        # breakpoint()
        #extract the data we want to use for calcaulting net imports by major fuel type and then sum up total tpes then calcualte the share of tehse. Then create a graph for the share by fuel as well as a graph for total imports. and within, do wahtever manipulations and calculations are needed to get it into the right format, then plotit
        table_id = 'energy_Trade_1'
        imports = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.chart_type == 'bar') ]
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
        table_id = 'energy_Trade_2'
        
        exports = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.chart_type == 'bar')]
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
        ##################
        
        #now grab the total TPES:
        table_id = 'energy_Supply & production_3'
        TPES = charts_mapping[(charts_mapping.table_id == table_id) & (charts_mapping.chart_type == 'area') & (charts_mapping['plotting_name'] == 'TPES')]
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
        import_share_of_tpes.loc[:, 'chart_title'] = 'Net imports share of adjusted TPES (%)'
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
        return None, None, worksheet
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
    return charts_to_plot, chart_positions, worksheet, current_row


def create_emissions_seaborn(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row, original_table_id, NEW_SCENARIO):
    """    
    """
    if 'co2e' in original_table_id:
        #use the co2e version of emissions
        if 'sector' in original_table_id:
            table_id = 'emissions_co2e_Emissions_co2e_2'
            title = 'CO2e Combustion Emissions by sector'
            plotting_name_column_name = 'Sector'
        else:
            table_id = 'emissions_co2e_Emissions_co2e_1'
            title = 'CO2e Combustion Emissions by fuel'
            plotting_name_column_name = 'Fuel'
    else:
        #use the co2 version of emissions
        if 'sector' in original_table_id:
            table_id = 'emissions_co2_Emissions_co2_2'
            title = 'CO2 Combustion Emissions by sector'
            plotting_name_column_name = 'Sector'
        else:
            table_id = 'emissions_co2_Emissions_co2_1'
            title = 'CO2 Combustion Emissions by fuel' 
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
    LINE_WIDTH = 1
    FONTSIZE = 14
    
    #extract the cols which have years in them
    year_cols = [col for col in emissions.columns if re.search(r'\d{4}', str(col))]
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    # Plot each unique fuel with its corresponding color
    
    #order them using the plotting_names_order dict
    unique_plotting_names = plotting_names_order[table_id] + [plotting_name for plotting_name in emissions[plotting_name_column_name].unique() if plotting_name not in plotting_names_order[table_id]]
    
    # Initialize a variable to keep track of the cumulative values for stacking
    cumulative_values = pd.Series([0] * len(year_cols), index=year_cols)

    for plotting_name in unique_plotting_names:
        plotting_data = emissions[emissions[plotting_name_column_name] == plotting_name].copy()
        if plotting_data.empty:
            continue
        for i, row in plotting_data.iterrows():
            values = row[year_cols]
            color = colours_dict.get(plotting_name, 'gray')
            
            # Plot net emissions as its own value, not cumulative
            if plotting_name == 'Net emissions':
                ax.plot(year_cols, values, color=color, label=plotting_name, linewidth=LINE_WIDTH)
            else:
                ax.fill_between(year_cols, cumulative_values.values.astype(float), (cumulative_values.values + values.values).astype(float), color=color, label=plotting_name)
                cumulative_values += values

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
    ax.legend(loc='center left', bbox_to_anchor=(1.2, 0.5), fontsize=FONTSIZE)
    #drop vertical gridlines
    ax.grid(axis='y')
    # Set gridlines to appear behind the charted colors
    ax.set_axisbelow(True)
    #make the chart show no gaps after  max and min years
    ax.set_xlim(min(year_cols), max(year_cols))
    #drop border around the chart
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    #set size of chart image using plotting_specs . width_inches and height_inches

    # Adjust the size of the figure to ensure everything remains visible
    fig.set_size_inches(plotting_specifications['width_inches']*1.3, plotting_specifications['height_inches'])#make width 1/3 larger to allow for legend which will be cropped out
    
    # plt.tight_layout()
    #SAVE THE CHART TO THE WORKSHEET
    # breakpoint()
    
    if 'code' in os.getcwd():
        #check file exists
        file_path = f'../intermediate_data/charts/{original_table_id}_{current_scenario}.png'
    else:
        #check file exists
        file_path = f'intermediate_data/charts/{original_table_id}_{current_scenario}.png'
    
    # Save the figure with tight bounding box
    plt.savefig(file_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    plt.clf()
    plt.close('all')
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
        PLOTTING_SEABORN=True
    )
    # breakpoint()
    # Add the image to the worksheet.. but first work out where to put it:
    worksheet.insert_image(chart_positions[0], file_path)
    
    if scenario_num == 0: #we will create an emissions wedge as well as the normal emissions chart 
        #run the wedge chart function instead, sicne most of it requries different processes but we want it in the same sheet
        charts_to_plot, chart_positions, worksheet, current_row = create_emissions_wedge_seaborn(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, patterns_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID, current_scenario, current_row, original_table_id, NEW_SCENARIO, charts_to_plot, chart_positions)
        
    return charts_to_plot, chart_positions, worksheet, current_row

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
    
    #drop net emissions from both, but check its there first
    if 'Net emissions' in emissions_base[plotting_name_column_name].unique():
        emissions_base = emissions_base[emissions_base[plotting_name_column_name] != 'Net emissions']
        emissions_new = emissions_new[emissions_new[plotting_name_column_name] != 'Net emissions']
    else:
        breakpoint()
        raise ValueError(f"Net emissions not found in emissions data. Need to update the code")
    # Compute total emissions per year for both scenarios (summing across sectors/fuels)
    total_base = emissions_base[year_cols].sum()
    total_new = emissions_new[year_cols].sum()

    # there's a slight change we have different plotting names in the two scenarios. 
    # we need to make sure we have all of them in the right order
    unique_plotting_names_base = plotting_names_order[table_id] + [
        plotting_name for plotting_name in emissions_base[plotting_name_column_name].unique() 
        if plotting_name not in plotting_names_order[table_id]
    ]
    unique_plotting_names_new = plotting_names_order[table_id] + [
        plotting_name for plotting_name in emissions_new[plotting_name_column_name].unique() 
        if plotting_name not in plotting_names_order[table_id]
    ]
    unique_plotting_names = list(set(unique_plotting_names_base + unique_plotting_names_new))

    # Instead of a single wedge fill from 0, fill from the NEW scenario line upward.
    # Group emissions data by the plotting name for each scenario:
    base_by_category = emissions_base.groupby(plotting_name_column_name)[year_cols].sum()
    new_by_category = emissions_new.groupby(plotting_name_column_name)[year_cols].sum()

    # Calculate difference in energy use for each plotting name.
    # For plotting names containing ccus/ccs/captured emissions we want to treat them differently.
    ccus_plotting_names = emissions_base[
        emissions_base[plotting_name_column_name].str.contains('ccus|ccs|captured emissions|captured_emissions', case=False, na=False)
    ][plotting_name_column_name].unique()

    # Create an empty DataFrame to hold differences.
    diff_df = pd.DataFrame()

    for plotting_name in unique_plotting_names:
        # Process only if the plotting name exists in base; and skip ccus here so we can handle them specially.
        if plotting_name in base_by_category.index and plotting_name not in ccus_plotting_names:
            base_vals = base_by_category.loc[plotting_name]
            if plotting_name not in new_by_category.index:
                raise ValueError(f"Plotting name {plotting_name} not found in {NEW_SCENARIO} scenario")
            new_vals = new_by_category.loc[plotting_name]
            diff_series = base_vals - new_vals
            
            # Find the ccus version of the plotting name, if it exists.
            ccus_match = [ccus_name for ccus_name in ccus_plotting_names if plotting_name in ccus_name]
            if ccus_match:
                
                # Subtract the captured emissions from the difference so it can be shown in the wedge. Make the captured emissions positive too
                captured_emissions = - new_by_category.loc[ccus_match[0]]
                
                diff_series = diff_series - captured_emissions
                #set the nae of the series to the plotting name
                diff_series.name = plotting_name
                diff_df = pd.concat([diff_df, captured_emissions], axis=1)
            diff_df = pd.concat([diff_df, diff_series], axis=1)
    #make sure that for all ears, the sum of diffs is equal to the difference in total emissionsbetween the two scenarios
    diff_df['wedge'] = diff_df.sum(axis=1)
    diff_df['line_diff'] = total_base - total_new
    
    if not np.allclose(diff_df['wedge'], diff_df['line_diff'], rtol=1e-2):
        breakpoint()
        # raise ValueError(f"Sum of differences in emissions does not match total difference between scenarios")
    
    #drop the line_diff and wedge cols
    diff_df = diff_df.drop(columns=['wedge', 'line_diff'])
    
    # Ensure the columns are in the desired order (using unique_plotting_names order)
    diff_df = diff_df.reindex(columns=unique_plotting_names, fill_value=0)
    ##############
    #START PLOTTING
    ##############
    # Plotting parameters
    # Plotting parameters
    LINE_WIDTH = 1
    FONTSIZE = 14

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

    # Loop over each plotting name (in the desired order) and fill the wedge.
    for plotting_name in unique_plotting_names:
        if plotting_name in diff_df.columns:
            diff_series = diff_df[plotting_name]
            y1 = cumulative_line
            y2 = cumulative_line + diff_series
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
    ax.legend(loc='center left', bbox_to_anchor=(1.2, 0.5), fontsize=FONTSIZE)
    ax.grid(axis='x')  # only horizontal grid lines
    ax.set_axisbelow(True)
    ax.set_xlim(min(year_cols), max(year_cols))

    # Remove chart borders for a clean, Excel-like look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Adjust the figure size (enlarged width to allow space for the legend)
    fig.set_size_inches(plotting_specifications['width_inches'] * 1.3,
                        plotting_specifications['height_inches'])

    # Determine file path and save the chart
    if 'code' in os.getcwd():
        file_path = f'../intermediate_data/charts/{original_table_id}_wedge.png'
    else:
        file_path = f'intermediate_data/charts/{original_table_id}_wedge.png'

    # breakpoint()#check the wedges
    plt.savefig(file_path, dpi=300, bbox_inches='tight')   
    plt.close(fig)
    plt.clf()
    plt.close('all')
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
    else:
        # breakpoint()
        # Insert the saved image into the worksheet in the second place returned by format_sheet_for_other_graphs
        worksheet.insert_image(chart_positions[1], file_path)
        
    return charts_to_plot, chart_positions, worksheet, current_row