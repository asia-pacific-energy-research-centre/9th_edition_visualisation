


def area_chart_config(workbook):

    # Create an area charts config
    area_chart = workbook.add_chart({'type': 'area', 'subtype': 'stacked'})
    area_chart.set_size({
        'width': 500,
        'height': 300
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

def sort_table_by_labels_dict(table,table_id_to_labels_dict,key_column):
    #extarct the plot id from the table
    table_id = table['table_id'].unique()[0]
    #get the labels for the plot id
    labels = table_id_to_labels_dict[table_id]
    #make sure the key column order is the same as labels order
    table[key_column] = pd.Categorical(table[key_column], labels)
    #sort the table by the key column
    table = table.sort_values(key_column)
    return table

def identify_chart_type_and_positions(table, table_id_to_chart_type,table_id_to_chart_position):
    #get table id and extract the chart types and their positions
    table_id = table['table_id'].iloc[0]
    chart_types = table_id_to_chart_type[table_id]
    chart_positions = table_id_to_chart_position[table_id]

    #if chart positions has more than one chart position that is the same, then we will need to find label it accordingly(or is it bett to just find chart position now?)
    return chart_types,chart_positions


def create_area_chart(num_rows, table, key_column, sheet, table_start_row, key_column_index, year_cols_start, num_cols, colours_dict, chart_height, area_chart):
    # Extract the series of data for the chart from the excels sheets data.
    for row_i in range(num_rows):
        if table[key_column].iloc[row_i] in ['Total', 'TPES', 'Total primary energy supply','TFEC']:
            pass
        elif sheet == 'Buildings' and table[key_column].iloc[row_i] == 'Buildings':
            pass
        elif sheet == 'Industry' and table[key_column].iloc[row_i] == 'Industry':
            pass
        else:
            area_chart.add_series({#each series here is of the format [sheetname, first_row, first_col, last_row, last_col] which refers to where the data is coming from
                
                'name':     [sheet, table_start_row + row_i + 1, key_column_index], # refers to labels
                #[sheet, (chart_height*len(num_rows_list)) + row_i + 1, 0],#referring to the name of the series #TEMP for now we are using 'table_id'

                'categories': [sheet,  table_start_row, year_cols_start,  table_start_row, num_cols - 1],#refers to x axis
                #[sheet,  (chart_height*len(num_rows_list)), key_column_index,  (chart_height*len(num_rows_list)), num_cols - 1],

                'values':    [sheet,  table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1], #[sheet,  (chart_height*len(num_rows_list)) + row_i + 1, 4, (chart_height*len(num_rows_list)) + row_i + 1, num_cols - 1],

                'fill':       {'color': table[key_column].map(colours_dict).iloc[row_i]},
                'border':     {'none': True}

            })   
    #double check if chart is empty, if so let user know and skip the chart
    if len(area_chart.series) == 0:
        print('Chart for ' + sheet +' with table_id ' + str(table['table_id'].iloc[0]) + ' is empty. Skipping...')#TEMP for now we are using 'table_id
        return False, False
    #add the chart
    # chart_position = 'B' + str((chart_height*(len(num_rows_list)-1)) + ((len(num_rows_list)-1)*sum_num_rows) + (3*len(num_rows_list)))
    chart_position = 'B' + str(table_start_row - chart_height + 3)

    return area_chart, chart_position