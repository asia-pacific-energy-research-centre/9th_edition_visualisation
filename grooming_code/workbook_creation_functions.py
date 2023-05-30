import math
import pandas as pd

def create_charts(table, chart_types,chart_config,workbook,num_table_rows, key_column, sheet, table_start_row, key_column_index, year_cols_start, num_cols, colours_dict):
    #depending on the chart type, create different charts. then add them to the worksheet according to their positions
    charts_to_plot = []
    for chart in chart_types:
        if chart == 'line':
            #configure the chart
            line_chart = line_chart_config(workbook,chart_config)
            line_chart = create_line_chart(num_table_rows, table, key_column, sheet, table_start_row, key_column_index, year_cols_start, num_cols, colours_dict, line_chart)
            if not line_chart:
                #if chart is False then dont plot the chart and carry on.
                continue
            charts_to_plot.append(line_chart)
        elif chart == 'area':
            #configure the chart
            area_chart = area_chart_config(workbook,chart_config)
            area_chart = create_area_chart(num_table_rows, table, key_column, sheet, table_start_row, key_column_index, year_cols_start, num_cols, colours_dict, area_chart)
            if not area_chart:
                #if chart is False then dont plot the chart and carry on.
                continue
            charts_to_plot.append(area_chart)
        elif chart == 'bar':
            #configure the chart
            bar_chart = bar_chart_config(workbook,chart_config)
            bar_chart = create_bar_chart(num_table_rows, table, key_column, sheet, table_start_row, key_column_index, year_cols_start, num_cols, colours_dict, bar_chart)
            if not bar_chart:
                #if chart is False then dont plot the chart and carry on.
                continue
            charts_to_plot.append(bar_chart)
    return charts_to_plot

def sort_table_by_labels(table,table_id_to_labels,key_column):
    #extarct the plot id from the table
    table_id = table['table_id'].unique()[0]
    #get the labels for the plot id
    labels = table_id_to_labels[table_id]
    #make sure the key column order is the same as labels order
    table[key_column] = pd.Categorical(table[key_column], labels)
    #sort the table by the key column
    table = table.sort_values(key_column)
    return table

def identify_chart_type_and_positions(table, table_id_to_chart_type,table_start_row, chart_config):
    #get table id and extract the chart types and, if there are more than one charts, their positions
    table_id = table['table_id'].iloc[0]
    chart_types = table_id_to_chart_type[table_id]
    chart_positions = []
    #if chart_types has more than one chart then we will need to estimate what column the next chart should be in since it is in the same row
    for chart in chart_types:
        #base on the position in the list of chart types, we can estimate the position of the chart
        index_of_chart = chart_types.index(chart)
        #default column width is 59 pixels. so take the chart width in pixels, divide by 59 and round up to get the number of columns to space for a chart
        num_cols_to_space = math.ceil(chart_config['width_pixels']/59)
        col_number = 2 + (index_of_chart * num_cols_to_space)
        #convert col number to letter. It will be the index of the letter in the alphabet 
        column_letter = get_column_letter(col_number)
        chart_positions.append(column_letter + str(table_start_row - chart_config['height'] + 3))

    return chart_types,chart_positions

def get_column_letter(column_number):
    string = ""
    while column_number > 0:
        column_number, remainder = divmod(column_number - 1, 26)
        string = chr(65 + remainder) + string
    return string


def get_key_column(table):
    #find out if the table is in terms of fuels or sectors. we can do this by identifying the number of unique values in the fuels_plotting column vs the sectors_plotting column
    if len(table['fuels_plotting'].unique()) > len(table['sectors_plotting'].unique()):
        key_column = 'fuels_plotting'
        key_column_index = table.columns.get_loc(key_column)
        # #drop non key column
        # table = table.drop(columns = ['sectors_plotting'])#keeping non key col for now as it might be sueful info
    else:
        key_column = 'sectors_plotting'
        key_column_index = table.columns.get_loc(key_column)
        #drop non key column
        # table = table.drop(columns = ['fuels_plotting'])
    return key_column, key_column_index
#######################################
#CHART CREATION
#######################################
def create_area_chart(num_table_rows, table, key_column, sheet, table_start_row, key_column_index, year_cols_start, num_cols, colours_dict, area_chart):
    # Extract the series of data for the chart from the excels sheets data.
    for row_i in range(num_table_rows):
        if table[key_column].iloc[row_i] in ['Total', 'TPES', 'Total primary energy supply','TFEC']:
            pass
        elif sheet == 'Buildings' and table[key_column].iloc[row_i] == 'Buildings':
            pass
        elif sheet == 'Industry' and table[key_column].iloc[row_i] == 'Industry':
            pass
        else:
            area_chart.add_series({#each series here is of the format [sheetname, first_row, first_col, last_row, last_col] which refers to where the data is coming from
                
                'name':     [sheet, table_start_row + row_i + 1, key_column_index], # refers to labels
                #[sheet, (chart_height*len(num_table_rows_list)) + row_i + 1, 0],#referring to the name of the series #TEMP for now we are using 'table_id'

                'categories': [sheet,  table_start_row, year_cols_start,  table_start_row, num_cols - 1],#refers to x axis
                #[sheet,  (chart_height*len(num_table_rows_list)), key_column_index,  (chart_height*len(num_table_rows_list)), num_cols - 1],

                'values':    [sheet,  table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1], #[sheet,  (chart_height*len(num_table_rows_list)) + row_i + 1, 4, (chart_height*len(num_table_rows_list)) + row_i + 1, num_cols - 1],

                'fill':       {'color': table[key_column].map(colours_dict).iloc[row_i]},
                'border':     {'none': True}

            })   
    #double check if chart is empty, if so let user know and skip the chart
    if len(area_chart.series) == 0:
        print('Chart for ' + sheet +' with table_id ' + str(table['table_id'].iloc[0]) + ' is empty. Skipping...')#TEMP for now we are using 'table_id
        return False
    else:
        return area_chart
    
def create_line_chart(num_table_rows, table, key_column, sheet, table_start_row, key_column_index, year_cols_start, num_cols, colours_dict, line_chart):
    # Extract the series of data for the chart from the excels sheets data.
    for row_i in range(num_table_rows):
        if table[key_column].iloc[row_i] in ['Total', 'TPES', 'Total primary energy supply','TFEC']:
            pass
        elif sheet == 'Buildings' and table[key_column].iloc[row_i] == 'Buildings':
            pass
        elif sheet == 'Industry' and table[key_column].iloc[row_i] == 'Industry':
            pass
        else:
            line_chart.add_series({
                'name':       [sheet, table_start_row + row_i + 1, key_column_index],
                'categories': [sheet, table_start_row, year_cols_start, table_start_row, num_cols - 1],
                'values':     [sheet, table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1],
                'line':       {'color': table[key_column].map(colours_dict).iloc[row_i], 'width': 1}
            })   
    #double check if chart is empty, if so let user know and skip the chart
    if len(line_chart.series) == 0:
        print('Chart for ' + sheet +' with table_id ' + str(table['table_id'].iloc[0]) + ' is empty. Skipping...')
        return False
    else:
        return line_chart

def create_bar_chart(num_table_rows, table, key_column, sheet, table_start_row, key_column_index, year_cols_start, num_cols, colours_dict, bar_chart):
    # Extract the series of data for the chart from the excels sheets data.
    for row_i in range(num_table_rows):
        if table[key_column].iloc[row_i] in ['Total', 'TPES', 'Total primary energy supply','TFEC']:
            pass
        elif sheet == 'Buildings' and table[key_column].iloc[row_i] == 'Buildings':
            pass
        elif sheet == 'Industry' and table[key_column].iloc[row_i] == 'Industry':
            pass
        else:
            bar_chart.add_series({
                'name':       [sheet, table_start_row + row_i + 1, key_column_index],
                'categories': [sheet, table_start_row, year_cols_start, table_start_row, num_cols - 1],
                'values':     [sheet, table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1],
                'fill':       {'color': table[key_column].map(colours_dict).iloc[row_i]},
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
def area_chart_config(workbook,chart_config):

    # Create an area charts config
    area_chart = workbook.add_chart({'type': 'area', 'subtype': 'stacked'})
    area_chart.set_size({
        'width': chart_config['width_pixels'],
        'height': chart_config['height_pixels']
    })

    area_chart.set_chartarea({
        'border': {'none': True}
    })

    area_chart.set_x_axis({
        # 'name': 'Year',
        'label_position': 'low',
        'crossing': 19,
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
        # 'name': 'PJ',
        'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
        'num_format': '# ### ### ##0',
        'major_gridlines': {
            'visible': True,
            'line': {'color': '#bebebe'}
        },
        'line': {'color': '#323232',
                    'width': 1,
                    'dash_type': 'square_dot'}
    })
        
    area_chart.set_legend({
        'font': {'name': 'Segoe UI', 'size': 9}
        #'none': True
    })
        
    area_chart.set_title({
        'none': True
    })

    return area_chart

def bar_chart_config(workbook,chart_config):
    # Create a another chart
    line_chart = workbook.add_chart({'type': 'column', 'subtype': 'percent_stacked'})
    line_chart.set_size({
        'width': chart_config['width_pixels'],
        'height': chart_config['height_pixels']
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
        # 'name': 'PJ',
        'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
        'major_gridlines': {
            'visible': True,
            'line': {'color': '#bebebe'}
        },
        'line': {'color': '#bebebe'}
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
 
def line_chart_config(workbook,chart_config):
    # Create a FED line chart with higher level aggregation
    line_chart = workbook.add_chart({'type': 'line'})
    line_chart.set_size({
        'width': chart_config['width_pixels'],
        'height': chart_config['height_pixels']
    })
    
    line_chart.set_chartarea({
        'border': {'none': True}
    })
    
    line_chart.set_x_axis({
        # 'name': 'Year',
        'label_position': 'low',
        'crossing': 19,
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
        # 'name': 'PJ',
        'num_font': {'name': 'Segoe UI', 'size': 9, 'color': '#323232'},
        'num_format': '# ### ### ##0',
        'major_gridlines': {
            'visible': True,
            'line': {'color': '#bebebe'}
        },
        'line': {'color': '#323232',
                 'width': 1,
                 'dash_type': 'square_dot'}
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


