import pandas as pd
import math
import numpy as np
import ast
import os
import shutil
from utility_functions import *
STRICT_DATA_CHECKING = False
# def data_checking_warning_or_error(message):
#     if STRICT_DATA_CHECKING:
#         raise Exception(message)
#     else:
#         print(message)

def create_sheets_from_mapping_df(workbook, charts_mapping, total_plotting_names, MIN_YEAR, colours_dict, cell_format1, cell_format2, header_format, plotting_specifications, plotting_names_order, plotting_name_to_label_dict, writer, EXPECTED_COLS, ECONOMY_ID): 
    #PREPARE DATA ########################################
    
    #filter for MIN_YEAR
    charts_mapping = charts_mapping.loc[charts_mapping['year'].astype(int) >= MIN_YEAR].copy()
    #make values 1 decimal place
    charts_mapping['value'] = charts_mapping['value'].round(1).copy()
    #replace nas with 0
    charts_mapping['value'] = charts_mapping['value'].fillna(0).copy()
    
    # Getting the max values for each sheet and chart type to make the charts' y-axis consistent
    max_and_min_values_dict = {}
    max_and_min_values_dict = extract_max_and_min_values(charts_mapping, max_and_min_values_dict, total_plotting_names)
    
    colours_dict = check_plotting_names_in_colours_dict(charts_mapping, colours_dict)
    plotting_name_to_label_dict = check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, plotting_name_to_label_dict)

    #so firstly, extract the unique sheets we will create:
    sheets = charts_mapping['sheet_name'].unique()

    #create a unit dictionary to map units to the correct sheet, if there are multiple units per sheet then concatenate them 
    # #NOTE THAT THIS DOESNT WORK WITH THE WAY UNITS ARE IMPLEMENTED IN THE CHARTS MAPPING, BUT THE ITNENTION IS THAT ONCE WE START PLOTTING DIFFERENT UNITS THEN THIS WILL BE SOLVED IN THE CHARTS MAPPING, NOT HERE (SO THIS CODE WILL STAY THE SAME)
    unit_dict = charts_mapping[['sheet_name','unit']].drop_duplicates().groupby('sheet_name')['unit'].apply(lambda x: ', '.join(x)).to_dict() #TODO

    # Custom order list #TODO custom order of sheets? 
    custom_order = ['Buildings', 'Industry', 'Transport', 'Agriculture', 'Non-energy', 'TFC by fuel', 'Fuel consumption power sector', 'Refining']

    # Sort the sheets according to the custom order
    sheets = sorted(sheets, key=lambda x: custom_order.index(x) if x in custom_order else len(custom_order))

    #then create a dictionary of the sheets and the dataframes we will use to populate them:
    sheet_dfs = {}
    for sheet in sheets:

        sheet_dfs[sheet] = ()

        sheet_data = charts_mapping.loc[charts_mapping['sheet_name'] == sheet]

        #pivot the data and create order of cols so it is fsater to create tables
        EXPECTED_COLS_wide = EXPECTED_COLS.copy()
        EXPECTED_COLS_wide.remove('year')
        EXPECTED_COLS_wide.remove('value')
        
        sheet_data = sheet_data.pivot(index=EXPECTED_COLS_wide, columns='year', values='value')
        # #potentially here we get nas from missing years for certain rows, so replace with 0
        # sheet_data = sheet_data.fillna(0)#decided against it because it seems the nas are useful
        sheet_data = sheet_data.reset_index()

        #sort by table_number
        sheet_data = sheet_data.sort_values(by=['table_number'])
        for scenario in sheet_data['scenario'].unique():
            if str(scenario) == 'nan':
                scenario_data = sheet_data.copy()
            else:   
                #extract scenario data
                scenario_data = sheet_data.loc[(sheet_data['scenario'] == scenario)]
            #add tables to tuple, by table number
            for table in scenario_data['table_number'].unique():
                table_data = scenario_data.loc[(scenario_data['table_number'] == table)]
                #drop table number from table data
                table_data = table_data.drop(columns = ['table_number'])

                #add table data to tuple
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
                breakpoint()
                raise Exception('we should only have one dimension type per table')
            ########################
            current_row, current_scenario, worksheet = add_section_titles(current_row, current_scenario, sheet, worksheet, cell_format1, cell_format2, space_under_titles, table, space_under_tables,unit_dict, ECONOMY_ID)
            ########################
            table, chart_types, table_id, plotting_name_column, year_cols_start,num_cols, chart_titles = format_table(table,plotting_names_order,plotting_name_to_label_dict)
            
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
            
            if len(chart_types) == 1 and 'bar' in chart_types:   
                table = create_bar_chart_table(table,year_cols_start,plotting_specifications['bar_years'])
            ########################
            #write table to sheet
            table.to_excel(writer, sheet_name = sheet, index = False, startrow = current_row)
            current_row += len(table.index) + space_under_tables + column_row
            num_table_rows = len(table.index)
            ######################## 
            #identify and format charts we need to create
            chart_positions = identify_chart_positions(current_row,num_table_rows,space_under_tables,column_row, space_above_charts, space_under_charts, plotting_specifications,chart_types)
            # print('max_and_min_values_dict', max_and_min_values_dict, 'for sheet', sheet)
            charts_to_plot = create_charts(table, chart_types, plotting_specifications, workbook,num_table_rows, plotting_name_column, table_id, sheet, current_row, space_under_tables, column_row, year_cols_start, num_cols, colours_dict,total_plotting_names, max_and_min_values_dict, chart_titles)
            ########################

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
                            breakpoint()
                except Exception as e:
                    print("Error: ", str(e))
            
            # #create a copy of the writer and try to close it, if it fails we set breakpoitn so we can see what is going on
            # try:
            #     writer.close()
            # except:
            #     breakpoint()
            #     print('writer close failed')
    
    workbook = order_sheets(workbook, plotting_specifications, sheets)
    # breakpoint()
    return workbook, writer

def add_section_titles(current_row, current_scenario, sheet, worksheet, cell_format1, cell_format2, space_under_titles, table, space_under_tables,unit_dict, ECONOMY_ID):
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
    elif table['scenario'].iloc[0] != current_scenario:
        #New scenario. Add scenario title to next line and then carry on
        current_scenario = table['scenario'].iloc[0]
        #if scenario is na then dont add it
        current_row += 2
        worksheet.write(current_row, 0, ECONOMY_ID, cell_format1)
        worksheet.write(current_row+1, 0, sheet, cell_format1)
        if str(current_scenario) != 'nan':
            worksheet.write(current_row+2, 0, current_scenario, cell_format1)
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

def extract_max_and_min_values(data, max_and_min_values_dict, total_plotting_names):

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
        y_axis_value = value - (0.05 * value)

    # Use absolute value to handle the logarithm for negatives
    order_of_magnitude = 10 ** math.floor(math.log10(abs(y_axis_value)))
    rounding_step = order_of_magnitude / 2

    # If the value is positive, round up. If negative, round down.
    if y_axis_value > 0:
        y_axis_value = math.ceil(y_axis_value / rounding_step) * rounding_step
    else:
        y_axis_value = math.floor(y_axis_value / rounding_step) * rounding_step
    return y_axis_value

def create_charts(table, chart_types, plotting_specifications, workbook, num_table_rows, plotting_name_column, table_id, sheet, current_row, space_under_tables, column_row, year_cols_start, num_cols, colours_dict, total_plotting_names, max_and_min_values_dict, chart_titles):
    # Depending on the chart type, create different charts. Then add them to the worksheet according to their positions
    charts_to_plot = []
    plotting_name_column_index = table.columns.get_loc(plotting_name_column)
    for i, chart in enumerate(chart_types):
        chart_title = chart_titles[i-1]
        # Get the y_axis_max from max_and_min_values_dict by including the table_id in the key
        # if table_id == 'Industry_3':
        #     breakpoint()
        y_axis_max = max_and_min_values_dict.get((sheet, chart, table_id, "max"))
        y_axis_min = max_and_min_values_dict.get((sheet, chart, table_id, "min"))
        if y_axis_max is None:
            continue  # Skip the chart creation if y_axis_max is None
        if y_axis_min is None:
            breakpoint()
            raise Exception("y_axis_min is None. We werent expecting this. perhaps its ok but need to check")
        if chart == 'line':
            # Configure the chart with the updated y_axis_max
            line_chart = line_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min)
            line_thickness = plotting_specifications['line_thickness']
            line_chart = create_line_chart(num_table_rows, table, plotting_name_column, sheet, current_row, space_under_tables, column_row, plotting_name_column_index, year_cols_start, num_cols, colours_dict, line_chart, total_plotting_names, line_thickness, table_id, chart_title)
            if not line_chart:
                continue
            charts_to_plot.append(line_chart)

        elif chart == 'area':
            # Configure the chart with the updated y_axis_max, y_axis_min
            area_chart = area_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min)
            area_chart = create_area_chart(num_table_rows, table, plotting_name_column, sheet, current_row, space_under_tables, column_row, plotting_name_column_index, year_cols_start, num_cols, colours_dict, area_chart, total_plotting_names, table_id, chart_title)
            if not area_chart:
                continue
            charts_to_plot.append(area_chart)

        elif chart == 'bar':
            # Configure the chart with the updated y_axis_max and y_axis_min
            bar_chart = bar_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min)
            bar_chart = create_bar_chart(num_table_rows, table, plotting_name_column, sheet, current_row, space_under_tables, column_row, plotting_name_column_index, year_cols_start, len(table.columns), colours_dict, bar_chart, total_plotting_names, table_id, chart_title)
            if not bar_chart:
                continue
            charts_to_plot.append(bar_chart)

    return charts_to_plot



# def prepare_bar_chart_table_and_chart(table,year_cols_start, plotting_specifications, workbook, num_table_rows, plotting_name_column, sheet, current_row,space_under_tables, column_row, colours_dict,writer,charts_to_plot,total_plotting_names):
#     plotting_name_column_index = table.columns.get_loc(plotting_name_column)
    
#     bar_chart_table = create_bar_chart_table(table,year_cols_start,plotting_specifications['bar_years'])
    
#     bar_chart_table.to_excel(writer, sheet_name = sheet, index = False, startrow = current_row)
#     current_row += len(bar_chart_table.index) + space_under_tables + column_row

#     bar_chart = bar_plotting_specifications(workbook,plotting_specifications)
#     bar_chart = create_bar_chart(num_table_rows, table, plotting_name_column, sheet, current_row, space_under_tables,column_row,plotting_name_column_index, year_cols_start, len(bar_chart_table.columns), colours_dict, bar_chart, total_plotting_names)

#     charts_to_plot.append(bar_chart)
#     return bar_chart_table, bar_chart, writer, current_row,charts_to_plot

def sort_table_rows_and_columns(table,table_id,plotting_names_order,year_cols):
    column_order = ['aggregate_name', 'plotting_name']+ year_cols.tolist()
    #sort column_order
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
    chart_titles = table['chart_title'].unique()
    #make sure that we only have data for one of the cahrt ttypes. The data should be the same since its based on the same table, so jsut take the first one
    table = table[table['chart_type']==chart_types[0]].copy()
    
    #then drop these columns
    table = table.drop(columns = ['aggregate_name_column', 'plotting_name_column', 'chart_type','table_id', 'dimensions', 'chart_title', 'scenario', 'unit','sheet_name'])#not sure if we should remove scenario and unit but it seems right since they are at the top of the section for that sheet. if it becomes a issue i think we should focus on making it clearer, not adding it to the table
    
    #format some cols:
    num_cols = len(table.dropna(axis='columns', how='all').columns) - 1
    first_non_object_col = table.select_dtypes(exclude=['object']).columns[0]
    year_cols_start = table.columns.get_loc(first_non_object_col)
    
    #set order of columns and table, dependent on what the aggregate column is:
    year_cols = table.columns[year_cols_start:]
    
    table = sort_table_rows_and_columns(table,table_id,plotting_names_order,year_cols)
    
    #rename fuels_plotting, emissions_fuels_plotting and emissions_sectors_plotting, sectors_plotting, capacity_plotting to Fuel and Sector respectively
    if plotting_name_column == 'fuels_plotting':
        table.rename(columns = {'plotting_name':'Fuel', 'aggregate_name':'Sector'}, inplace = True)
        plotting_name_column = 'Fuel'
        aggregate_name_column = 'Sector'
    elif plotting_name_column == 'emissions_fuels_plotting':
        table.rename(columns = {'plotting_name':'Fuel', 'aggregate_name':'Sector'}, inplace = True)
        plotting_name_column = 'Fuel'
        aggregate_name_column = 'Sector'
    elif plotting_name_column == 'sectors_plotting':
        table.rename(columns = {'plotting_name':'Sector', 'aggregate_name':'Fuel'}, inplace = True)
        plotting_name_column = 'Sector'
        aggregate_name_column = 'Fuel'
    elif plotting_name_column == 'emissions_sectors_plotting':
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
        else:
            table.rename(columns = {'plotting_name':plotting_name_column, 'aggregate_name':aggregate_name_column}, inplace = True)
        
    #convert plotting column and aggregate columns names to labels if any of them need converting:
    table[plotting_name_column] = table[plotting_name_column].map(plotting_name_to_label_dict)#todo test i dont delete data here
    
    return table, chart_types, table_id, plotting_name_column, year_cols_start,num_cols, chart_titles

def create_bar_chart_table(table,year_cols_start,bar_years):
    #create a new table of data so we only have data for every year that is a mutliple of 10. If the first year is not a multiple of 10 then include this too. This will be written 2 row under the table this is based on
    USE_BAR_YEARS=True
    if USE_BAR_YEARS:
        years_to_keep = [year for year in table.columns[year_cols_start:] if str(year) in bar_years]
    else:    
        years_to_keep = [year for year in table.columns[year_cols_start:] if int(year) % 10 == 0 or year == table.columns[year_cols_start]]
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
    for chart in chart_types:
        #based on the position in the list of chart types, we can estimate the position of the chart
        index_of_chart = np.where(chart_types == chart)[0][0]
        #default column width is 59 pixels. so take the chart width in pixels, divide by 59 and round up to get the number of columns to space for a chart
        num_cols_to_space = math.ceil(plotting_specifications['width_pixels']/59)
        col_number = 4 + (index_of_chart * num_cols_to_space)
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
def create_area_chart(num_table_rows, table, plotting_name_column, sheet, current_row,space_under_tables,column_row, plotting_name_column_index, year_cols_start, num_cols, colours_dict, area_chart,total_plotting_names, table_id, chart_title):
    # Extract the series of data for the chart from the excels sheets data.
    table_start_row = current_row - num_table_rows - space_under_tables - column_row
    for row_i in range(num_table_rows):
        if table[plotting_name_column].iloc[row_i] in total_plotting_names:
            pass
        # elif sheet == 'Buildings' and table[plotting_name_column].iloc[row_i] == 'Buildings':
        #     pass
        # elif sheet == 'Industry' and table[plotting_name_column].iloc[row_i] == 'Industry':
        #     pass
        else:
            area_chart.add_series({#each series here is of the format [sheetname, first_row, first_col, last_row, last_col] which refers to where the data is coming from
                
                'name':     [sheet, table_start_row + row_i + 1, plotting_name_column_index], # refers to labels
                #[sheet, (chart_height*len(num_table_rows_list)) + row_i + 1, 0],#referring to the name of the series #TEMP for now we are using 'table_id'

                'categories': [sheet,  table_start_row, year_cols_start - 1,  table_start_row, num_cols - 1],#refers to x axis
                #[sheet,  (chart_height*len(num_table_rows_list)), plotting_name_column_index,  (chart_height*len(num_table_rows_list)), num_cols - 1],

                'values':    [sheet,  table_start_row + row_i + 1, year_cols_start - 1, table_start_row + row_i + 1, num_cols - 1], #[sheet,  (chart_height*len(num_table_rows_list)) + row_i + 1, 4, (chart_height*len(num_table_rows_list)) + row_i + 1, num_cols - 1],

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
    
def create_line_chart(num_table_rows, table, plotting_name_column, sheet, current_row,space_under_tables,column_row, plotting_name_column_index, year_cols_start, num_cols, colours_dict, line_chart, total_plotting_names, line_thickness, table_id, chart_title):
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
                'categories': [sheet, table_start_row, year_cols_start - 1, table_start_row, num_cols - 1],
                'values':     [sheet, table_start_row + row_i + 1, year_cols_start - 1, table_start_row + row_i + 1, num_cols - 1],
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

def create_bar_chart(num_table_rows, table, plotting_name_column, sheet, current_row, space_under_tables, column_row,plotting_name_column_index, year_cols_start, num_cols, colours_dict, bar_chart,total_plotting_names, table_id, chart_title):
    # Extract the series of data for the chart from the excels sheets data.
    table_start_row = current_row - num_table_rows - space_under_tables - column_row
    for row_i in range(num_table_rows):
        if table[plotting_name_column].iloc[row_i] in total_plotting_names:
            pass
        # elif sheet == 'Buildings' and table[plotting_name_column].iloc[row_i] == 'Buildings':
        #     pass
        # elif sheet == 'Industry' and table[plotting_name_column].iloc[row_i] == 'Industry':
        #     pass
        else:
            bar_chart.add_series({
                'name':       [sheet, table_start_row + row_i + 1, plotting_name_column_index],
                'categories': [sheet, table_start_row, year_cols_start - 1, table_start_row, num_cols - 1],
                'values':     [sheet, table_start_row + row_i + 1, year_cols_start - 1, table_start_row + row_i + 1, num_cols - 1],
                'fill':       {'color': table[plotting_name_column].map(colours_dict).iloc[row_i]},
                'border':     {'none': True}
            })   
    
    # Add a title to the chart
    bar_chart.set_title({'name': chart_title,'name_font': {'size': 9}})
    
    #double check if chart is empty, if so let user know and skip the chart
    if len(bar_chart.series) == 0:
        print('Chart for ' + sheet +' with table_id ' + table_id + ' is empty. Skipping...')
        return False
    else:
        return bar_chart

#######################################
#CHART CONFIGS
#######################################
def area_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min):

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
        'crossing': OUTLOOK_BASE_YEAR - MIN_YEAR + 1,
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

def bar_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min):
    # Create a another chart
    bar_chart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})#can make this percent_stacked to make it a percentage stacked bar chart!
    bar_chart.set_size({
        'width': plotting_specifications['width_pixels'],
        'height': plotting_specifications['height_pixels']
    })
    
    bar_chart.set_chartarea({
        'border': {'none': True}
    })
    
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

def line_plotting_specifications(workbook, plotting_specifications, y_axis_max, y_axis_min):
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
        'crossing': OUTLOOK_BASE_YEAR - MIN_YEAR + 1,
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

def order_sheets(workbook, plotting_specifications, sheets):
    #order the sheets in the workbook accoridng to the custom order in master_config>plotting_specifications>sheet_order. If a sheet is not in the sheet_order list then it will be added to the end of the workbook
    sheet_order = ast.literal_eval(plotting_specifications['sheet_order'])
    #since sh
    worksheet_order = []
    end_sheets = []
    for sheet in sheet_order:
        if sheet in sheets:
            worksheet_order.append(sheet)
    
    #find sheets not in sheet_order and add them to the end of the list. they will be in worksheets_objs:
    # Get a list of all worksheets in the workbook
    worksheets = workbook.worksheets()
    # Get the names of all worksheets
    worksheet_names = [worksheet.get_name() for worksheet in worksheets]
    end_sheets = [sheet for sheet in worksheet_names if sheet not in worksheet_order]
    worksheet_order = worksheet_order + end_sheets
    
    workbook.worksheets_objs.sort(key=lambda x: worksheet_order.index(x.get_name()))#should add a check here to make sure all sheets are in the workbook
    return workbook


def check_plotting_name_label_in_plotting_name_to_label_dict(colours_dict, plotting_name_to_label_dict):
    #add all other unique plotting names to the plotting_name_to_label dict, but have it so they map to themselves. can get these from colours_dict
    for plotting_name in colours_dict.keys():#TODO WAT TO DO ABOUT POTENTIAL DUPLICATES ACROSS SOURCES HERE 
        if plotting_name not in plotting_name_to_label_dict.keys():
            plotting_name_to_label_dict[plotting_name] = plotting_name
    return plotting_name_to_label_dict

def check_plotting_names_in_colours_dict(charts_mapping, colours_dict, RAISE_ERROR_IF_NOT_IN_DICT=False):
    #cehck that all unique plotting names are in colours_dict, otherwise we will get an error when we try to save the workbook to excel
    unique_plotting_names = colours_dict.keys()
    plotting_names_in_charts_mapping = charts_mapping.copy()
    plotting_names_in_charts_mapping = plotting_names_in_charts_mapping['plotting_name'].unique()
    plotting_names_not_in_colours_dict = [x for x in plotting_names_in_charts_mapping if x not in unique_plotting_names]
    if len(plotting_names_not_in_colours_dict) > 0:
        if RAISE_ERROR_IF_NOT_IN_DICT:
            raise Exception('The following plotting names are not in colours_dict: {}'.format(plotting_names_not_in_colours_dict))
        else:
            #set the missing values to random colours
            print('WARNING: The following plotting names are not in colours_dict, they will have random colors assigned: {}'.format(plotting_names_not_in_colours_dict))
            import random
            for plotting_name in plotting_names_not_in_colours_dict:
                colours_dict[plotting_name] = '#{:06x}'.format(random.randint(0, 256**3-1))
    return colours_dict
    
