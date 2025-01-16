
import pandas as pd
import workbook_creation_functions
from utility_functions import *
import numpy as np

def create_extra_graphs(workbook, all_charts_mapping_files_dict, total_plotting_names, MIN_YEAR,  plotting_specifications, plotting_names_order,plotting_name_to_label_dict, colours_dict, cell_format1, cell_format2, new_charts_dict, header_format, writer, EXPECTED_COLS,ECONOMY_ID):
    scenarios_list=['reference', 'target']
    #use this to create graphs that are a little more complex than the standard ones. tehse will be deisgned on a case by case basis, using explicit code.
            
    for new_chart in new_charts_dict.keys():
        source = new_charts_dict[new_chart]['source']
        sheet_name = new_charts_dict[new_chart]['sheet_name']
        function = new_charts_dict[new_chart]['function']
        chart_types = new_charts_dict[new_chart]['chart_types']
        if len(all_charts_mapping_files_dict[source]) != 1:
            raise Exception(f'Expected exactly 1 charts mapping file for create_extra_graphs() for source {source}, but found {len(all_charts_mapping_files_dict[source])}')
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
        
        workbook.add_worksheet(sheet_name)
        scenario_num = 0
        for scenario in scenarios_list:
            
            ##############
            #todo, not sure whatto do anbout diff scenarios here
            worksheet = workbook.get_worksheet_by_name(sheet_name)
            charts_mapping_scenario = charts_mapping[charts_mapping.scenario == scenario]
            charts_to_plot, chart_positions, worksheet = function(charts_mapping_scenario, sheet_name,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict, cell_format1, cell_format2, scenario_num, scenarios_list, header_format, plotting_specifications, writer, chart_types,ECONOMY_ID)
            scenario_num+=1
            worksheet = workbook_creation_functions.write_charts_to_sheet(charts_to_plot, chart_positions, worksheet)
            ###############
    workbook = workbook_creation_functions.order_sheets(workbook, plotting_specifications)
    return workbook, writer
        
def create_refined_products_bar_and_net_imports_line(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID):
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
    refined_products.loc[:, 'table_id'] = sheet
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
    postive_refined_products = refined_products[refined_products[year_cols] > 0]
    max_value_refined = postive_refined_products[year_cols].sum(axis=0).max()
    max_value_crude_oil_supply = crude_oil_supply_line.loc[crude_oil_supply_line.plotting_name.isin(['Crude production', 'Crude exports', 'Crude imports']), year_cols].max().max()
    max_value = max(max_value_refined, max_value_crude_oil_supply) 
    max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
        
    key_max_line = (sheet, 'line', sheet, "max")
    key_max_bar = (sheet, 'bar', sheet, "max")
    key_max_bar_line = (sheet, 'combined_line_bar', sheet, "max")
    #the min value will be the min of the sum of the NEGATIVE refined products and the min of the net imports:#first melt, then filter and then group by and sum
    negative_refined_products = refined_products[refined_products[year_cols] < 0]
    min_value_refined = negative_refined_products[year_cols].sum(axis=0).min()
    min_value_crude_oil_supply = crude_oil_supply_line.loc[crude_oil_supply_line.plotting_name.isin(['Crude production', 'Crude exports', 'Crude imports']), year_cols].min().min()
    min_value = min(min_value_refined, min_value_crude_oil_supply) 
    min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
        
    key_min_line = (sheet, 'line', sheet, "min")
    key_min_bar = (sheet, 'bar', sheet, "min")
    key_min_bar_line = (sheet, 'combined_line_bar', sheet, "min")
    
    max_and_min_values_dict[key_max_line] = max_value
    max_and_min_values_dict[key_max_bar] = max_value
    max_and_min_values_dict[key_min_line] = min_value
    max_and_min_values_dict[key_min_bar] = min_value
    max_and_min_values_dict[key_max_bar_line] = max_value
    max_and_min_values_dict[key_min_bar_line] = min_value
    ##################
    
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(charts_mapping, colours_dict)
    plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, plotting_name_to_label_dict)
    
    unit_dict = {sheet: 'PJ'}
    
    charts_to_plot, chart_positions, worksheet = format_sheet_for_other_graphs(refined_products_and_net_imports,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict)
    
    return charts_to_plot, chart_positions, worksheet


def format_sheet_for_other_graphs(refined_products_and_net_imports,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet,workbook, plotting_specifications, writer, sheet, colours_dict, cell_format1, cell_format2, max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID,unit_dict):
    #########################
    table, chart_types_unused, table_id, plotting_name_column, year_cols_start,num_cols, chart_titles, first_year_col, sheet_name = workbook_creation_functions.format_table(refined_products_and_net_imports,plotting_names_order,plotting_name_to_label_dict)
    
    if len(chart_types) == 1 and 'bar' in chart_types and not sheet == 'CO2 emissions components':   
        table = workbook_creation_functions.create_bar_chart_table(table,year_cols_start,plotting_specifications['bar_years'], sheet_name)
    #########################
    column_row = 1
    space_under_tables = 1
    space_above_charts = 1
    space_under_charts = 1
    space_under_titles = 1
    
    #calcualte current row using the table times the scenario number
    num_table_rows = table.shape[0]
    if scenario_num == 0:
        current_row = 1
        current_scenario = ''#for seom reason we have to do this? my bad lol
    else:#add space as if we have already done this
        current_scenario = scenarios_list[scenario_num - 1]#technical detail just to make add_section_titles work as expected. - it got removed in format_table but it wasnt set right anyway
        current_row = num_table_rows * scenario_num + space_under_tables + column_row + space_above_charts + space_under_charts + plotting_specifications['height'] + 1
    table['scenario'] = scenarios_list[scenario_num]# - it got removed in format_table 
    current_row, current_scenario, worksheet = workbook_creation_functions.add_section_titles(current_row, current_scenario, sheet, worksheet, cell_format1, cell_format2, space_under_titles, table, space_under_tables,unit_dict, ECONOMY_ID)
    
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
    
    charts_to_plot = workbook_creation_functions.create_charts(table, chart_types, plotting_specifications, workbook, num_table_rows, plotting_name_column, table_id, sheet, current_row, space_under_tables, column_row, year_cols_start, num_cols, colours_dict,total_plotting_names, max_and_min_values_dict, chart_titles, first_year_col, sheet_name)

    return charts_to_plot, chart_positions, worksheet


def create_refining_and_low_carbon_fuels(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID):
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
        refined_products.loc[:, 'table_id'] = sheet
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
        low_carbon_fuels.loc[:, 'table_id'] = sheet
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
        max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
            
        key_max = (sheet, chart_type, sheet, "max")
        
        min_value = 0#refined_products_and_low_carbon_fuels[year_cols].min().min()
        min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
            
        key_min = (sheet, chart_type, sheet, "min")
        
        max_and_min_values_dict[key_max] = max_value
        max_and_min_values_dict[key_min] = min_value
        
        ##################
        final_table = pd.concat([final_table, refined_products_and_low_carbon_fuels])
        ##################
    
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(refined_products_and_low_carbon_fuels, colours_dict)
    
    plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, plotting_name_to_label_dict)
    
    unit_dict = {sheet: 'PJ'}
    
    charts_to_plot, chart_positions, worksheet = format_sheet_for_other_graphs(refined_products_and_low_carbon_fuels,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict)
    
    return charts_to_plot, chart_positions, worksheet

def create_liquid_biofuels_and_bioenergy_supply_charts(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID):
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
        liquid_biofuels_supply.loc[:, 'table_id'] = sheet
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
        bioenergy_supply.loc[:, 'table_id'] = sheet
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
        
        max_value = bioenergy_supply[year_cols].sum(axis=0).max()
        max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
            
        key_max = (sheet, chart_type, sheet, "max")
        
            
        #the min value will be the min of the sum of the NEGATIVE refined products and the min of the net imports:#first melt, then filter and then group by and sum
        non_year_cols = [col for col in bioenergy_supply.columns if col not in year_cols]
        negatives = bioenergy_supply.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        #filter
        negatives = negatives[negatives['value'] < 0]
        #group by and sum
        negatives = negatives.groupby(['year'])['value'].sum().reset_index()
        min_value = negatives.value.min()
        min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
                    
        key_min = (sheet, chart_type, sheet, "min")
        
        max_and_min_values_dict[key_max] = max_value
        max_and_min_values_dict[key_min] = min_value
        
        ##################
        final_table = pd.concat([final_table, bioenergy_supply])
        ##################
    
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(bioenergy_supply, colours_dict)
    
    plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, plotting_name_to_label_dict)
    
    unit_dict = {sheet: 'PJ'}
    
    charts_to_plot, chart_positions, worksheet = format_sheet_for_other_graphs(bioenergy_supply,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict)
    
    return charts_to_plot, chart_positions, worksheet


def create_natural_gas_and_lng_supply_charts(charts_mapping, sheet,plotting_names_order,plotting_name_to_label_dict, worksheet,workbook,  colours_dict,cell_format1, cell_format2,  scenario_num,scenarios_list, header_format,plotting_specifications, writer, chart_types,ECONOMY_ID):
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
        lng_supply.loc[:, 'table_id'] = sheet
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
        nat_gas_supply.loc[:, 'table_id'] = sheet
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
        max_value = workbook_creation_functions.calculate_y_axis_value(max_value)
            
        key_max = (sheet, chart_type, sheet, "max")
        
            
        #the min value will be the min of the sum of the NEGATIVE refined products and the min of the net imports:#first melt, then filter and then group by and sum
        negatives = nat_gas_supply.melt(id_vars=non_year_cols, value_vars=year_cols, var_name='year', value_name='value').copy()
        #filter
        negatives = negatives[negatives['value'] < 0]
        #group by and sum
        negatives = negatives.groupby(['year'])['value'].sum().reset_index()
        min_value = negatives.value.min()
        min_value = workbook_creation_functions.calculate_y_axis_value(min_value)
                    
        key_min = (sheet, chart_type, sheet, "min")
        
        max_and_min_values_dict[key_max] = max_value
        max_and_min_values_dict[key_min] = min_value
        
        ##################
        final_table = pd.concat([final_table, nat_gas_supply])
        ##################
    
    colours_dict = workbook_creation_functions.check_plotting_names_in_colours_dict(nat_gas_supply, colours_dict)
    
    plotting_name_to_label_dict = workbook_creation_functions.check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, plotting_name_to_label_dict)
    
    unit_dict = {sheet: 'PJ'}
    
    charts_to_plot, chart_positions, worksheet = format_sheet_for_other_graphs(nat_gas_supply,plotting_names_order,plotting_name_to_label_dict, scenario_num, scenarios_list, header_format, worksheet, workbook, plotting_specifications, writer, sheet, colours_dict,cell_format1, cell_format2,  max_and_min_values_dict, total_plotting_names, chart_types, ECONOMY_ID, unit_dict)
    
    return charts_to_plot, chart_positions, worksheet

