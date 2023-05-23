import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
STRICT_DATA_CHECKING = False
def data_checking_warning_or_error(message):
    if STRICT_DATA_CHECKING:
        raise Exception(message)
    else:
        print(message)

#create FILE_DATE_ID for use in file names
FILE_DATE_ID = datetime.now().strftime('%Y%m%d')
#read in data
#%%
#load data from pickle
#save data to pickle
# plotting_df.to_pickle('../intermediate_data/data/data_mapped_to_plotting_names_9th.pkl')
#and sav charts_mapping to pickle since its useful
# charts_mapping.to_pickle('../intermediate_data/data/charts_mapping_9th.pkl')

plotting_df = pd.read_pickle('../intermediate_data/data/data_mapped_to_plotting_names_9th.pkl')
# plotting_df.columns
# Index(['scenarios', 'economy', 'year', 'sectors_plotting', 'fuels_plotting',
#        'value'],
#       dtype='object')

charts_mapping = pd.read_pickle('../intermediate_data/data/charts_mapping_9th.pkl')
# charts_mapping.columns Index(['sheet', 'unit', 'table_number', 'plot_id', 'scenarios', 'economy',
#    'year', 'sectors_plotting', 'fuels_plotting', 'value', 'legend'],
#   dtype='object')

#import chart_config xlsx
chart_config = pd.read_excel('../config/chart_config.xlsx', sheet_name='variables')
#%% 

#what we want to do here is replicated the workbooks created in the 8th edition code by matt horne. we will do it in a slightly different way because we already have all the data ready, we just need a funciton to iterate through it. 
#first, explore the process of creating excel sheets wiht pyhton:
################################################################################################################################
#%%
#IMPORT CONFIG
#drop comments col from chart_config and, assuming we only have two cols left, convert into dictrionary
chart_config = chart_config.drop(columns=['comments'])
if len(chart_config.columns) != 2:
    raise Exception('chart_config must have exactly two columns')
chart_config = chart_config.set_index(chart_config.columns[0]).to_dict()[chart_config.columns[1]]

# Make space for charts (before data/tables)
chart_height =  chart_config['chart_height']
col_chart_years = chart_config['col_chart_years']

#TEMP
#create random colors dict as we dont have an official one yet:
#assign a random color to each unique value in fuels_plotting and sectors_plotting
unique_fuels = plotting_df.fuels_plotting.unique()
unique_sectors = plotting_df.sectors_plotting.unique()
unique_fuels_and_sectors = np.concatenate((unique_fuels, unique_sectors))
colours_dict = {}
for i in unique_fuels_and_sectors:
    colours_dict[i] = '#%06X' % np.random.randint(0, 0xFFFFFF)
################################################################################################################################
#PREPARE DATA

#ALL TEMP
economy = plotting_df.economy.unique()[0]#TEMP
FED_fuel = charts_mapping[charts_mapping['sheet']=='FED by fuel']#TEMP
#jsut grab table 1 for now
FED_fuel = FED_fuel[FED_fuel['table_number']==1]
#filter for reference scenario
FED_fuel = FED_fuel[FED_fuel['scenarios']=='reference']
#filter for economy
FED_fuel = FED_fuel[FED_fuel['economy']==economy]

#make the date wide and remove unneccsary cols
FED_fuel = FED_fuel[['unit', 'value', 'fuels_plotting','sectors_plotting','scenarios','year']]
FED_fuel = FED_fuel.pivot(index=['unit','fuels_plotting','sectors_plotting','scenarios'], columns='year', values='value')
FED_fuel = FED_fuel.reset_index()

#%%
run_this = False
if run_this:
    ################################################################################################################################
    # Create a Pandas excel writer workbook using xlsxwriter as the engine and save it in the directory created above
    writer = pd.ExcelWriter('../output/output_workbooks/' + economy + '_charts_' + FILE_DATE_ID + '.xlsx', engine = 'xlsxwriter')
    workbook = writer.book
    pd.io.formats.excel.ExcelFormatter.header_style = None

    # Insert the various dataframes into different sheets of the workbook
    # REFERENCE and NETZERO

    # FED by fuel
    FED_fuel.to_excel(writer, sheet_name = 'FED by fuel', index = False, startrow = chart_height)


    # CHARTS
    # REFERENCE

    # Access the workbook and first sheet with data from df1
    ref_worksheet1 = writer.sheets['FED by fuel']

    # Comma format and header format        
    space_format = workbook.add_format({'num_format': '# ### ### ##0.0;-# ### ### ##0.0;-'})
    percentage_format = workbook.add_format({'num_format': '0.0%'})
    header_format = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'bold': True})
    cell_format1 = workbook.add_format({'bold': True})
    cell_format2 = workbook.add_format({'font_size': 9})

    # Apply comma format and header format to relevant data rows
    ref_fedfuel_1_cols = len(FED_fuel.columns)
    ref_fedfuel_1_rows = len(FED_fuel.index)

    ref_fedfuel_2_cols = len(FED_fuel.columns)
    ref_fedfuel_2_rows = len(FED_fuel.index)

    netz_fedfuel_1_cols = len(FED_fuel.columns)
    netz_fedfuel_1_rows = len(FED_fuel.index)

    ref_worksheet1.set_column(1, ref_fedfuel_1_cols + 1, None, space_format)
    ref_worksheet1.set_row(chart_height, None, header_format)
    ref_worksheet1.set_row(chart_height + ref_fedfuel_1_rows + 3, None, header_format)

    ref_worksheet1.set_row((2 * chart_height) + ref_fedfuel_1_rows + ref_fedfuel_2_rows + 6, None, header_format)

    ref_worksheet1.set_row((2 * chart_height) + ref_fedfuel_1_rows + ref_fedfuel_2_rows + netz_fedfuel_1_rows + 9, None, header_format)

    ref_worksheet1.write(0, 0, economy + ' FED fuel Reference', cell_format1)

    ref_worksheet1.write(chart_height + ref_fedfuel_1_rows + ref_fedfuel_2_rows + 6, 0, economy + ' FED fuel Carbon Neutrality', cell_format1)


    # Create a FED area chart
    ref_fedfuel_chart1 = workbook.add_chart({'type': 'area', 'subtype': 'stacked'})
    ref_fedfuel_chart1.set_size({
        'width': 500,
        'height': 300
    })

    ref_fedfuel_chart1.set_chartarea({
        'border': {'none': True}
    })

    ref_fedfuel_chart1.set_x_axis({
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
        
    ref_fedfuel_chart1.set_y_axis({
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
        
    ref_fedfuel_chart1.set_legend({
        'font': {'name': 'Segoe UI', 'size': 9}
        #'none': True
    })
        
    ref_fedfuel_chart1.set_title({
        'none': True
    })

    # Configure the series of the chart from the dataframe data.
    for i in range(ref_fedfuel_1_rows):
        if not FED_fuel['fuel_code'].iloc[i] in ['Total']:
            ref_fedfuel_chart1.add_series({
                'name':       ['FED by fuel', chart_height + i + 1, 0],#[sheetname, first_row, first_col, last_row, last_col]#refers to where the data is coming from
                'categories': ['FED by fuel', chart_height, 2, chart_height, ref_fedfuel_1_cols - 1],
                'values':     ['FED by fuel', chart_height + i + 1, 2, chart_height + i + 1, ref_fedfuel_1_cols - 1],
                'fill':       {'color': FED_fuel['fuel_code'].map(colours_dict).loc[i]},
                'border':     {'none': True}
            })

        else:
            pass    
        
    ref_worksheet1.insert_chart('B3', ref_fedfuel_chart1)

####################################################################################################################################
#FUNCTIONISED VERSION OF ABOVE
####################################################################################################################################

#%%

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

#%%

#attempt to create a function to do the above for us.

#so firstly, extract the unique sheets we will create:
sheets = charts_mapping['sheet'].unique()

#create a unit dictionary to map units to the correct sheet, if there are multiple units per sheet then concatenate them
unit_dict = charts_mapping[['sheet','unit']].drop_duplicates().groupby('sheet')['unit'].apply(lambda x: ', '.join(x)).to_dict()

#then create a dictionary of the sheets and the dataframes we will use to populate them:
sheet_dfs = {}
for sheet in sheets:
    sheet_dfs[sheet] = ()

    sheet_data = charts_mapping.loc[charts_mapping['sheet'] == sheet]
    sheet_data = sheet_data[['unit', 'value', 'fuels_plotting','sectors_plotting','scenarios','year','table_number','plot_id']]
    #pivot the data and create order of cols
    sheet_data = sheet_data.pivot(index=['plot_id','unit','fuels_plotting','sectors_plotting','scenarios','table_number'], columns='year', values='value')
    sheet_data = sheet_data.reset_index()

    #add tables to tuple by table number
    for table in sheet_data['table_number'].unique():
        table_data = sheet_data.loc[(sheet_data['table_number'] == table)]
        #drop table number from table data
        table_data = table_data.drop(columns = ['table_number'])
        #add table data to tuple
        sheet_dfs[sheet] = sheet_dfs[sheet] + (table_data,)

#now we have a dictionary of dataframes for each sheet, we can iterate through them and create the charts and tables we need.
writer = pd.ExcelWriter('../output/output_workbooks/' + economy + '_charts_' + FILE_DATE_ID + '.xlsx', engine = 'xlsxwriter')
workbook = writer.book
#format the workbook
# Comma format and header format        
space_format = workbook.add_format({'num_format': '# ### ### ##0.0;-# ### ### ##0.0;-'})
percentage_format = workbook.add_format({'num_format': '0.0%'})
header_format = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'bold': True})
cell_format1 = workbook.add_format({'bold': True})
cell_format2 = workbook.add_format({'font_size': 9})


#iterate through the sheets and create them
for sheet in sheets:
    #create sheet in workbook
    workbook.add_worksheet(sheet)
    worksheet = workbook.get_worksheet_by_name(sheet)
    
    #write details at the top
    worksheet.write(0, 0, economy + ' ' + sheet, cell_format1)
    unit = unit_dict[sheet]
    worksheet.write(1, 0, unit, cell_format2)

    #format some cells in sheet
    num_cols = len(sheet_dfs[sheet][0].columns)
    worksheet.set_column(1, num_cols + 1, None, space_format)#set_column(first_col, last_col, width, cell_format, options)
    worksheet.set_row(chart_height, None, header_format)

    #get index for start of year cols, which is when the first non object column is
    first_non_object_col = sheet_dfs[sheet][0].select_dtypes(exclude=['object']).columns[0]
    year_cols_start = sheet_dfs[sheet][0].columns.get_loc(first_non_object_col)

    num_tables = len(sheet_dfs[sheet])
    num_rows_list = []
    for table in sheet_dfs[sheet]:

        num_rows = len(table.index)
        sum_num_rows = sum(num_rows_list)

        table_start_row = (chart_height*(len(num_rows_list)+1)) + sum_num_rows + (3*len(num_rows_list))
        worksheet.set_row(table_start_row, None, header_format)
        #write table to sheet
        table.to_excel(writer, sheet_name = sheet, index = False, startrow = table_start_row)

        #add num rows to lsit so we can skip them when we add following elements
        num_rows_list.append(num_rows)

        #when we introduce scenarios, add titel to idnicate scenario here
        # ref_worksheet1.write(chart_height + ref_fedfuel_1_rows + ref_fedfuel_2_rows + 6, 0, economy + ' FED fuel Carbon Neutrality', cell_format1)

        #configure the chart
        area_chart = area_chart_config(workbook)
        # Extract the series of data for the chart from the excels sheets data.
        #find out if we are plotting in terms of fuels or sectors. we can do this by identifying the number of unique values in the fuels_plotting column vs the sectors_plotting column
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

        for row_i in range(num_rows):
            if not table[key_column].iloc[row_i] in ['Total']:#maybe 'Total' is too vague, might need to have a list of vlaues. #also,m is this going to reuin the num rows count?
                area_chart.add_series({#each series here is of the format [sheetname, first_row, first_col, last_row, last_col] which refers to where the data is coming from
                    
                    'name':     [sheet, table_start_row + row_i + 1, key_column_index], # refers to labels
                    #[sheet, (chart_height*len(num_rows_list)) + row_i + 1, 0],#referring to the name of the series #TEMP for now we are using 'plot_id'

                    'categories': [sheet,  table_start_row, year_cols_start,  table_start_row, num_cols - 1],#refers to x axis
                    #[sheet,  (chart_height*len(num_rows_list)), key_column_index,  (chart_height*len(num_rows_list)), num_cols - 1],

                    'values':    [sheet,  table_start_row + row_i + 1, year_cols_start, table_start_row + row_i + 1, num_cols - 1], #[sheet,  (chart_height*len(num_rows_list)) + row_i + 1, 4, (chart_height*len(num_rows_list)) + row_i + 1, num_cols - 1],

                    'fill':       {'color': table[key_column].map(colours_dict).iloc[row_i]},
                    'border':     {'none': True}

                })

            else:
                pass    

        #add the chart
        chart_position = 'B' + str((chart_height*(len(num_rows_list)-1)) + ((len(num_rows_list)-1)*sum_num_rows) + (3*len(num_rows_list)))
        worksheet.insert_chart(chart_position, area_chart)

#save the workbook
writer.save()
#open workbook
os.startfile('../output/output_workbooks/' + economy + '_charts_' + FILE_DATE_ID + '.xlsx')
#%%
