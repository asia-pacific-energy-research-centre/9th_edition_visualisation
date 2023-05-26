#%%
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

#create FILE_DATE_ID for use in file names
FILE_DATE_ID = datetime.now().strftime('%Y%m%d')
#read in data from charts mapping for each available economy for the FILE_DATE_ID. e.g. charts_mapping_9th_{economy_x}_{FILE_DATE_ID}.pkl
charts_mapping_files = [x for x in os.listdir('../intermediate_data/data/') if 'charts_mapping_9th' in x]
charts_mapping_files = [x for x in charts_mapping_files if 'pkl' in x]
charts_mapping_files = [x for x in charts_mapping_files if FILE_DATE_ID in x]
if len(charts_mapping_files) == 0:
    raise Exception('No charts mapping files found for FILE_DATE_ID: {}'.format(FILE_DATE_ID))

############################################
#read in data and extract economy from the names. 
#to extract the economy we can just use the economys in the original input file!
model_df_wide = pd.read_csv('../input_data/model_df_wide_20230420.csv')
economies = model_df_wide['economy'].unique()
charts_mapping_economys = []
for file in charts_mapping_files:
    for economy in economies:
        if economy in file:
            charts_mapping_economys.append(economy)
############################################
#import chart_config xlsx
chart_config_variables = pd.read_excel('../config/chart_config.xlsx', sheet_name='variables')
table_id_to_labels_df = pd.read_excel('../config/chart_config.xlsx', sheet_name='table_id_to_labels')
table_id_to_chart_type_df = pd.read_excel('../config/chart_config.xlsx', sheet_name='table_id_to_chart_type', index_col=0)
table_id_to_chart_position_df = pd.read_excel('../config/chart_config.xlsx', sheet_name='table_id_to_chart_position', index_col=0)

#convert
############################################
#load in colours dict, make sure top row is not a header
colours_dict = pd.read_csv('../config/colours_dict.csv', header=None)
colours_dict = colours_dict.set_index(colours_dict.columns[0]).to_dict()[colours_dict.columns[1]]


################################################################################################################################
#FORMAT CONFIGS
################################################################################################################################
#cconvert into dictrionary
if len(chart_config_variables.columns) != 2:
    raise Exception('chart_config_variables must have exactly two columns')
chart_config_variables = chart_config_variables.set_index(chart_config_variables.columns[0]).to_dict()[chart_config_variables.columns[1]]

# Make space for charts (before data/tables)
chart_height =  chart_config_variables['chart_height']
col_chart_years = ast.literal_eval(chart_config_variables['col_chart_years']) #will be like ['2000', '2010', '2018', '2020', '2030', '2040', '2050'] so format it as a list

#clean table_id_to_X files
# Convert the DataFrame values to lists and then to dictionary
table_id_to_labels_dict = table_id_to_labels_df.set_index('Unnamed: 0').T.to_dict('list')
table_id_to_chart_type_dict = table_id_to_chart_type_dict.set_index('Unnamed: 0').T.to_dict('list')
table_id_to_chart_position_dict = table_id_to_chart_position_dict.set_index('Unnamed: 0').T.to_dict('list')
 
#check they all havesame keys
if table_id_to_labels_dict.keys() != table_id_to_chart_type_dict.keys() != table_id_to_chart_position_dict.keys():
    raise Exception('You need to have the same table_ids in each of the table_id_to_X files')
    
# Drop the nan values from the lists
for key in table_id_to_labels_dict.keys():
    table_id_to_labels_dict[key] = [item for item in table_id_to_labels_dict[key] if item == item]  # item == item is a way to check if item is not nan
    table_id_to_chart_type_dict[key] = [item for item in table_id_to_chart_type_dict[key] if item == item]
    table_id_to_chart_position_dict[key] = [item for item in table_id_to_chart_position_dict[key] if item == item]


####################################################################################################################################


#%%
########################################################.
#start process
########################################################.
for economy in charts_mapping_economys:
    charts_mapping = pd.read_pickle('../intermediate_data/data/charts_mapping_9th_{}_{}.pkl'.format(economy, FILE_DATE_ID))
    # charts_mapping.columns Index(['sheet', 'unit', 'table_number', 'table_id', 'scenarios', 'economy',
    #    'year', 'sectors_plotting', 'fuels_plotting', 'value', 'legend'],
    #   dtype='object')

    #what we want to do here is replicate the workbooks created in the 8th edition code by matt horne. we will do it in a slightly different way because we already have all the data ready, we just need a funciton to iterate through it. 
    #first, explore the process of creating excel sheets wiht pyhton:

    for economy in charts_mapping['economy'].unique():
        charts_mapping_economy = charts_mapping.loc[charts_mapping['economy'] == economy]

        #so firstly, extract the unique sheets we will create:
        sheets = charts_mapping_economy['sheet'].unique()

        #create a unit dictionary to map units to the correct sheet, if there are multiple units per sheet then concatenate them
        unit_dict = charts_mapping_economy[['sheet','unit']].drop_duplicates().groupby('sheet')['unit'].apply(lambda x: ', '.join(x)).to_dict()

        #then create a dictionary of the sheets and the dataframes we will use to populate them:
        sheet_dfs = {}
        for sheet in sheets:
            sheet_dfs[sheet] = ()

            sheet_data = charts_mapping_economy.loc[charts_mapping_economy['sheet'] == sheet]
            sheet_data = sheet_data[['unit', 'value', 'fuels_plotting','sectors_plotting','scenarios','year','table_number','table_id']]
            #pivot the data and create order of cols
            sheet_data = sheet_data.pivot(index=['table_id','unit','fuels_plotting','sectors_plotting','scenarios','table_number'], columns='year', values='value')
            sheet_data = sheet_data.reset_index()

            #sort by table_number
            sheet_data = sheet_data.sort_values(by=['table_number'])
            for scenario in sheet_data['scenarios'].unique():
                #extract scenario data
                scenario_data = sheet_data.loc[(sheet_data['scenarios'] == scenario)]
                #add tables to tuple by table number
                for table in scenario_data['table_number'].unique():
                    table_data = scenario_data.loc[(scenario_data['table_number'] == table)]
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
        # cell_format3 = workbook.add_format({'font_size': 9, 'bold': True, 'underline': True})


        #iterate through the sheets and create them
        for sheet in sheets:
            #create sheet in workbook
            workbook.add_worksheet(sheet)
            worksheet = workbook.get_worksheet_by_name(sheet)
            
            #format some cells in sheet
            num_cols = len(sheet_dfs[sheet][0].columns)
            # worksheet.set_column(1, num_cols + 1, None, space_format)#set_column(first_col, last_col, width, cell_format, options) #whats this do. trying out rmeoving it
            # worksheet.set_row(chart_height, None, header_format)#whats this do. trying out rmeoving it

            #get index for start of year cols, which is when the first non object column is
            first_non_object_col = sheet_dfs[sheet][0].select_dtypes(exclude=['object']).columns[0]
            year_cols_start = sheet_dfs[sheet][0].columns.get_loc(first_non_object_col)

            num_tables = len(sheet_dfs[sheet])
            num_rows_list = []
            current_scenario = ''
            scenarios_spaces = 0
            for table in sheet_dfs[sheet]:
                num_rows = len(table.index)
                sum_num_rows = sum(num_rows_list) + scenarios_spaces
                #add num rows to lsit so we can skip them when we add following elements
                num_rows_list.append(num_rows)
                ########################
                if current_scenario == '':
                    #this is the first table. we will also use this opportunity to add the title of the sheet:
                    current_scenario = table['scenarios'].iloc[0]
                    worksheet.write(0, 0, economy + ' ' + sheet + ' ' + current_scenario, cell_format1)
                    unit = unit_dict[sheet]
                    worksheet.write(1, 0, unit, cell_format2)
                elif table['scenarios'].iloc[0] != current_scenario:
                    #New scenario. Add scenario title to next line and then carry on
                    current_scenario = table['scenarios'].iloc[0]
                    row = ((chart_height*(len(num_rows_list))) + sum_num_rows) - chart_height + 2
                    worksheet.write(row, 0, economy + ' ' + sheet + ' ' + current_scenario, cell_format1)
                    scenarios_spaces+=2#add some space under the scenario title
                    sum_num_rows+=2#add some space under the scenario title
                else:
                    pass
                ########################
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
                ########################
                #now start adding the table and charts
                table_start_row = (chart_height*(len(num_rows_list))) + sum_num_rows
                worksheet.set_row(table_start_row, None, header_format)

                #sort table into correct order
                table = workbook_creation_functions.sort_table_by_labels_dict(table,table_id_to_labels_dict,key_column)
                #identify chart types we need to create
                chart_types = workbook_creation_functions.identify_chart_type_and_positions(table, table_id_to_chart_type,table_id_to_chart_position)
                
                def create_charts(table, chart_types,chart_positions):
                    #depending on the chart type, create different charts. then add them to the worksheet according to their positions
                    table_id = table['table_id'].iloc[0]
                    charts_to_plot = []
                    for chart in chart_types[table_id]:
                        if chart == 'line':
                            #configure the chart
                            line_chart, chart_position = workbook_creation_functions.line_chart_config(num_rows, table, key_column, sheet, table_start_row, key_column_index, year_cols_start, num_cols, colours_dict, chart_height, area_chart)
                            if not line_chart:
                                #if chart is False then dont plot the chart and carry on.
                                continue
                            charts_to_plot.append([line_chart,chart_position])
                        elif chart == 'area':
                            #configure the chart
                            area_chart, chart_position = workbook_creation_functions.area_chart_config(num_rows, table, key_column, sheet, table_start_row, key_column_index, year_cols_start, num_cols, colours_dict, chart_height, area_chart)
                            if not area_chart:
                                #if chart is False then dont plot the chart and carry on.
                                continue
                            charts_to_plot.append([area_chart,chart_position])
                        elif chart == 'bar':
                            #configure the chart
                            bar_chart, chart_position = workbook_creation_functions.bar_chart_config(num_rows, table, key_column, sheet, table_start_row, key_column_index, year_cols_start, num_cols, colours_dict, chart_height, area_chart)
                            if not bar_chart:
                                #if chart is False then dont plot the chart and carry on.
                                continue
                            charts_to_plot.append([bar_chart,chart_position])
                            


                #write table to sheet
                table.to_excel(writer, sheet_name = sheet, index = False, startrow = table_start_row)

        for chart in charts_to_plot:
            chart_position = chart[0]
            chart = chart[1]
            worksheet.insert_chart(chart_position, chart)

        #save the workbook
        writer.close()



#ok. now we are going to save the plotting configurations so we can edit and utilise them later.
# So we will save the unique table_id and key_columns all in a dataframe, and then save that dataframe to a csv. this can be the table_id_to_labels_dict. This can be used to manually set the order of the labels in the legend. We will qait to see if ther eare other uses
# Then save each table_id with a column called chart_type, which will be area_chart for now. This can be the table_id_to_chart_type_dict
# Then save each table_id with a column called chart_position, which will be used to indicate if the chart will be above its table or above the previous table and to the left of it. We will have to update the code above for this to work properly though. example of this is in 8th edition FED by Fuel

#would be good to make the process clean so it can be done many times.

#also to do:
#when we use a bar chart, we will have ot make sure 10 year increments are skipped



# %%
