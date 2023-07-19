
# Purpose: This script will create the 9th edition workbook for each economy.
#it is the main script for creating the workbook. it will call functions from workbook_creation_functions.py
#%%
import pickle
import pandas as pd
from datetime import datetime
import os
import ast
import workbook_creation_functions
STRICT_DATA_CHECKING = False
def data_checking_warning_or_error(message):
    if STRICT_DATA_CHECKING:
        raise Exception(message)
    else:
        print(message)

#######################################################
#CONFIG PREPARATION
#create FILE_DATE_ID for use in file names
FILE_DATE_ID = datetime.now().strftime('%Y%m%d')
# FILE_DATE_ID = '20230706'
total_plotting_names=['Total', 'TPES', 'Total primary energy supply','TFEC']
MIN_YEAR = 2000
#######################################################

#read in titles, only, from charts mapping for each available economy for the FILE_DATE_ID. e.g. charts_mapping_9th_{economy_x}_{FILE_DATE_ID}.pkl. We will use each of these to create a workbook, for each economy
charts_mapping_files = [x for x in os.listdir('../intermediate_data/data/') if 'charts_mapping_9th' in x]
charts_mapping_files = [x for x in charts_mapping_files if 'pkl' in x]
charts_mapping_files = [x for x in charts_mapping_files if FILE_DATE_ID in x]
if len(charts_mapping_files) == 0:
    raise Exception('No charts mapping files found for FILE_DATE_ID: {}'.format(FILE_DATE_ID))
#%%
############################################
#import master_config xlsx
plotting_specifications = pd.read_excel('../config/master_config.xlsx', sheet_name='plotting_specifications')
plotting_name_to_label = pd.read_excel('../config/master_config.xlsx', sheet_name='plotting_name_to_label')
colours_dict = pd.read_excel('../config/master_config.xlsx', sheet_name='colors')
with open(f'../intermediate_data/config/plotting_names_order_{FILE_DATE_ID}.pkl', 'rb') as handle:
    plotting_names_order = pickle.load(handle)
################################################################################
#FORMAT CONFIGS
################################################################################
#cconvert into dictrionary
if len(plotting_specifications.columns) != 2:
    raise Exception('plotting_specifications must have exactly two columns')
plotting_specifications = plotting_specifications.set_index(plotting_specifications.columns[0]).to_dict()[plotting_specifications.columns[1]]
# Format the bar_years as a list
plotting_specifications['bar_years'] = ast.literal_eval(plotting_specifications['bar_years']) #will be like ['2000', '2010', '2018', '2020', '2030', '2040', '2050'] so format it as a list

plotting_name_to_label_dict = plotting_name_to_label.set_index(plotting_name_to_label.columns[0]).to_dict()[plotting_name_to_label.columns[1]]
#add all other unique plotting names to the plotting_name_to_label dict, but have it so they map to themselves. can get these from colours_dict
for plotting_name in colours_dict['plotting_name'].unique():
    if plotting_name not in plotting_name_to_label_dict.keys():
        plotting_name_to_label_dict[plotting_name] = plotting_name

colours_dict = colours_dict.set_index(colours_dict.columns[0]).to_dict()[colours_dict.columns[1]]
####################################################################################################################################


#%%
########################################################.
#start process
########################################################.
for file in charts_mapping_files:
    #PREPARE DATA ########################################
    charts_mapping = pd.read_pickle(f'../intermediate_data/data/{file}')
    # 'sheet_name', 'table_number', 'chart_type', 'plotting_name',
    #    'scenario', 'economy', 'year', 'value', 'unit'
    #filter for MIN_YEAR
    charts_mapping = charts_mapping.loc[charts_mapping['year'].astype(int) >= MIN_YEAR]
    #make values 1 decimal place
    charts_mapping['value'] = charts_mapping['value'].round(1)
    #replace nas with 0
    charts_mapping['value'] = charts_mapping['value'].fillna(0)
    
    economy = charts_mapping.economy.unique()[0]

    #so firstly, extract the unique sheets we will create:
    sheets = charts_mapping['sheet_name'].unique()

    #create a unit dictionary to map units to the correct sheet, if there are multiple units per sheet then concatenate them 
    # #NOTE THAT THIS DOESNT WORK WITH THE WAY UNITS ARE IMPLEMENTED IN THE CHARTS MAPPING, BUT THE ITNENTION IS THAT ONCE WE START PLOTTING DIFFERENT UNITS THEN THIS WILL BE SOLVED IN THE CHARTS MAPPING, NOT HERE (SO THIS CODE WILL STAY THE SAME)
    unit_dict = charts_mapping[['sheet_name','unit']].drop_duplicates().groupby('sheet_name')['unit'].apply(lambda x: ', '.join(x)).to_dict()

    #then create a dictionary of the sheets and the dataframes we will use to populate them:
    sheet_dfs = {}
    for sheet in sheets:

        
        sheet_dfs[sheet] = ()

        sheet_data = charts_mapping.loc[charts_mapping['sheet_name'] == sheet]
        #drop economy and sheet_name from sheet_data
        sheet_data = sheet_data.drop(['economy','sheet_name'], axis=1)
        #pivot the data and create order of cols so it is fsater to create tables
        sheet_data = sheet_data.pivot(index=['table_number', 'chart_type', 'sectors_plotting', 'fuels_plotting', 'plotting_column', 'aggregate_column', 'scenario', 'unit', 'table_id'], columns='year', values='value')
        sheet_data = sheet_data.reset_index()

        #sort by table_number
        sheet_data = sheet_data.sort_values(by=['table_number'])
        for scenario in sheet_data['scenario'].unique():
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

    #every table has the format:'table_number', 'chart_type', 'sectors_plotting', 'fuels_plotting', 'plotting_column', 'aggregate_column', 'scenario', 'unit', ...YEARS... where years is a list of the years columns in the table (eg. 2019, 2020, 2021, 2022, 2023, 2024, 2025)

    writer = pd.ExcelWriter('../output/output_workbooks/' + economy + '_charts_' + FILE_DATE_ID + '.xlsx', engine = 'xlsxwriter')
    workbook = writer.book
    #format the workbook
    # Comma format and header format    #NOTE I DONT KNOW IF ACTUALLY IMPLEMEMNTED all of THESE BUT THEY COULD BE USEFUL!    
    space_format = workbook.add_format({'num_format': '# ### ### ##0.0;-# ### ### ##0.0;-'})
    percentage_format = workbook.add_format({'num_format': '0.0%'})
    header_format = workbook.add_format({'font_name': 'Calibri', 'font_size': 11, 'bold': True})
    cell_format1 = workbook.add_format({'bold': True})
    cell_format2 = workbook.add_format({'font_size': 9})
    # cell_format3 = workbook.add_format({'font_size': 9, 'bold': True, 'underline': True})
    #CREATE WORKBOOK ########################################
    #iterate through the sheets and create them
    for sheet in sheets:
        #create sheet in workbook
        workbook.add_worksheet(sheet)
        worksheet = workbook.get_worksheet_by_name(sheet)

        space_under_tables = 1
        space_under_charts = 2
        space_under_titles = 1
        column_row = 1
        current_scenario = ''
    
        current_row = 0
        for table in sheet_dfs[sheet]:

            ########################
            if current_scenario == '':
                #this is the first table. we will also use this opportunity to add the title of the sheet:
                current_scenario = table['scenario'].iloc[0]
                worksheet.write(0, 0, economy + ' ' + sheet + ' ' + current_scenario, cell_format1)
                unit = unit_dict[sheet]
                worksheet.write(1, 0, unit, cell_format2)
                current_row += 2
            elif table['scenario'].iloc[0] != current_scenario:
                #New scenario. Add scenario title to next line and then carry on
                current_scenario = table['scenario'].iloc[0]
                current_row += 2
                worksheet.write(current_row, 0, economy + ' ' + sheet + ' ' + current_scenario, cell_format1)
                current_row += space_under_titles                
            else:
                #add one line space between tables of same scenario
                current_row += space_under_tables
                pass
            ########################
            table, chart_types, table_id, plotting_column, year_cols_start,num_cols = workbook_creation_functions.format_table(table,plotting_names_order,plotting_name_to_label_dict)
            #make the cols for plotting_column and the one before it a bit wider so the text fits
            plotting_column_index = table.columns.get_loc(plotting_column)
            aggregate_column_index = plotting_column_index - 1
            worksheet.set_column(plotting_column_index, plotting_column_index, 20)
            worksheet.set_column(aggregate_column_index, aggregate_column_index, 20)
            ########################
            #now start adding the table and charts
            #find out if there is at least a chart for this table, in which case we need to space the table down by the height of the chart (we will add cahrt after adding table because we use the details of where the table is before adding chart)
            if len(chart_types) > 0:
                current_row += plotting_specifications['height']

            worksheet.set_row(current_row, None, header_format)
            ########################
            #if chart_type len is 1 and it is a bar chart, we need to edit the table to work for bar charts:
            if len(chart_types) == 1 and 'bar' in chart_types:   
                table = workbook_creation_functions.create_bar_chart_table(table,year_cols_start,plotting_specifications['bar_years'])
            ########################
            #write table to sheet
            table.to_excel(writer, sheet_name = sheet, index = False, startrow = current_row)
            current_row += len(table.index) + space_under_tables + column_row
            num_table_rows = len(table.index)
            ########################
            #identify and format charts we need to create
            chart_positions = workbook_creation_functions.identify_chart_positions(current_row,num_table_rows,space_under_tables,column_row, space_under_charts, plotting_specifications,chart_types)
            
            charts_to_plot = workbook_creation_functions.create_charts(table, chart_types,plotting_specifications,workbook,num_table_rows, plotting_column, sheet, current_row, space_under_tables, column_row, year_cols_start, num_cols, colours_dict,total_plotting_names)
            ########################

            #write charts to sheet
            for i, chart in enumerate(charts_to_plot):
                chart_position = chart_positions[i]
                worksheet.insert_chart(chart_position, chart)

    #save the workbook
    writer.close()

#%%




# %%
