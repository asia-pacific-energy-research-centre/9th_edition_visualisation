import time
import uuid
import pandas as pd
import math
import numpy as np
import ast
import os
import shutil
from utility_functions import *
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import random
from matplotlib.lines import Line2D
import create_legend
def create_sheets_from_mapping_df(workbook, charts_mapping_df, total_plotting_names, MIN_YEAR, colours_dict, patterns_dict, cell_format1, cell_format2, header_format, plotting_specifications, plotting_names_order, plotting_name_to_label_dict, writer, EXPECTED_COLS, ECONOMY_ID): 
    #PREPARE DATA ########################################
    charts_mapping = charts_mapping_df.copy()
    #filter for MIN_YEAR
    charts_mapping = charts_mapping.loc[charts_mapping['year'].astype(int) >= MIN_YEAR].copy()
    # If chart_title is Passenger stock shares or Freight stock shares, round the values to 3 decimal places instead of 1
    if charts_mapping['chart_title'].isin(['Passenger stock shares', 'Freight stock shares']).any():
        charts_mapping['value'] = charts_mapping['value'].round(3).copy()
    else:
        #make values 1 decimal place
        charts_mapping['value'] = charts_mapping['value'].round(1).copy()
    # Replace NaNs with 0 except for 'Transport stocks', 'Transport activity' and 'Intensity' sheets
    mask = ~charts_mapping['sheet_name'].isin(['Transport stocks', 'Transport activity', 'Indicators'])
    charts_mapping.loc[mask, 'value'] = charts_mapping.loc[mask, 'value'].fillna(0).copy()
    ########################################
    #Addition to handle transport capacity data not having data from before the base year. It sets the data from the base year as the data for all years before the base year. This is a pretty quick hack but unnoticable in the final output, as long as there is onyl 1 or 2 years before the base year.
    #double check there are only 1 or 2 years before the base year
    if len(charts_mapping[charts_mapping['sheet_name'].isin(['Transport stocks', 'Transport activity'])]) > 0:
        years_less = charts_mapping[(charts_mapping['year'].astype(int) < OUTLOOK_BASE_YEAR-2)].copy()
        if len(years_less['year'].unique()) > 2:
            #drop years that areless than 2 years before the base year
            charts_mapping = charts_mapping[~((charts_mapping['year'].isin(years_less['year'].unique()) & (charts_mapping['sheet_name'].isin(['Transport stocks', 'Transport activity']))))].copy()
            # breakpoint()
            # raise Exception('There are more than 2 years before the base year. This is not expected. Please check the data')
        
        mask2 = (charts_mapping['sheet_name'].isin(['Transport stocks', 'Transport activity'])) & (charts_mapping['year'].astype(int) < OUTLOOK_BASE_YEAR)
        mask3 = (charts_mapping['sheet_name'].isin(['Transport stocks', 'Transport activity'])) & (charts_mapping['year'].astype(int) == OUTLOOK_BASE_YEAR)
        # Replace 0s with the data from the OUTLOOK_BASE_YEAR for 'Transport stocks', 'Transport activity' only for years before OUTLOOK_BASE_YEAR.
        EXPECTED_COLS_no_year = EXPECTED_COLS.copy()
        EXPECTED_COLS_no_year.remove('year')
        EXPECTED_COLS_no_year.remove('value')
        df_to_merge = charts_mapping.loc[mask3].copy()
        
        # Perform the merge
        charts_mapping = pd.merge(charts_mapping, df_to_merge, on=EXPECTED_COLS_no_year, how='left', suffixes=('', '_y'))
        
        #where mask2 is true, replace the value with the value from the base year
        charts_mapping.loc[(charts_mapping['sheet_name'].isin(['Transport stocks', 'Transport activity'])) & (charts_mapping['year'].astype(int) < OUTLOOK_BASE_YEAR), 'value'] = charts_mapping.loc[(charts_mapping['sheet_name'].isin(['Transport stocks', 'Transport activity'])) & (charts_mapping['year'].astype(int) < OUTLOOK_BASE_YEAR), 'value_y']
        # Drop the unnecessary columns 
        charts_mapping.drop(columns=[col for col in charts_mapping.columns if '_y' in col], inplace=True)
    
    # Additional code to handle Electricity sheet
    if 'Electricity demand' in charts_mapping['sheet_name'].unique():
        electricity_sheet_mask = charts_mapping['sheet_name'] == 'Electricity demand'
        charts_mapping.loc[electricity_sheet_mask, 'unit'] = 'TWh'
        charts_mapping.loc[electricity_sheet_mask, 'value'] = (charts_mapping.loc[electricity_sheet_mask, 'value'].astype(float) / 3.6).round(1)
    ########################################
    # Getting the max values for each sheet and chart type to make the charts' y-axis consistent
    max_and_min_values_dict = {}
    max_and_min_values_dict = extract_max_and_min_values(charts_mapping, max_and_min_values_dict, total_plotting_names, plotting_specifications)
    
    colours_dict = check_plotting_names_in_colours_dict(charts_mapping, colours_dict)
    patterns_dict = check_plotting_names_in_patterns_dict(patterns_dict)
    plotting_name_to_label_dict = check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict)

    #so firstly, extract the unique sheets we will create:
    sheets = charts_mapping['sheet_name'].unique()
    
    #create a unit dictionary to map units to the correct sheet, if there are multiple units per sheet then concatenate them 
    # #NOTE THAT THIS DOESNT WORK WITH THE WAY UNITS ARE IMPLEMENTED IN THE CHARTS MAPPING, BUT THE ITNENTION IS THAT ONCE WE START PLOTTING DIFFERENT UNITS THEN THIS WILL BE SOLVED IN THE CHARTS MAPPING, NOT HERE (SO THIS CODE WILL STAY THE SAME)
    unit_dict = charts_mapping[['sheet_name','unit']].drop_duplicates().groupby('sheet_name')['unit'].apply(lambda x: ', '.join(x)).to_dict() #TODO

    # # Custom order list #TODO custom order of sheets? 
    # custom_order = ['Buildings', 'Industry', 'Transport', 'Agriculture', 'Non-energy', 'TFC by fuel', 'Fuel consumption power sector', 'Refining']

    # # Sort the sheets according to the custom order
    # sheets = sorted(sheets, key=lambda x: custom_order.index(x) if x in custom_order else len(custom_order))

    #then create a dictionary of the sheets and the dataframes we will use to populate them:
    sheet_dfs = {}
    for sheet in sheets:
        sheet_dfs[sheet] = ()

        sheet_data = charts_mapping.loc[charts_mapping['sheet_name'] == sheet]

        # Pivot the data and create an order of cols so it is faster to create tables
        EXPECTED_COLS_wide = EXPECTED_COLS.copy()
        EXPECTED_COLS_wide.remove('year')
        EXPECTED_COLS_wide.remove('value')
        
        try:
            sheet_data = sheet_data.pivot(index=EXPECTED_COLS_wide, columns='year', values='value')
        except Exception as e:
            #check for duplicates
            if sheet_data.duplicated(subset=EXPECTED_COLS_wide+['year']).any():
                dupes = sheet_data[sheet_data.duplicated(subset=EXPECTED_COLS_wide+['year'])]
            breakpoint()
            raise Exception('There are duplicates in the data. Please check the data. Duplicates:', dupes)
        # #potentially here we get nas from missing years for certain rows, so replace with 0
        # sheet_data = sheet_data.fillna(0)#decided against it because it seems the nas are useful
        sheet_data = sheet_data.reset_index()

        #sort by table_number
        sheet_data = sheet_data.sort_values(by=['table_number'])
        # for scenario in sheet_data['scenario'].unique():
        #     if str(scenario) == 'nan':
        #         scenario_data = sheet_data.copy()
        #     else:   
        #         #extract scenario data
        #         scenario_data = sheet_data.loc[(sheet_data['scenario'] == scenario)]
        #     #add tables to tuple, by table number
        #     for table in scenario_data['table_number'].unique():
        #         table_data = scenario_data.loc[(scenario_data['table_number'] == table)]
        #         #drop table number from table data
        #         table_data = table_data.drop(columns = ['table_number'])

        #         #add table data to tuple
        #         sheet_dfs[sheet] = sheet_dfs[sheet] + (table_data,)
        if sheet in ['Indicators']:
            # Handle all data as one scenario block for "Intensity" or "Renewables share" sheet
            for table in sheet_data['table_number'].unique():
                table_data = sheet_data.loc[(sheet_data['table_number'] == table)]
                table_data = table_data.drop(columns=['table_number'])
                # Update 'plotting_name' based on 'scenario' values
                table_data['plotting_name'] = table_data['scenario'].apply(lambda x: x.capitalize() if x in ['reference', 'target'] else table_data['plotting_name'])
                sheet_dfs[sheet] = sheet_dfs[sheet] + (table_data,)
        else:
            # Process each scenario individually for other sheets (sorted alphabetically)
            for scenario in sorted(sheet_data['scenario'].unique().tolist()):
                if str(scenario) == 'nan':
                    scenario_data = sheet_data.copy()
                else:
                    scenario_data = sheet_data.loc[(sheet_data['scenario'] == scenario)]

                for table in scenario_data['table_number'].unique():
                    table_data = scenario_data.loc[(scenario_data['table_number'] == table)]
                    table_data = table_data.drop(columns=['table_number'])
                    sheet_dfs[sheet] = sheet_dfs[sheet] + (table_data,)
    #PREPARE DATA END  ########################################
    #now we have a dictionary of dataframes for each sheet, we can iterate through them and create the charts and tables we need.
    #every table has the format (var might change)
    # EXPECTED_COLS = ['source', 'table_number', 'chart_type','plotting_name', 'plotting_name_column','aggregate_name', 'aggregate_name_column', 'scenario', 'unit', 'table_id', 'dimensions', 'chart_title', 'year', 'value','sheet_name']

    #iterate through the sheets and create them
    for sheet in sheets:
        # if sheet == 'Production':
        #     breakpoint()#checkingw why production has negative bvlaues
        #create sheet in workbook
        try:
            workbook.add_worksheet(sheet)
        except Exception as e:
            print('Error adding sheet', sheet, 'to workbook. Error:', e)
            breakpoint()
            workbook.add_worksheet(sheet)
        worksheet = workbook.get_worksheet_by_name(sheet)

        space_under_tables = 1
        space_above_charts = 5# I THINK THIS NEEDS TO BE 1 LESS THAN space_under_charts ALWAYS. Think its because when u increase size of chart it increases the space it takes up equally upwards as downwards. 
        space_under_charts = 6
        space_under_titles = 1
        column_row = 1
        current_scenario = ''
    
        current_row = 0
        for table in sheet_dfs[sheet]:
            
            dimensions = table['dimensions'].unique()[0]
            if len(table['dimensions'].unique()) > 1:
                raise Exception('we should only have one dimension type per table') 
            ########################
            current_row, current_scenario, worksheet = add_section_titles(current_row, current_scenario, sheet, worksheet, cell_format1, cell_format2, space_under_titles, table, space_under_tables,unit_dict, ECONOMY_ID)
            ########################
            table, chart_types, table_id, plotting_name_column, year_cols_start,num_cols, chart_titles, first_year_col, sheet_name = format_table(table,plotting_names_order,plotting_name_to_label_dict)
            
            try:
                # Try to convert 'first_year_col' to an integer and use it
                first_year_col = int(first_year_col)
            except ValueError:
                # If conversion fails, default to MIN_YEAR
                first_year_col = MIN_YEAR
            
            #make the cols for plotting_name_column and the one before it a bit wider so the text fits
            plotting_name_column_index = table.columns.get_loc(plotting_name_column)
            aggregate_name_column_index = plotting_name_column_index - 1
            worksheet.set_column(plotting_name_column_index, plotting_name_column_index, 20)
            if dimensions == '2D':
                worksheet.set_column(aggregate_name_column_index, aggregate_name_column_index, 20)
            ########################
            #now start adding the table and charts
            #find out if there is at least a chart for this table, in which case we need to space the table down by the height of the chart (we will add cahrt after adding table because we use the details of where the table is before adding chart)
            if len(chart_types) > 0:
                current_row += plotting_specifications['height']

            worksheet.set_row(current_row, None, header_format)
            ########################
            #if chart_type len is 1 and it is a bar chart, we need to edit the table to work for bar charts:
            
            if len(chart_types) == 1 and 'bar' in chart_types and not sheet == 'CO2 emissions components':   
                table = create_bar_chart_table(table,year_cols_start,plotting_specifications['bar_years'], sheet_name)
            ########################
            # Define the mapping dictionary
            column_mapping_combined_kaya = {
                3000: f'Emissions {OUTLOOK_BASE_YEAR}',
                3001: 'Population',
                3002: 'GDP per capita',
                3003: 'Intensity REF',
                3004: f'Emissions {OUTLOOK_LAST_YEAR} REF',
                3005: 'Intensity TGT',
                3006: f'Emissions {OUTLOOK_LAST_YEAR} TGT',
                
            }
            column_mapping_kaya = {
                3000: f'Emissions {OUTLOOK_BASE_YEAR}',
                3001: 'Population',
                3002: 'GDP per capita',
                3003: 'Energy intensity',
                3004: 'Emissions intensity',
                3005: f'Emissions {OUTLOOK_LAST_YEAR}'
            }
            
            # If sheet is CO2 emissions components, rename the years
            if sheet == 'CO2 emissions components':
                #check if the plotting name contains combined (e.g. rise_combined) or not then apply the combined or kaya mapping:
                # breakpoint()
                if 'combined' in table[plotting_name_column].iloc[0]:
                    # Rename the columns using the mapping dictionary
                    table.rename(columns=column_mapping_combined_kaya, inplace=True)
                else:
                    # Rename the columns using the mapping dictionary
                    table.rename(columns=column_mapping_kaya, inplace=True)
                    #drop 3006 drom the table
                    table = table.drop(columns=[3006], errors='ignore')
                #need to reset the year_cols_start (it wasnt correct before either)
                year_cols_start = table.columns.get_loc(f'Emissions {OUTLOOK_BASE_YEAR}')
                
            ########################
            #write table to sheet
            table.to_excel(writer, sheet_name = sheet, index = False, startrow = current_row)
            current_row += len(table.index) + space_under_tables + column_row
            num_table_rows = len(table.index)
            ######################## 
            # breakpoint()#do we have access to colors and labelshere and can we create legends here?
            #identify and format charts we need to create
            chart_positions = identify_chart_positions(current_row,num_table_rows,space_under_tables,column_row, space_above_charts, space_under_charts, plotting_specifications,chart_types)
            # print('max_and_min_values_dict', max_and_min_values_dict, 'for sheet', sheet)
            # breakpoint()#do we have access to a charts type map?
            worksheet = create_legend.create_legend(colours_dict, patterns_dict, plotting_name_column, table,plotting_specifications, chart_positions, worksheet,ECONOMY_ID,total_plotting_names,chart_types)
            
            charts_to_plot = create_charts(table, chart_types, plotting_specifications, workbook,num_table_rows, plotting_name_column, table_id, sheet, current_row, space_under_tables, column_row, year_cols_start, num_cols, colours_dict, patterns_dict,total_plotting_names, max_and_min_values_dict, chart_titles, first_year_col, sheet_name)
            ########################

            #write charts to sheet
            worksheet = write_charts_to_sheet(charts_to_plot, chart_positions, worksheet)
                        
            # #create a copy of the writer and try to close it, if it fails we set breakpoitn so we can see what is going on
            # try:
            #     writer.close()
            # except:
            #     breakpoint()
            #     print('writer close failed')
            
            
    workbook = order_sheets(workbook, plotting_specifications)
    # breakpoint()
    return workbook, writer, colours_dict

def add_section_titles(current_row, current_scenario, sheet, worksheet, cell_format1, cell_format2, space_under_titles, table, space_under_tables,unit_dict, ECONOMY_ID, NEW_SCENARIO=False):
    
    if current_scenario == '':
        #this is the first table. we will also use this opportunity to add the title of the sheet:
        current_scenario = table['scenario'].iloc[0]
        worksheet.write(0, 0, ECONOMY_ID, cell_format1)
        worksheet.write(1, 0, sheet, cell_format1)
        if str(current_scenario) != 'nan':
            worksheet.write(2, 0, current_scenario.capitalize(), cell_format1)
        unit = unit_dict[sheet]
        worksheet.write(1, 0, unit, cell_format2)
        current_row += 2
    elif table['scenario'].iloc[0] != current_scenario or NEW_SCENARIO:
        #New scenario. Add scenario title to next line and then carry on
        current_scenario = table['scenario'].iloc[0]
        #if scenario is na then dont add it
        current_row += 2
        worksheet.write(current_row, 0, ECONOMY_ID, cell_format1)
        worksheet.write(current_row+1, 0, sheet, cell_format1)
        if str(current_scenario) != 'nan':
            worksheet.write(current_row+2, 0, current_scenario.capitalize(), cell_format1)
        current_row += space_under_titles                
    else:
        #add one line space between tables of same scenario
        current_row += space_under_tables
    return current_row, current_scenario, worksheet
    
def prepare_workbook_for_all_charts(ECONOMY_ID, FILE_DATE_ID):
    # Set the path for the economy folder
    economy_folder = '../output/output_workbooks/' + ECONOMY_ID

    # Check if the folder for the economy exists
    if not os.path.exists(economy_folder):
        os.makedirs(economy_folder)  # If not, create it
    else:
        # If it exists, check if there is an 'old' folder within it
        old_folder = os.path.join(economy_folder, 'old')
        if not os.path.exists(old_folder):
            os.makedirs(old_folder)  # If not, create it

        for file_name in os.listdir(economy_folder):
            if file_name != 'old':  # Avoid moving the 'old' folder
                file_path = os.path.join(economy_folder, file_name)
                old_file_path = os.path.join(old_folder, file_name)
                
                # If the file already exists in the 'old' folder, remove it
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                    
                # Then move the file to the 'old' folder
                shutil.move(file_path, old_folder)

    writer = pd.ExcelWriter(os.path.join(economy_folder, ECONOMY_ID + '_charts_' + FILE_DATE_ID + '.xlsx'), engine='xlsxwriter')
    workbook = writer.book
    #format the workbook
    # Comma format and header format    #NOTE I DONT KNOW IF ACTUALLY IMPLEMEMNTED all of THESE BUT THEY COULD BE USEFUL!    #TODO THESE SPECS SHOULD PROBABLY BE RECORDED IN A MORE OFFICAL LOCATIO
    space_format = workbook.add_format({'num_format': '# ### ### ##0.0;-# ### ### ##0.0;-'})
    percentage_format = workbook.add_format({'num_format': '0.0%'})
    header_format = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'bold': True})
    cell_format1 = workbook.add_format({'bold': True})
    cell_format2 = workbook.add_format({'font_size': 9})
    # cell_format3 = workbook.add_format({'font_size': 9, 'bold': True, 'underline': True})

    return workbook, writer, space_format, percentage_format, header_format, cell_format1, cell_format2

def extract_max_and_min_values(data, max_and_min_values_dict, total_plotting_names, plotting_specifications):

    unique_sheets = data['sheet_name'].unique()
    unique_chart_types = data['chart_type'].unique()
    unique_table_ids = data['table_id'].unique()

    for sheet in unique_sheets:
        for chart_type in unique_chart_types:
            for table_id in unique_table_ids:
                subset = data[
                    (data['sheet_name'] == sheet) &
                    (data['chart_type'] == chart_type) &
                    (data['table_id'] == table_id)
                ].copy()
                if subset.empty:
                    continue
                #set value to 0 where plotting name is one of the total plotting names. This is so that the max/min y value is not affected by the total plotting names, since they arent plotted 
                subset.loc[subset['plotting_name'].isin(total_plotting_names), 'value'] = 0
                
                # if chart_type is combined, set value to 0 where plotting name is in plotting_specifications['combined_line_bar_chart_lines_plotting_names']
                if chart_type == 'combined_line_bar':
                    subset.loc[subset['plotting_name'].isin(plotting_specifications['combined_line_bar_chart_lines_plotting_names']), 'value'] = 0

                # if subset.aggregate_name_column.iloc[0] == 'fuels_plotting':
                #     subset.loc[subset['plotting_name_column'].isin(total_plotting_names), 'value'] = 0
                # elif subset.aggregate_name_column.iloc[0] == 'sectors_plotting':
                #     subset.loc[subset.plotting_name_column.isin(total_plotting_names), 'value'] = 0
                # elif subset.aggregate_name_column.iloc[0] == 'emissions_sectors_plotting':
                #     subset.loc[subset['plotting_name_column'].isin(total_plotting_names), 'value'] = 0 #TODO i think we might have issues with duplicated plotting namesbetweensources. perhaps need to use the id?
                # elif subset.aggregate_name_column.iloc[0] == 'emissions_fuels_plotting':
                #     subset.loc[subset['plotting_name_column'].isin(total_plotting_names), 'value'] = 0 #TODO i think we might have issues with duplicated plotting namesbetweensources. perhaps need to use the id?
                # elif subset.aggregate_name_column.iloc[0] == 'capacity_plotting':
                #     # subset.loc[subset['capacity_plotting'].isin(total_plotting_names), 'value'] = 0 #TODO i think we might have issues with duplicated plotting namesbetweensources. perhaps need to use the id?
                #     pass# i dont think we need to do anything here
                    
                postive_values = subset[subset['value'] >= 0].copy()
                negative_values = subset[subset['value'] <= 0].copy()
                if len(postive_values) > 0:
                    max_value = postive_values.groupby(['year', 'scenario'])['value'].sum().max()
                    if chart_type == 'line':#we dont want to sum the values for line charts
                        max_value = postive_values['value'].max()
                else:
                    max_value = 0
                if len(negative_values) > 0:
                    min_value = negative_values.groupby(['year', 'scenario'])['value'].sum().min()
                    if chart_type == 'line':#we dont want to sum the values for line charts
                        min_value = negative_values['value'].min()
                else:
                    min_value = 0

                if chart_type == 'area' and min_value < 0 and max_value > 0:
                    #area plots dont really work when we have negative and positive values. so let user know but dont raise an error
                    print('WARNING: Area chart for ' + sheet + ' with table_id ' + str(table_id) + ' has both negative and positive values. This will not work well. Please consider changing the chart type to line or bar')
                        
                # Calculate max y-axis value for the chart
                if max_value is not None and not np.isnan(max_value):
                    if max_value == 0:
                        y_axis_max = 0
                    elif max_value > 0:
                        y_axis_max = calculate_y_axis_value(max_value)
                    else:
                        y_axis_max = None
                    key_max = (sheet, chart_type, table_id, "max")
                    max_and_min_values_dict[key_max] = y_axis_max

                # Calculate min y-axis value for the chart
                if min_value is not None and not np.isnan(min_value):
                    if min_value == 0:
                        y_axis_min = 0
                    elif min_value < 0:
                        y_axis_min = calculate_y_axis_value(min_value)
                    else:
                        y_axis_min = None
                    key_min = (sheet, chart_type, table_id, "min")
                    max_and_min_values_dict[key_min] = y_axis_min

    # Remove items with None values
    max_and_min_values_dict = {k: v for k, v in max_and_min_values_dict.items() if v is not None}

    return max_and_min_values_dict

def calculate_y_axis_value(value):
    # Adjust the value by 5% in the appropriate direction
    if value > 0:
        y_axis_value = value + (0.05 * value)
    else:
        y_axis_value = value - (0.1 * abs(value))

    # Use absolute value to handle the logarithm for negatives
    if y_axis_value != 0:
        try:
            order_of_magnitude = 10 ** math.floor(math.log10(abs(y_axis_value)))
            rounding_step = order_of_magnitude / 2

            # If the value is positive, round up. If negative, round down.
            if y_axis_value > 0:
                y_axis_value = math.ceil(y_axis_value / rounding_step) * rounding_step
            else:
                y_axis_value = math.floor(y_axis_value / rounding_step) * rounding_step
        
        except OverflowError:
            breakpoint()#why si this occurring
            raise Exception('Overflow error when calculating y_axis_value. This is not expected. Please check the data')

    return y_axis_value

def create_charts(table, chart_types, plotting_specifications, workbook, num_table_rows, plotting_name_column, table_id, sheet, current_row, space_under_tables, column_row, year_cols_start, num_cols, colours_dict, patterns_dict, total_plotting_names, max_and_min_values_dict, chart_titles, first_year_col, sheet_name):
    
    colours_dict = check_plotting_names_in_colours_dict(table, colours_dict, plotting_name_column=plotting_name_column)
    patterns_dict = check_plotting_names_in_patterns_dict(patterns_dict)
    # Depending on the chart type, create different charts. Then add them to the worksheet according to their positions
    charts_to_plot = []
    plotting_name_column_index = table.columns.get_loc(plotting_name_column)
    
    for i, chart in enumerate(chart_types):
        chart_title = chart_titles[0]
        # Get the y_axis_max from max_and_min_values_dict by including the table_id in the key
        # if table_id == 'Industry_3':
        #     breakpoint()
        # If chart_title is Passenger stock shares or Freight stock shares, set y_axis_max to 100
        if chart_title in ['Passenger stock shares', 'Freight stock shares']:
            y_axis_max = 100
        else:
            y_axis_max = max_and_min_values_dict.get((sheet, chart, table_id, "max"))
        y_axis_min = max_and_min_values_dict.get((sheet, chart, table_id, "min"))
        if y_axis_max is None:
            continue  # Skip the chart creation if y_axis_max is None
        if y_axis_min is None:
            raise Exception("y_axis_min is None. We werent expecting this. perhaps its ok but need to check")
        if chart == 'line':
            # Configure the chart with the updated y_axis_max
            line_chart = line_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min, first_year_col)
            line_thickness = plotting_specifications['line_thickness']
            line_chart = create_line_chart(num_table_rows, table, plotting_name_column, sheet, current_row, space_under_tables, column_row, plotting_name_column_index, year_cols_start, num_cols, colours_dict, patterns_dict, line_chart, total_plotting_names, line_thickness, table_id, chart_title)
            if not line_chart:
                continue
            charts_to_plot.append(line_chart)

        elif chart == 'area':
            # Configure the chart with the updated y_axis_max, y_axis_min
            area_chart = area_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min, first_year_col)
            area_chart = create_area_chart(num_table_rows, table, plotting_name_column, sheet, current_row, space_under_tables, column_row, plotting_name_column_index, year_cols_start, num_cols, colours_dict, patterns_dict, area_chart, total_plotting_names, table_id, chart_title)
            if not area_chart:
                continue
            charts_to_plot.append(area_chart)

        elif chart == 'bar':
            # Configure the chart with the updated y_axis_max and y_axis_min
            bar_chart = bar_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min, sheet_name)
            bar_chart = create_bar_chart(num_table_rows, table, plotting_name_column, sheet, current_row, space_under_tables, column_row, plotting_name_column_index, year_cols_start, len(table.columns), colours_dict, patterns_dict, bar_chart, total_plotting_names, table_id, chart_title)
            if not bar_chart:
                continue
            charts_to_plot.append(bar_chart)

        elif chart == 'combined_line_bar':
            
            primary_chart, secondary_chart = combined_line_bar_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min, first_year_col)
            line_thickness = plotting_specifications['line_thickness']
            combined_chart = create_combined_line_bar_chart(num_table_rows, table, plotting_name_column, sheet, current_row,space_under_tables,column_row, plotting_name_column_index, year_cols_start, num_cols, colours_dict, patterns_dict, primary_chart, secondary_chart, total_plotting_names, line_thickness, table_id, chart_title, plotting_specifications)
            if not combined_chart:
                continue
            charts_to_plot.append(combined_chart)

        elif chart == 'percentage_bar':
            
            percentage_bar_chart = percentage_bar_plotting_specifications(workbook, plotting_specifications)
            percentage_bar_chart = create_percentage_bar_chart(num_table_rows, table, plotting_name_column, sheet, current_row, space_under_tables, column_row, plotting_name_column_index, year_cols_start, num_cols, colours_dict, patterns_dict, percentage_bar_chart, total_plotting_names, table_id, chart_title)
            if not percentage_bar_chart:
                continue
            charts_to_plot.append(percentage_bar_chart)
        # elif chart == 'combined_line_bar':
        #     bar_chart = bar_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min, sheet_name)
        #     line_chart = line_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min, first_year_col)
            
        #     combined_chart = combine_bar_and_line_chart_specs(workbook, bar_chart, line_chart, plotting_specifications)
            
        #     combined_chart = create_combined_bar_and_line_chart(num_table_rows, table, plotting_name_column, sheet, current_row, space_under_tables, column_row, plotting_name_column_index, year_cols_start, num_cols, colours_dict, patterns_dict, bar_chart, line_chart, total_plotting_names, plotting_specifications['line_thickness'], table_id, chart_title)
            
        #     charts_to_plot.append(combined_chart)
            
    return charts_to_plot



# def prepare_bar_chart_table_and_chart(table,year_cols_start, plotting_specifications, workbook, num_table_rows, plotting_name_column, sheet, current_row,space_under_tables, column_row, colours_dict, patterns_dict,writer,charts_to_plot,total_plotting_names):
#     plotting_name_column_index = table.columns.get_loc(plotting_name_column)
    
#     bar_chart_table = create_bar_chart_table(table,year_cols_start,plotting_specifications['bar_years'])
    
#     bar_chart_table.to_excel(writer, sheet_name = sheet, index = False, startrow = current_row)
#     current_row += len(bar_chart_table.index) + space_under_tables + column_row

#     bar_chart = bar_plotting_specifications(workbook,plotting_specifications)
#     bar_chart = create_bar_chart(num_table_rows, table, plotting_name_column, sheet, current_row, space_under_tables,column_row,plotting_name_column_index, year_cols_start, len(bar_chart_table.columns), colours_dict, patterns_dict, bar_chart, total_plotting_names)

#     charts_to_plot.append(bar_chart)
#     return bar_chart_table, bar_chart, writer, current_row,charts_to_plot

def sort_table_rows_and_columns(table,table_id,plotting_names_order,year_cols):
    column_order = ['aggregate_name', 'plotting_name']+ year_cols
    #sort column_order
    try:
        table = table[column_order].copy()
    except:
        breakpoint()
        table = table[column_order].copy()
    #get the rows order for the plot id, if it exists
    if table_id in plotting_names_order.keys():
        labels = plotting_names_order[table_id].copy()
        #make sure the plotting_name_column order is the same as labels order
        table['plotting_name'] = pd.Categorical(table['plotting_name'], labels)
        #sort the table by the plotting_name_column
        table = table.sort_values('plotting_name')
    return table

def format_table(table,plotting_names_order,plotting_name_to_label_dict):
    #extract useful info from df before removing it (as we dont want to show it in the xlsx table)
    aggregate_name_column = table['aggregate_name_column'].iloc[0]
    plotting_name_column = table['plotting_name_column'].iloc[0]
    
    chart_types = np.sort(table['chart_type'].unique())
    table_id = table['table_id'].iloc[0]
    sheet_name = table['sheet_name'].iloc[0]
    chart_titles = table['chart_title'].unique()
    #make sure that we only have data for one of the cahrt ttypes. The data should be the same since its based on the same table, so jsut take the first one
    number_unique_charts = len(table['chart_type'].unique())
    # table = table[table['chart_type']==chart_types[0]].copy()
    if len(table['chart_type'].unique()) > 1:
        #remove duplicates where we exclude the chart type column and if that contains exactly x/number_unique_charts then the rows then we can assume that the chart types are different for the same table, so we will choose to keep the first chart type to keep previous behaviour of the system
        if len(table.drop_duplicates(subset = table.columns.difference(['chart_type']))) == len(table)/number_unique_charts:
            table = table[table['chart_type']==chart_types[0]].copy()
        else:
            pass
            #trying to work out whether having multiple chart types is an issue since we want to be able to od this for the bar line chart type but it seems that given the fix aboev it should be fine
    #then drop these columns
    table = table.drop(columns = ['aggregate_name_column', 'plotting_name_column', 'chart_type','table_id', 'dimensions', 'chart_title', 'scenario', 'unit', 'sheet_name'])#not sure if we should remove scenario and unit but it seems right since they are at the top of the section for that sheet. if it becomes a issue i think we should focus on making it clearer, not adding it to the table
    
    #format some cols:
    num_cols = len(table.dropna(axis='columns', how='all').columns) - 1
    year_cols = [col for col in table.columns if re.search(r'\d{4}', str(col))]
    
    # Adjust num_cols for 'Transport stocks' and 'Transport activity' sheet
    # if sheet_name == 'Transport stocks' or sheet_name == 'Transport activity':
    #     num_cols += 1

    ############################################
    # Modification of the tables in Excel
    ############################################
    # Conditional removal of rows where all data columns are zeros, excluding specific sheet names
    if sheet_name not in ['Generation capacity', 'Transport stocks', 'Transport activity']:
        # If no rows have the specified 'sheet_name', remove rows where all year columns are zeros
        table = table.loc[~(table[year_cols] == 0).all(axis=1)]
    
    # # Conditional removal of first year column(s) if all values are zeros in the beginning year(s) for all rows
    # cols_to_remove = []
    # for col in year_cols:
    #     if (table[col] == 0).all():
    #         cols_to_remove.append(col)
    #     else:
    #         # Stop removing columns once you encounter a column with a non-zero value
    #         break

    # # Remove the identified columns
    # table = table.drop(columns=cols_to_remove)
    
    ############################################
    
    # # Ensure year_cols is updated after potentially removing columns
    # year_cols = table.columns[year_cols_start:]  # This initializes year_cols as a pandas.Index
    # year_cols = year_cols.intersection(table.columns)  # This filters year_cols, keeping it as a pandas.Index
    
    # Get the year of the first year column for crossing
    first_year_col = year_cols[0]
    # try:
    #set order of columns and table, dependent on what the aggregate column is:
    table = sort_table_rows_and_columns(table,table_id,plotting_names_order,year_cols)
    
    # try:
    year_cols_start = table.columns.get_loc(year_cols[0])
    # except:
    #     breakpoint()
    year_cols = table.columns[year_cols_start:]
    # except:
    #     breakpoint()
    #     table = sort_table_rows_and_columns(table,table_id,plotting_names_order,year_cols)
    #rename fuels_plotting, emissions_fuels_plotting and emissions_sectors_plotting, sectors_plotting, capacity_plotting to Fuel and Sector respectively
    if plotting_name_column == 'fuels_plotting' or plotting_name_column == 'emissions_fuels_plotting':
        table.rename(columns = {'plotting_name':'Fuel', 'aggregate_name':'Sector'}, inplace = True)
        plotting_name_column = 'Fuel'
        aggregate_name_column = 'Sector'
    elif plotting_name_column == 'sectors_plotting' or plotting_name_column == 'emissions_sectors_plotting':
        table.rename(columns = {'plotting_name':'Sector', 'aggregate_name':'Fuel'}, inplace = True)
        plotting_name_column = 'Sector'
        aggregate_name_column = 'Fuel'
    elif plotting_name_column == 'capacity_plotting':#i guess this can just be based on sectors?
        table.rename(columns = {'plotting_name':'Sector'}, inplace = True)#, aggregate_name_column:'Fuel'
        plotting_name_column = 'Sector'
        aggregate_name_column = np.nan#'Fuel'#TODO is this right?
    else:
        #just assume that the plotting_name_column is the plotting name and the aggregate_name_column is the aggregate name
        if str(aggregate_name_column) == 'nan':
            table.rename(columns = {'plotting_name':plotting_name_column}, inplace = True)
            table.drop(columns = ['aggregate_name'], inplace = True)
            #since we dropped a column we need to update the year_cols_start to start at year_cols_start -1 (but for some reason year_cols_start = table.columns.get_loc(year_cols[0]) doesnt work)
            year_cols_start -= 1 
        else:
            table.rename(columns = {'plotting_name':plotting_name_column, 'aggregate_name':aggregate_name_column}, inplace = True)
        
    #convert plotting column and aggregate columns names to labels if any of them need converting:
    try:
        table[plotting_name_column] = table[plotting_name_column].map(plotting_name_to_label_dict).fillna(table[plotting_name_column])
    except:
        # breakpoint()#TypeError: Cannot set a Categorical with another, without identical categories
        table[plotting_name_column] = table[plotting_name_column].map(plotting_name_to_label_dict)
        
    #and just in case we now have any duplicated plotting anmes from the mapping, we will sum them
    if aggregate_name_column in table.columns:
        table = table.groupby([aggregate_name_column, plotting_name_column], observed=True, sort=False).sum().reset_index()
    else:
        table = table.groupby([plotting_name_column], observed=True, sort=False).sum().reset_index()
    
    return table, chart_types, table_id, plotting_name_column, year_cols_start,num_cols, chart_titles, first_year_col, sheet_name

def create_bar_chart_table(table,year_cols_start,bar_years, sheet_name):
    # Directly return the original table without modifications if sheet_name is 'Emissions'
    if sheet_name in ['Emissions_co2', 'Emissions_ch4', 'Emissions_co2e', 'Emissions_no2']:
        return table
    
    #create a new table of data so we only have data for every year that is a mutliple of 10. If the first year is not a multiple of 10 then include this too. This will be written 2 row under the table this is based on
    USE_BAR_YEARS=True
    if USE_BAR_YEARS:
        years_to_keep = [year for year in table.columns[year_cols_start:] if str(year) in bar_years]
    else:    
        years_to_keep = [year for year in table.columns[year_cols_start:] if int(year) % 10 == 0 or year == table.columns[year_cols_start]]
    
    if sheet_name =='Generation capacity':
        #drop all years before 2020:
        years_to_keep = [year for year in years_to_keep if int(year) >= 2020]
        # breakpoint()#not working?
    new_table = table.copy()
    #for every col after year_cols_start, filter for the years we want to keep only
    non_year_cols = table.columns[:year_cols_start]
    new_table = new_table[non_year_cols.to_list() + years_to_keep]
    return new_table

def identify_chart_positions(current_row,num_table_rows,space_under_tables,column_row, space_above_charts,space_under_charts, plotting_specifications,chart_types):
    table_start_row = current_row - num_table_rows - space_under_tables - column_row
    #get table id and extract the chart types and, if there are more than one charts, their positions
    chart_positions = []
    #if chart_types has more than one chart then we will need to estimate what column the next chart should be in since it is in the same row
    for i, chart in enumerate(chart_types):
        # #based on the position in the list of chart types, we can estimate the position of the chart
        # index_of_chart = np.where(chart_types == chart)[0][0]
        #default column width is 59 pixels. so take the chart width in pixels, divide by 59 and round up to get the number of columns to space for a chart
        num_cols_to_space = math.ceil(plotting_specifications['width_pixels'] / 59)
        col_number = 4 + (i * num_cols_to_space)
        #convert col number to letter. It will be the index of the letter in the alphabet 
        column_letter = get_column_letter(col_number)
        chart_positions.append(column_letter + str(table_start_row - plotting_specifications['height'] + space_above_charts - space_under_charts))

    return chart_positions

def get_column_letter(column_number):
    string = ""
    while column_number > 0:
        column_number, remainder = divmod(column_number - 1, 26)
        string = chr(65 + remainder) + string
    return string


# def get_plotting_name_column(table):
#     #find out if the table is aggreagted in terms of fuels or sectors. This is s
#     if len(table['fuels_plotting'].unique()) > len(table['sectors_plotting'].unique()):
#         plotting_name_column = 'fuels_plotting'
#         plotting_name_column_index = table.columns.get_loc(plotting_name_column)
#         # #drop non key column
#         # table = table.drop(columns = ['sectors_plotting'])#keeping non key col for now as it might be sueful info
#     else:
#         plotting_name_column = 'sectors_plotting'
#         plotting_name_column_index = table.columns.get_loc(plotting_name_column)
#         #drop non key column
#         # table = table.drop(columns = ['fuels_plotting'])
#     return plotting_name_column, plotting_name_column_index

#######################################
#CHART CREATION
#######################################
def create_area_chart(num_table_rows, table, plotting_name_column, sheet, current_row,space_under_tables,column_row, plotting_name_column_index, year_cols_start, num_cols, colours_dict, patterns_dict, area_chart,total_plotting_names, table_id, chart_title):
    # Extract the series of data for the chart from the excels sheets data.
    table_start_row = current_row - num_table_rows - space_under_tables - column_row
    for row_i in range(num_table_rows):
        series_name = table[plotting_name_column].iloc[row_i]
        if series_name in total_plotting_names:
            pass
        # elif sheet == 'Buildings' and table[plotting_name_column].iloc[row_i] == 'Buildings':
        #     pass
        # elif sheet == 'Industry' and table[plotting_name_column].iloc[row_i] == 'Industry':
        #     pass
        else:
            if series_name in patterns_dict.keys():#if 'CCS' in series_name or 'idle' in series_name:
                # Apply a pattern fill for 'CCS' or 'idle'
                
                area_chart.add_series({
                    'name':       [sheet, table_start_row + row_i + 1, plotting_name_column_index],
                    'categories': [sheet, table_start_row, year_cols_start, table_start_row, num_cols - 1],
                    'values':     [sheet, table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1],
                    'pattern':    {'pattern': patterns_dict[series_name], 'fg_color': table[plotting_name_column].map(colours_dict).iloc[row_i], 'bg_color': 'white'},
                    'border':     {'none': True}
                    })
            else:
                #check if were missing the color so table[plotting_name_column].map(colours_dict).iloc[row_i] is nan and whether thats causing errors
                if table[plotting_name_column].map(colours_dict).iloc[row_i] is np.nan:
                    breakpoint()
                    
                # Apply a solid fill for others
                area_chart.add_series({
                    'name':       [sheet, table_start_row + row_i + 1, plotting_name_column_index],
                    'categories': [sheet, table_start_row, year_cols_start, table_start_row, num_cols - 1],
                    'values':     [sheet, table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1],
                    'fill':       {'color': table[plotting_name_column].map(colours_dict).iloc[row_i]},
                    'border':     {'none': True}
                    })

    # Add a title to the chart
    area_chart.set_title({'name': chart_title,'name_font': {'size': 9}})
    
    #double check if chart is empty, if so let user know and skip the chart
    if len(area_chart.series) == 0:
        print('Chart for ' + sheet +' with table_id ' + table_id + ' is empty. Skipping...')#TEMP for now we are using 'table_id
        return False
    else:
        return area_chart
    
def create_line_chart(num_table_rows, table, plotting_name_column, sheet, current_row,space_under_tables,column_row, plotting_name_column_index, year_cols_start, num_cols, colours_dict, patterns_dict, line_chart, total_plotting_names, line_thickness, table_id, chart_title):
    table_start_row = current_row - num_table_rows - space_under_tables - column_row #add one for columns
    # Extract the series of data for the chart from the excels sheets data.
    for row_i in range(num_table_rows):
        if table[plotting_name_column].iloc[row_i] in total_plotting_names:
            pass
        # elif sheet == 'Buildings' and table[plotting_name_column].iloc[row_i] == 'Buildings':
        #     pass
        # elif sheet == 'Industry' and table[plotting_name_column].iloc[row_i] == 'Industry':
        #     pass
        else:
            line_chart.add_series({
                'name':       [sheet, table_start_row + row_i + 1, plotting_name_column_index],
                'categories': [sheet, table_start_row, year_cols_start, table_start_row, num_cols - 1],
                'values':     [sheet, table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1],
                'line':       {'color': table[plotting_name_column].map(colours_dict).iloc[row_i], 'width': line_thickness}
            })   
    
    # Add a title to the chart
    line_chart.set_title({'name': chart_title,'name_font': {'size': 9}})

    #double check if chart is empty, if so let user know and skip the chart
    if len(line_chart.series) == 0:
        print('Chart for ' + sheet +' with table_id ' + table_id + ' is empty. Skipping...')
        return False
    else:
        return line_chart

def create_bar_chart(num_table_rows, table, plotting_name_column, sheet, current_row, space_under_tables, column_row,plotting_name_column_index, year_cols_start, num_cols, colours_dict, patterns_dict, bar_chart,total_plotting_names, table_id, chart_title):
    # Extract the series of data for the chart from the excels sheets data.
    table_start_row = current_row - num_table_rows - space_under_tables - column_row
    for row_i in range(num_table_rows):
        series_name = table[plotting_name_column].iloc[row_i]
        if table[plotting_name_column].iloc[row_i] in total_plotting_names:
            pass
        # elif sheet == 'Buildings' and table[plotting_name_column].iloc[row_i] == 'Buildings':
        #     pass
        # elif sheet == 'Industry' and table[plotting_name_column].iloc[row_i] == 'Industry':
        #     pass
        else:
            if series_name in patterns_dict.keys():# if 'CCS' in series_name or 'idle' in series_name:
                # Apply a pattern fill for 'CCS' or 'idle'
                bar_chart.add_series({
                    'name':       [sheet, table_start_row + row_i + 1, plotting_name_column_index],
                    'categories': [sheet, table_start_row, year_cols_start, table_start_row, num_cols - 1],
                    'values':     [sheet, table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1],
                    'pattern':    {'pattern': patterns_dict[series_name], 'fg_color': table[plotting_name_column].map(colours_dict).iloc[row_i], 'bg_color': 'white'},
                    'border':     {'none': True}
                    })
            elif series_name == 'base':
                # Apply no fill for base
                bar_chart.add_series({
                    'name':       [sheet, table_start_row + row_i + 1, plotting_name_column_index],
                    'categories': [sheet, table_start_row, year_cols_start, table_start_row, num_cols - 1],
                    'values':     [sheet, table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1],
                    'fill':       {'none': True},
                    'border':     {'none': True},
                    'gap':        '20'
                    })
            elif 'rise' in series_name or 'fall' in series_name:
                # Apply transparent fill for 'rise' or 'fall'
                bar_chart.add_series({
                    'name':       [sheet, table_start_row + row_i + 1, plotting_name_column_index],
                    'categories': [sheet, table_start_row, year_cols_start, table_start_row, num_cols - 1],
                    'values':     [sheet, table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1],
                    'fill':       {'color': table[plotting_name_column].map(colours_dict).iloc[row_i], 'transparency': 50},
                    'border':     {'none': True}
                    })
            else:
                # Apply a solid fill for others
                bar_chart.add_series({
                    'name':       [sheet, table_start_row + row_i + 1, plotting_name_column_index],
                    'categories': [sheet, table_start_row, year_cols_start, table_start_row, num_cols - 1],
                    'values':     [sheet, table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1],
                    'fill':       {'color': table[plotting_name_column].map(colours_dict).iloc[row_i]},
                    'border':     {'none': True}
                    })
    
    # Add a title to the chart
    bar_chart.set_title({'name': chart_title,'name_font': {'size': 9}})
    
    # Exclude legend if sheet is 'CO2 emissions components'
    if sheet == 'CO2 emissions components':
        bar_chart.set_legend({'none': True})
    
    #double check if chart is empty, if so let user know and skip the chart
    if len(bar_chart.series) == 0:
        print('Chart for ' + sheet +' with table_id ' + table_id + ' is empty. Skipping...')
        return False
    else:
        return bar_chart
    

def create_combined_line_bar_chart(num_table_rows, table, plotting_name_column, sheet, current_row, space_under_tables, column_row, plotting_name_column_index, year_cols_start, num_cols, colours_dict, patterns_dict, primary_chart, secondary_chart, total_plotting_names, line_thickness, table_id, chart_title, plotting_specifications):
    table_start_row = current_row - num_table_rows - space_under_tables - column_row
    
    # Set the gap and overlap for the primary chart
    # It is only necessary to apply the gap and overlap property to one series in the primary chart.
    
    gap = 0  # Set the gap between columns to 33
    overlap = 100  # Set the overlap between columns to 100
    GAP_OVERLAP_APPLIED = False
    # Add series to primary chart
    for row_i in range(num_table_rows):
        series_name = table[plotting_name_column].iloc[row_i]
        if series_name in total_plotting_names:
            continue  # Skip this series
        else:
            series_options = {
                'name':       [sheet, table_start_row + row_i + 1, plotting_name_column_index],
                'categories': [sheet, table_start_row, year_cols_start, table_start_row, num_cols - 1],
                'values':     [sheet, table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1],
                'border':     {'none': True}
            }
            if series_name not in plotting_specifications['combined_line_bar_chart_lines_plotting_names']:
                if series_name in patterns_dict.keys():#if 'CCS' in series_name or 'carbon capture' in series_name:
                    # Apply a pattern fill for 'CCS' or 'carbon capture'
                    series_options.update({
                        'pattern': {'pattern': patterns_dict[series_name], 'fg_color': table[plotting_name_column].map(colours_dict).iloc[row_i], 'bg_color': 'white'}
                    })
                else:
                    # Apply a solid fill for others
                    series_options.update({
                        'fill': {'color': table[plotting_name_column].map(colours_dict).iloc[row_i]}
                    })
                # Only apply gap and overlap once to the series
                if GAP_OVERLAP_APPLIED is False:
                    series_options.update({'gap': gap, 'overlap': overlap})
                    GAP_OVERLAP_APPLIED = True
                primary_chart.add_series(series_options)
            elif series_name in plotting_specifications['combined_line_bar_chart_lines_plotting_names']:
                
                # This part remains unchanged
                # Add a series to secondary chart with line settings
                secondary_chart.add_series({
                    'name':       [sheet, table_start_row + row_i + 1, plotting_name_column_index],
                    'categories': [sheet, table_start_row, year_cols_start, table_start_row, num_cols - 1],
                    'values':     [sheet, table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1],
                    'line':       {'color': table[plotting_name_column].map(colours_dict).iloc[row_i], 'width': line_thickness}
                })
    # Combine the charts and configure the combined chart as before
    primary_chart.combine(secondary_chart)
    primary_chart.set_title({'name': chart_title, 'name_font': {'size': 9}})
    primary_chart.set_size({'width': plotting_specifications['width_pixels'], 'height': plotting_specifications['height_pixels']})

    if len(primary_chart.series) == 0:
        print('Chart for ' + sheet + ' with table_id ' + table_id + ' is empty. Skipping...')
        return False
    else:
        return primary_chart
    
def create_percentage_bar_chart(num_table_rows, table, plotting_name_column, sheet, current_row, space_under_tables, column_row, plotting_name_column_index, year_cols_start, num_cols, colours_dict, patterns_dict, percentage_bar_chart, total_plotting_names, table_id, chart_title):
    # Extract the series of data for the chart from the excel sheets data.
    table_start_row = current_row - num_table_rows - space_under_tables - column_row
    for row_i in range(num_table_rows):
        series_name = table[plotting_name_column].iloc[row_i]
        if series_name in total_plotting_names:
            pass
        else:
            series_options = {
                'name':       [sheet, table_start_row + row_i + 1, plotting_name_column_index],
                'categories': [sheet, table_start_row, year_cols_start, table_start_row, num_cols - 1],
                'values':     [sheet, table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1],
                'border':     {'none': True}
            }
            if series_name in patterns_dict.keys():
                # if 'CCS' in series_name or 'idle' in series_name:
                # breakpoint()#how to make this dependid on a a parameter?
                # Apply a pattern fill for 'CCS' or 'idle'
                series_options.update({
                    'pattern': {'pattern': patterns_dict[series_name], 'fg_color': table[plotting_name_column].map(colours_dict).iloc[row_i], 'bg_color': 'white', 'transparency': 15}
                })
            else:
                series_options.update({
                    'fill': {'color': table[plotting_name_column].map(colours_dict).iloc[row_i], 'transparency': 15}
                })
            
            percentage_bar_chart.add_series(series_options)

    # Add a title to the chart
    percentage_bar_chart.set_title({'name': chart_title, 'name_font': {'size': 9}})

    # Double check if chart is empty, if so let user know and skip the chart
    if len(percentage_bar_chart.series) == 0:
        print('Chart for ' + sheet + ' with table_id ' + table_id + ' is empty. Skipping...')
        return False
    else:
        return percentage_bar_chart

#######################################
#CHART CONFIGS
#######################################
def area_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min, first_year_col):

    # Create an area charts config
    area_chart = workbook.add_chart({'type': 'area', 'subtype': 'stacked'})
    area_chart.set_size({
        'width': plotting_specifications['width_pixels'],
        'height': plotting_specifications['height_pixels']
    })

    area_chart.set_chartarea({
        'border': {'none': True}
    })

    area_chart.set_x_axis({
        # 'name': 'Year',
        'label_position': 'low',
        'crossing': (OUTLOOK_BASE_YEAR - first_year_col) + 1,
        'major_tick_mark': 'none',
        'minor_tick_mark': 'none',
        'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
        'position_axis': 'on_tick',
        'interval_unit': 10,
        'line': {'color': '#bebebe'}
    })
        
    area_chart.set_y_axis({
        'major_tick_mark': 'none', 
        'minor_tick_mark': 'none',
        'label_position': 'low',
        'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
        'num_format': '# ### ### ##0',
        'major_gridlines': {
            'visible': True,
            'line': {'color': '#bebebe'}
        },
        'line': {'color': '#323232', 'width': 1, 'dash_type': 'square_dot'},
        'min': y_axis_min,
        'max': y_axis_max  # Set the max value for y-axis
    })
        
    area_chart.set_legend({
        'font': {'name': 'Segoe UI', 'size': 9}
        #'none': True
    })
        
    area_chart.set_title({
        'name_font': {'size': 9}  # Set the size of the title text
    })

    return area_chart

def bar_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min, sheet_name):
    # Create a another chart
    bar_chart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})#can make this percent_stacked to make it a percentage stacked bar chart!
    bar_chart.set_size({
        'width': plotting_specifications['bar_width_pixels'],
        'height': plotting_specifications['bar_height_pixels']
    })
    
    bar_chart.set_chartarea({
        'border': {'none': True}
    })
    if sheet_name in ['Emissions_co2', 'Emissions_ch4', 'Emissions_co2e', 'Emissions_no2']:
        bar_chart.set_x_axis({
            # 'name': 'Year',
            'label_position': 'low',
            'major_tick_mark': 'none',
            'minor_tick_mark': 'none',
            'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
            'interval_unit': 10,
            'line': {'color': '#bebebe'}
        })
    else:
        bar_chart.set_x_axis({
            # 'name': 'Year',
            'label_position': 'low',
            'major_tick_mark': 'none',
            'minor_tick_mark': 'none',
            'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
            'interval_unit': 1,
            'line': {'color': '#bebebe'}
        })
        
    bar_chart.set_y_axis({
        'major_tick_mark': 'none', 
        'minor_tick_mark': 'none',
        'label_position': 'low',
        'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
        'num_format': '# ### ### ##0',
        'major_gridlines': {
            'visible': True,
            'line': {'color': '#bebebe'}
        },
        'line': {'color': '#bebebe'},
        'min': y_axis_min,
        'max': y_axis_max  # Set the max value for y-axis
    })
        
    bar_chart.set_legend({
        'font': {'name': 'Segoe UI', 'size': 9}
        #'none': True
    })
        
    bar_chart.set_title({
        'name_font': {'size': 9}  # Set the size of the title text
    })

    # # Configure the series of the chart from the dataframe data.    
    # for component in ref_fedfuel_2['fuel_code'].unique():
    #     i = ref_fedfuel_2[ref_fedfuel_2['fuel_code'] == component].index[0]
    #     if not ref_fedfuel_2['fuel_code'].iloc[i] in ['Total']:
    #         line_chart.add_series({
    #             'name':       ['FED by fuel', chart_height + ref_fedfuel_1_rows + i + 4, 0],
    #             'categories': ['FED by fuel', chart_height + ref_fedfuel_1_rows + 3, 2, chart_height + ref_fedfuel_1_rows + 3, ref_fedfuel_2_cols - 1],
    #             'values':     ['FED by fuel', chart_height + ref_fedfuel_1_rows + i + 4, 2, chart_height + ref_fedfuel_1_rows + i + 4, ref_fedfuel_2_cols - 1],
    #             'fill':       {'color': ref_fedfuel_2['fuel_code'].map(colours_dict).loc[i]},
    #             'border':     {'none': True},
    #             'gap':        100
    #         })

    return bar_chart

def line_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min, first_year_col):
    # Create a FED line chart with higher level aggregation
    line_chart = workbook.add_chart({'type': 'line'})
    line_chart.set_size({
        'width': plotting_specifications['width_pixels'],
        'height': plotting_specifications['height_pixels']
    })
    
    line_chart.set_chartarea({
        'border': {'none': True}
    })
    
    line_chart.set_x_axis({
        # 'name': 'Year',
        'label_position': 'low',
        'crossing': (OUTLOOK_BASE_YEAR - first_year_col) + 1,
        'major_tick_mark': 'none',
        'minor_tick_mark': 'none',
        'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
        'position_axis': 'on_tick',
        'interval_unit': 10,
        'line': {'color': '#bebebe'}
    })
        
    line_chart.set_y_axis({
        'major_tick_mark': 'none', 
        'minor_tick_mark': 'none',
        'label_position': 'low',
        'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
        'num_format': '# ### ### ##0',
        'major_gridlines': {
            'visible': True,
            'line': {'color': '#bebebe'}
        },
        'line': {'color': '#323232', 'width': 1, 'dash_type': 'square_dot'},
        'min': y_axis_min,
        'max': y_axis_max  # Set the max value for y-axis
    })
        
    line_chart.set_legend({
        'font': {'name': 'Segoe UI', 'size': 9}
        #'none': True
    })
        
    line_chart.set_title({
        'name_font': {'size': 9}  # Set the size of the title text
    })
    
    # # Configure the series of the chart from the dataframe data.
    # for i in range(ref_fedfuel_1_rows):
    #     if not ref_fedfuel_1['fuel_code'].iloc[i] in ['Total']:
    #         line_chart.add_series({
    #             'name':       ['FED by fuel', chart_height + i + 1, 0],
    #             'categories': ['FED by fuel', chart_height, 2, chart_height, ref_fedfuel_1_cols - 1],
    #             'values':     ['FED by fuel', chart_height + i + 1, 2, chart_height + i + 1, ref_fedfuel_1_cols - 1],
    #             'line':       {'color': ref_fedfuel_1['fuel_code'].map(colours_dict).loc[i], 'width': 1}
    #         })

    return line_chart   

def combined_line_bar_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min, first_year_col):

    # Create a combined charts config
    primary_chart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})
    # Create secondary line chart
    secondary_chart = workbook.add_chart({'type': 'line', 'secondary': True})

    primary_chart.set_chartarea({
        'border': {'none': True}
    })

    # Set the x-axis and y-axis configurations
    primary_chart.set_x_axis({
        'label_position': 'low',
        'crossing': (OUTLOOK_BASE_YEAR - first_year_col) + 1,
        'major_tick_mark': 'none',
        'minor_tick_mark': 'none',
        'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
        'position_axis': 'on_tick',
        'interval_unit': 10,
        'line': {'color': '#bebebe'}
    })
        
    primary_chart.set_y_axis({
        'major_tick_mark': 'none', 
        'minor_tick_mark': 'none',
        'label_position': 'low',
        'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
        'num_format': '# ### ### ##0',
        'major_gridlines': {
            'visible': True,
            'line': {'color': '#bebebe'}
        },
        'line': {'color': '#323232', 'width': 1, 'dash_type': 'square_dot'},
        'min': y_axis_min,
        'max': y_axis_max  # Set the max value for y-axis
    })
        
    primary_chart.set_legend({
        'font': {'name': 'Segoe UI', 'size': 9}
        #'none': True
    })
        
    primary_chart.set_title({
        'name_font': {'size': 9}  # Set the size of the title text
    })

    return primary_chart, secondary_chart

def percentage_bar_plotting_specifications(workbook, plotting_specifications):
    # Create a percentage bar chart config
    percentage_bar_chart = workbook.add_chart({'type': 'area', 'subtype': 'percent_stacked'})
    percentage_bar_chart.set_size({
        'width': plotting_specifications['width_pixels'],
        'height': plotting_specifications['height_pixels']
    })
    
    percentage_bar_chart.set_chartarea({
        'border': {'none': True}
    })

    percentage_bar_chart.set_x_axis({
        # 'name': 'Year',
        'label_position': 'low',
        'major_tick_mark': 'none',
        'minor_tick_mark': 'none',
        'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
        'interval_unit': 10,
        'line': {'color': '#bebebe'}
    })
        
    percentage_bar_chart.set_y_axis({
        'major_tick_mark': 'none', 
        'minor_tick_mark': 'none',
        'label_position': 'low',
        'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
        'num_format': '0%',
        'major_gridlines': {
            'visible': True,
            'line': {'color': '#bebebe'}
        },
        'line': {'color': '#bebebe'}
    })
        
    percentage_bar_chart.set_legend({
        'font': {'name': 'Segoe UI', 'size': 9}
        #'none': True
    })
        
    percentage_bar_chart.set_title({
        'name_font': {'size': 9}  # Set the size of the title text
    })

    return percentage_bar_chart

def order_sheets(workbook, plotting_specifications):
    #order the sheets in the workbook accoridng to the custom order in master_config>plotting_specifications>sheet_order. If a sheet is not in the sheet_order list then it will be added to the end of the workbook
    #note that the workbook may hjave more sheets than are just in sheets. so order all sheets in the workbook not just the ones in sheets
    
    # Get a list of all worksheets in the workbook
    worksheets = workbook.worksheets()
    # Get the names of all worksheets
    worksheet_names = [worksheet.get_name() for worksheet in worksheets]
    
    sheet_order = plotting_specifications['sheet_order']
    #since sh
    worksheet_order = []
    end_sheets = []
    for sheet in sheet_order:
        if sheet in worksheet_names:
            worksheet_order.append(sheet)
    
    #find sheets not in sheet_order and add them to the end of the list. they will be in worksheets_objs:
    end_sheets = [sheet for sheet in worksheet_names if sheet not in sheet_order]
    worksheet_order = worksheet_order + end_sheets
    
    workbook.worksheets_objs.sort(key=lambda x: worksheet_order.index(x.get_name()))#should add a check here to make sure all sheets are in the workbook
    
    return workbook


def check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, patterns_dict, plotting_name_to_label_dict):
    #add all other unique plotting names to the plotting_name_to_label dict, but have it so they map to themselves. can get these from colours_dict
    for plotting_name in colours_dict.keys():#TODO WAT TO DO ABOUT POTENTIAL DUPLICATES ACROSS SOURCES HERE 
        if plotting_name not in plotting_name_to_label_dict.keys():
            plotting_name_to_label_dict[plotting_name] = plotting_name
    return plotting_name_to_label_dict

import re

def check_plotting_names_in_colours_dict(charts_mapping, colours_dict, RAISE_ERROR_IF_NOT_IN_DICT=False, plotting_name_column='plotting_name'):
    temp_plotting_name_to_color_dict = {}
    # Check that all unique plotting names are in colours_dict, patterns_dict, otherwise we will get an error when we try to save the workbook to Excel
    unique_plotting_names = colours_dict.keys()
    plotting_names_in_charts_mapping = charts_mapping.copy()
    plotting_names_in_charts_mapping = plotting_names_in_charts_mapping[plotting_name_column].unique()
    plotting_names_not_in_colours_dict = [x for x in plotting_names_in_charts_mapping if x not in unique_plotting_names]
    
    if len(plotting_names_not_in_colours_dict) > 0:
        if RAISE_ERROR_IF_NOT_IN_DICT:
            raise Exception('The following plotting names are not in colours_dict: {}'.format(plotting_names_not_in_colours_dict))
        else:
            # Set the missing values to random colours
            print('WARNING: The following plotting names are not in colours_dict, patterns_dict, they will have random colors assigned: {}'.format(plotting_names_not_in_colours_dict))
            for plotting_name in plotting_names_not_in_colours_dict:
                colours_dict[plotting_name] = '#{:06x}'.format(random.randint(0, 256**3-1))
    
    # Validate that all colors in colours_dict are valid hex colors
    for plotting_name, color in colours_dict.items():
        if not re.match(r"#[0-9a-fA-F]{6}", color):
            breakpoint()
            raise Exception("Color '%s' isn't a valid Excel color for plotting name '%s'" % (color, plotting_name))
    
    for plotting_name in plotting_names_in_charts_mapping:
        if plotting_name in plotting_names_not_in_colours_dict:
            temp_plotting_name_to_color_dict[plotting_name] = ''
        else:
            temp_plotting_name_to_color_dict[plotting_name] = colours_dict[plotting_name]
    
    save_used_colors_dict(temp_plotting_name_to_color_dict)
                
    return colours_dict


def check_plotting_names_in_patterns_dict(patterns_dict):
    # Define the set of allowed pattern names (this list comes from XlsxWriter's available options)
    allowed_patterns = {
        'none', 'solid', 'wide_downward_diagonal', 'wide_upward_diagonal',
        'narrow_downward_diagonal', 'narrow_upward_diagonal', 'light_vertical',
        'light_horizontal', 'light_downward_diagonal', 'light_upward_diagonal',
        'dark_vertical', 'dark_horizontal', 'dark_downward_diagonal', 'dark_upward_diagonal',
        'percent_05', 'percent_10', 'percent_20', 'percent_25', 'percent_30',
        'percent_40', 'percent_50', 'percent_60', 'percent_70', 'percent_75',
        'percent_80', 'percent_90', 'vertical_brick', 'horizontal_brick', 'weave',
        'dotted_grid', 'plaid', 'divot', 'spheroids', 'criss_cross', 'checker',
        'trellis', 'zigzag'
    }

    # Validate that all patterns in patterns_dict are valid for Excel:
    for plotting_name, pattern_name in patterns_dict.items():
        
        # Validate that the pattern is one of the allowed XlsxWriter pattern types.
        if pattern_name not in allowed_patterns:
            breakpoint()
            raise Exception(f"Pattern {pattern_name} isn't a valid Excel pattern for plotting name {plotting_name}")

    return patterns_dict

def write_charts_to_sheet(charts_to_plot, chart_positions, worksheet):
    #write charts to sheet
    for i, chart in enumerate(charts_to_plot):
        chart_position = chart_positions[i]
        import warnings

        try:
            with warnings.catch_warnings(record=True) as w:
                # Cause all warnings to always be triggered.
                warnings.simplefilter("always")

                # Attempt to insert the chart
                worksheet.insert_chart(chart_position, chart)

                # Check if a warning occurred
                if len(w) > 0:
                    print("Warning caught: ", str(w[-1].message))
        except Exception as e:
            print("Error: ", str(e))
    return worksheet
        
# def create_combined_bar_and_line_chart(num_table_rows, table, plotting_name_column, sheet, current_row, space_under_tables, column_row, 
#                           plotting_name_column_index, year_cols_start, num_cols, colours_dict, patterns_dict, bar_chart, line_chart, total_plotting_names, 
#                           line_thickness, table_id, chart_title):
#     """
#     Creates a combined bar and line chart from the given data.
    
#     :param num_table_rows: Number of rows in the table to be plotted.
#     :param table: The data table containing the plotting data.
#     :param plotting_name_column: Column name used for labeling the series.
#     :param sheet: Name of the Excel sheet.
#     :param current_row: Current row position in the Excel sheet.
#     :param space_under_tables: Space between tables in the sheet.
#     :param column_row: Column row offset.
#     :param plotting_name_column_index: Index of the plotting name column.
#     :param year_cols_start: Column index for the year start.
#     :param num_cols: Total number of columns.
#     :param colours_dict: Dictionary mapping series names to colors.
#     :param total_plotting_names: List of names to be excluded from plotting.
#     :param line_thickness: Thickness of the line in the line chart.
#     :param table_id: ID for the current table.
#     :param chart_title: Title for the chart.
    
#     :return: A combined bar and line chart object.
#     """
#     table_start_row = current_row - num_table_rows - space_under_tables - column_row
    
#     # Extract bar chart series from the data
#     for row_i in range(num_table_rows):
#         series_name = table[plotting_name_column].iloc[row_i]
#         if series_name in total_plotting_names:
#             continue
#         if 'CCS' in series_name or 'idle' in series_name or series_name == 'base' or 'rise' in series_name or 'fall' in series_name:
#             raise Exception("Series name should not be 'CCS', 'idle', 'base', 'rise', or 'fall' for a combined bar and line chart.")
#         else:
#             # Apply a solid fill for others
#             bar_chart.add_series({
#                 'name':       [sheet, table_start_row + row_i + 1, plotting_name_column_index],
#                 'categories': [sheet, table_start_row, year_cols_start - 1, table_start_row, num_cols - 1],
#                 'values':     [sheet, table_start_row + row_i + 1, year_cols_start - 1, table_start_row + row_i + 1, num_cols - 1],
#                 'fill':       {'color': table[plotting_name_column].map(colours_dict).iloc[row_i]},
#                 'border':     {'none': True}
#             })
        
#     # Extract line chart series from the data
#     for row_i in range(num_table_rows):
#         if table[plotting_name_column].iloc[row_i] in total_plotting_names:
#             continue
#         line_chart.add_series({
#             'name':       [sheet, table_start_row + row_i + 1, plotting_name_column_index],
#             'categories': [sheet, table_start_row, year_cols_start - 1, table_start_row, num_cols - 1],
#             'values':     [sheet, table_start_row + row_i + 1, year_cols_start - 1, table_start_row + row_i + 1, num_cols - 1],
#             'line':       {'color': table[plotting_name_column].map(colours_dict).iloc[row_i], 'width': line_thickness}
#         })
    
#     # Combine the bar chart and line chart
#     combined_chart = bar_chart
#     combined_chart.combine(line_chart)
#     breakpoint()
#     # Add a title to the chart
#     combined_chart.set_title({'name': chart_title,'name_font': {'size': 9}})
    
#     #double check if chart is empty, if so let user know and skip the chart
#     if len(combined_chart.series) == 0:
#         print('Chart for ' + sheet +' with table_id ' + table_id + ' is empty. Skipping...')
#         return False
#     else:
#         return combined_chart

    
# def combine_bar_and_line_chart_specs(workbook, bar_chart, line_chart, plotting_specifications):
#     """
#     Combines a bar chart and a line chart into a single chart.
    
#     :param workbook: The xlsxwriter Workbook object.
#     :param bar_chart: The existing bar chart object.
#     :param line_chart: The existing line chart object.
#     :param plotting_specifications: A dictionary containing specifications for the plot, like width and height.
#     """
    
#     # Set the combined chart as a 'chart' type to allow combination
#     combined_chart = workbook.add_chart({'type': 'column'})

#     # Add the bar chart to the combined chart
#     combined_chart.combine(line_chart)
    
#     # Apply the same chart specifications to the combined chart
#     combined_chart.set_size({
#         'width': plotting_specifications['width_pixels'],
#         'height': plotting_specifications['height_pixels']
#     })
    
#     combined_chart.set_chartarea({
#         'border': {'none': True}
#     })
    
#     # Configure X-axis and Y-axis properties
#     combined_chart.set_x_axis({
#         'label_position': 'low',
#         'major_tick_mark': 'none',
#         'minor_tick_mark': 'none',
#         'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
#         'interval_unit': 1,
#         'line': {'color': '#bebebe'}
#     })
    
#     combined_chart.set_y_axis({
#         'major_tick_mark': 'none',
#         'minor_tick_mark': 'none',
#         'label_position': 'low',
#         'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
#         'num_format': '# ### ### ##0',
#         'major_gridlines': {
#             'visible': True,
#             'line': {'color': '#bebebe'}
#         },
#         'line': {'color': '#bebebe'}
#     })
    
#     # Set legend and title similar to bar chart
#     combined_chart.set_legend({
#         'font': {'name': 'Segoe UI', 'size': 9}
#     })
    
#     combined_chart.set_title({
#         'name': 'Combined Bar and Line Chart',
#         'name_font': {'size': 9}
#     })

#     return combined_chart
