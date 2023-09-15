import pandas as pd
import math
import numpy as np
STRICT_DATA_CHECKING = False
def data_checking_warning_or_error(message):
    if STRICT_DATA_CHECKING:
        raise Exception(message)
    else:
        print(message)


def extract_max_values(data, max_values_dict):

    # Filter out rows with 'TFEC' in the 'sector' column before grouping
    filtered_data = data[data['sectors_plotting'].str.contains('TFEC') == False]
    
    grouped_data = filtered_data.groupby(['sheet_name', 'chart_type', 'scenario', 'year']).agg({'value': 'sum'}).reset_index()
    
    unique_sheets = grouped_data['sheet_name'].unique()
    unique_chart_types = grouped_data['chart_type'].unique()
    
    for sheet in unique_sheets:
        for chart_type in unique_chart_types:
            if chart_type == 'line':
                subset = data[(data['sheet_name'] == sheet) & (data['chart_type'] == chart_type) & (data['sectors_plotting'].str.contains('TFEC') == False)]
                max_value = subset['value'].max()
            else:
                subset = grouped_data[(grouped_data['sheet_name'] == sheet) & (grouped_data['chart_type'] == chart_type)]
                max_value = subset['value'].max()
            
            if max_value is not None and not np.isnan(max_value):
                # Adding 5% of the max value for padding
                y_axis_max = max_value + (0.05 * max_value)
                
                if y_axis_max <= 0:
                    y_axis_max = max_value + abs(0.05 * max_value)

                try:
                    # Calculate the order of magnitude of the max value
                    order_of_magnitude = 10 ** math.floor(math.log10(y_axis_max))
                    
                    # Calculate a rounding step based on the order of magnitude
                    rounding_step = order_of_magnitude / 2
                    
                    # Round up to the nearest rounding step
                    y_axis_max = math.ceil(y_axis_max / rounding_step) * rounding_step
                except ValueError:
                    y_axis_max = 10  # You can choose a suitable fallback value here
            else:
                y_axis_max = None
            
            max_values_dict[(sheet, chart_type)] = y_axis_max
    
    return max_values_dict


def create_charts(table, chart_types, plotting_specifications, workbook, num_table_rows, plotting_column, sheet, current_row, space_under_tables, column_row, year_cols_start, num_cols, colours_dict, total_plotting_names, max_values_dict):
    #depending on the chart type, create different charts. then add them to the worksheet according to their positions
    charts_to_plot = []
    plotting_column_index = table.columns.get_loc(plotting_column)
    for chart in chart_types:
        if chart == 'line':
            #configure the chart
            y_axis_max = max_values_dict.get((sheet, 'line'))
            line_chart = line_plotting_specifications(workbook, plotting_specifications, y_axis_max)
            line_chart = create_line_chart(num_table_rows, table, plotting_column, sheet, current_row,space_under_tables,column_row, plotting_column_index, year_cols_start, num_cols, colours_dict, line_chart,total_plotting_names)
            if not line_chart:
                #if chart is False then dont plot the chart and carry on.
                continue
            charts_to_plot.append(line_chart)
        elif chart == 'area':
            #configure the chart
            y_axis_max = max_values_dict.get((sheet, 'area'))
            area_chart = area_plotting_specifications(workbook, plotting_specifications, y_axis_max)
            area_chart = create_area_chart(num_table_rows, table, plotting_column, sheet, current_row,space_under_tables,column_row, plotting_column_index, year_cols_start, num_cols, colours_dict, area_chart,total_plotting_names)
            if not area_chart:
                #if chart is False then dont plot the chart and carry on.
                continue
            charts_to_plot.append(area_chart)
        elif chart == 'bar':            
            #configure the chart
            y_axis_max = max_values_dict.get((sheet, 'bar'))
            bar_chart = bar_plotting_specifications(workbook, plotting_specifications, y_axis_max)
            bar_chart = create_bar_chart(num_table_rows, table, plotting_column, sheet, current_row, space_under_tables,column_row,plotting_column_index, year_cols_start, len(table.columns), colours_dict, bar_chart, total_plotting_names)
            if not bar_chart:
                #if chart is False then dont plot the chart and carry on.
                continue
            charts_to_plot.append(bar_chart)
    return charts_to_plot

# def prepare_bar_chart_table_and_chart(table,year_cols_start, plotting_specifications, workbook, num_table_rows, plotting_column, sheet, current_row,space_under_tables, column_row, colours_dict,writer,charts_to_plot,total_plotting_names):
#     plotting_column_index = table.columns.get_loc(plotting_column)
    
#     bar_chart_table = create_bar_chart_table(table,year_cols_start,plotting_specifications['bar_years'])
    
#     bar_chart_table.to_excel(writer, sheet_name = sheet, index = False, startrow = current_row)
#     current_row += len(bar_chart_table.index) + space_under_tables + column_row

#     bar_chart = bar_plotting_specifications(workbook,plotting_specifications)
#     bar_chart = create_bar_chart(num_table_rows, table, plotting_column, sheet, current_row, space_under_tables,column_row,plotting_column_index, year_cols_start, len(bar_chart_table.columns), colours_dict, bar_chart, total_plotting_names)

#     charts_to_plot.append(bar_chart)
#     return bar_chart_table, bar_chart, writer, current_row,charts_to_plot

def sort_table_rows_and_columns(table,table_id,plotting_names_order,aggregate_column,plotting_column,year_cols):
    column_order = ['scenario', 'unit', aggregate_column, plotting_column]+ year_cols.tolist()
    #sort column_order
    table = table[column_order]
    #get the rows order for the plot id
    labels = plotting_names_order[table_id]
    
    #make sure the plotting_column order is the same as labels order
    table[plotting_column] = pd.Categorical(table[plotting_column], labels)
    #sort the table by the plotting_column
    
    table = table.sort_values(plotting_column)
    return table

def format_table(table,plotting_names_order,plotting_name_to_label_dict):
    #extract useful info from df before removing it (as we dont want to show it in the xlsx table)
    aggregate_column = table['aggregate_column'].iloc[0]
    plotting_column = table['plotting_column'].iloc[0]
    chart_types = table['chart_type'].unique()
    table_id = table['table_id'].iloc[0]
    
    #make sure that we only have data for one of the cahrt ttypes. The data should be the same since its based on the same table, so jsut take the first one
    table = table[table['chart_type']==chart_types[0]]
    
    #then drop these columns
    table = table.drop(columns = ['aggregate_column', 'plotting_column', 'chart_type','table_id'])
    
    #format some cols:
    num_cols = len(table.columns)
    first_non_object_col = table.select_dtypes(exclude=['object']).columns[0]
    year_cols_start = table.columns.get_loc(first_non_object_col)
    #set order of columns and table, dependent on what the aggregate column is:
    year_cols = table.columns[year_cols_start:]
    
    table = sort_table_rows_and_columns(table,table_id,plotting_names_order,aggregate_column,plotting_column,year_cols)
    
    #rename fuels_plotting and sectors_plotting to Fuel and Sector respectively
    if plotting_column == 'fuels_plotting':
        table.rename(columns = {plotting_column:'Fuel', aggregate_column:'Sector'}, inplace = True)
        plotting_column = 'Fuel'
        aggregate_column = 'Sector'
    else:
        table.rename(columns = {plotting_column:'Sector', aggregate_column:'Fuel'}, inplace = True)
        plotting_column = 'Sector'
        aggregate_column = 'Fuel'
        
    #convert plotting column and aggregate columns names to labels if any of them need converting:
    table[plotting_column] = table[plotting_column].map(plotting_name_to_label_dict)#todo test i dont delete data here
    
    return table, chart_types, table_id, plotting_column, year_cols_start,num_cols

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
    print(new_table)
    return new_table

def identify_chart_positions(current_row,num_table_rows,space_under_tables,column_row, space_under_charts, plotting_specifications,chart_types):
    table_start_row = current_row - num_table_rows - space_under_tables - column_row
    #get table id and extract the chart types and, if there are more than one charts, their positions
    chart_positions = []
    #if chart_types has more than one chart then we will need to estimate what column the next chart should be in since it is in the same row
    for chart in chart_types:
        #based on the position in the list of chart types, we can estimate the position of the chart
        index_of_chart = np.where(chart_types == chart)[0][0]
        #default column width is 59 pixels. so take the chart width in pixels, divide by 59 and round up to get the number of columns to space for a chart
        num_cols_to_space = math.ceil(plotting_specifications['width_pixels']/59)
        col_number = 2 + (index_of_chart * num_cols_to_space)
        #convert col number to letter. It will be the index of the letter in the alphabet 
        column_letter = get_column_letter(col_number)
        chart_positions.append(column_letter + str(table_start_row - plotting_specifications['height'] + space_under_charts))

    return chart_positions

def get_column_letter(column_number):
    string = ""
    while column_number > 0:
        column_number, remainder = divmod(column_number - 1, 26)
        string = chr(65 + remainder) + string
    return string


# def get_plotting_column(table):
#     #find out if the table is aggreagted in terms of fuels or sectors. This is s
#     if len(table['fuels_plotting'].unique()) > len(table['sectors_plotting'].unique()):
#         plotting_column = 'fuels_plotting'
#         plotting_column_index = table.columns.get_loc(plotting_column)
#         # #drop non key column
#         # table = table.drop(columns = ['sectors_plotting'])#keeping non key col for now as it might be sueful info
#     else:
#         plotting_column = 'sectors_plotting'
#         plotting_column_index = table.columns.get_loc(plotting_column)
#         #drop non key column
#         # table = table.drop(columns = ['fuels_plotting'])
#     return plotting_column, plotting_column_index

#######################################
#CHART CREATION
#######################################
def create_area_chart(num_table_rows, table, plotting_column, sheet, current_row,space_under_tables,column_row, plotting_column_index, year_cols_start, num_cols, colours_dict, area_chart,total_plotting_names):
    # Extract the series of data for the chart from the excels sheets data.
    table_start_row = current_row - num_table_rows - space_under_tables - column_row
    for row_i in range(num_table_rows):
        if table[plotting_column].iloc[row_i] in total_plotting_names:
            pass
        # elif sheet == 'Buildings' and table[plotting_column].iloc[row_i] == 'Buildings':
        #     pass
        # elif sheet == 'Industry' and table[plotting_column].iloc[row_i] == 'Industry':
        #     pass
        else:
            area_chart.add_series({#each series here is of the format [sheetname, first_row, first_col, last_row, last_col] which refers to where the data is coming from
                
                'name':     [sheet, table_start_row + row_i + 1, plotting_column_index], # refers to labels
                #[sheet, (chart_height*len(num_table_rows_list)) + row_i + 1, 0],#referring to the name of the series #TEMP for now we are using 'table_id'

                'categories': [sheet,  table_start_row, year_cols_start,  table_start_row, num_cols - 1],#refers to x axis
                #[sheet,  (chart_height*len(num_table_rows_list)), plotting_column_index,  (chart_height*len(num_table_rows_list)), num_cols - 1],

                'values':    [sheet,  table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1], #[sheet,  (chart_height*len(num_table_rows_list)) + row_i + 1, 4, (chart_height*len(num_table_rows_list)) + row_i + 1, num_cols - 1],

                'fill':       {'color': table[plotting_column].map(colours_dict).iloc[row_i]},
                'border':     {'none': True}

            })   
    #double check if chart is empty, if so let user know and skip the chart
    if len(area_chart.series) == 0:
        print('Chart for ' + sheet +' with table_id ' + str(table['table_id'].iloc[0]) + ' is empty. Skipping...')#TEMP for now we are using 'table_id
        return False
    else:
        return area_chart
    
def create_line_chart(num_table_rows, table, plotting_column, sheet, current_row,space_under_tables,column_row, plotting_column_index, year_cols_start, num_cols, colours_dict, line_chart, total_plotting_names):
    table_start_row = current_row - num_table_rows - space_under_tables - column_row #add one for columns
    # Extract the series of data for the chart from the excels sheets data.
    for row_i in range(num_table_rows):
        if table[plotting_column].iloc[row_i] in total_plotting_names:
            pass
        # elif sheet == 'Buildings' and table[plotting_column].iloc[row_i] == 'Buildings':
        #     pass
        # elif sheet == 'Industry' and table[plotting_column].iloc[row_i] == 'Industry':
        #     pass
        else:
            line_chart.add_series({
                'name':       [sheet, table_start_row + row_i + 1, plotting_column_index],
                'categories': [sheet, table_start_row, year_cols_start, table_start_row, num_cols - 1],
                'values':     [sheet, table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1],
                'line':       {'color': table[plotting_column].map(colours_dict).iloc[row_i], 'width': 1}
            })   
    #double check if chart is empty, if so let user know and skip the chart
    if len(line_chart.series) == 0:
        print('Chart for ' + sheet +' with table_id ' + str(table['table_id'].iloc[0]) + ' is empty. Skipping...')
        return False
    else:
        return line_chart

def create_bar_chart(num_table_rows, table, plotting_column, sheet, current_row, space_under_tables, column_row,plotting_column_index, year_cols_start, num_cols, colours_dict, bar_chart,total_plotting_names):
    # Extract the series of data for the chart from the excels sheets data.
    table_start_row = current_row - num_table_rows - space_under_tables - column_row
    for row_i in range(num_table_rows):
        if table[plotting_column].iloc[row_i] in total_plotting_names:
            pass
        # elif sheet == 'Buildings' and table[plotting_column].iloc[row_i] == 'Buildings':
        #     pass
        # elif sheet == 'Industry' and table[plotting_column].iloc[row_i] == 'Industry':
        #     pass
        else:
            bar_chart.add_series({
                'name':       [sheet, table_start_row + row_i + 1, plotting_column_index],
                'categories': [sheet, table_start_row, year_cols_start, table_start_row, num_cols - 1],
                'values':     [sheet, table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1],
                'fill':       {'color': table[plotting_column].map(colours_dict).iloc[row_i]},
                'border':     {'none': True}
            })   
    #double check if chart is empty, if so let user know and skip the chart
    if len(bar_chart.series) == 0:
        print('Chart for ' + sheet +' with table_id ' + str(table['table_id'].iloc[0]) + ' is empty. Skipping...')
        return False
    else:
        return bar_chart

#######################################
#CHART CONFIGS
#######################################
def area_plotting_specifications(workbook, plotting_specifications, y_axis_max):

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
        'crossing': 21,
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
        'min': 0,
        'max': y_axis_max,  # Set the max value for y-axis
    })
        
    area_chart.set_legend({
        'font': {'name': 'Segoe UI', 'size': 9}
        #'none': True
    })
        
    area_chart.set_title({
        'none': True
    })

    return area_chart

def bar_plotting_specifications(workbook, plotting_specifications, y_axis_max):
    # Create a another chart
    line_chart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})#can make this percent_stacked to make it a percentage stacked bar chart!
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
        'major_tick_mark': 'none',
        'minor_tick_mark': 'none',
        'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
        'interval_unit': 1,
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
        'line': {'color': '#bebebe'},
        'min': 0,
        'max': y_axis_max,  # Set the max value for y-axis
    })
        
    line_chart.set_legend({
        'font': {'name': 'Segoe UI', 'size': 9}
        #'none': True
    })
        
    line_chart.set_title({
        'none': True
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

    return line_chart

def line_plotting_specifications(workbook, plotting_specifications, y_axis_max):
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
        'crossing': 21,
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
        'min': 0,
        'max': y_axis_max,  # Set the max value for y-axis
    })
        
    line_chart.set_legend({
        'font': {'name': 'Segoe UI', 'size': 9}
        #'none': True
    })
        
    line_chart.set_title({
        'none': True
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


