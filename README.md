## Preparation:
conda env create --prefix ./env --file ./config/env_jupyter.yml

## Description
1_map_9th_data_to_plotting_template.py : run this first. it will map the 9th data to a plotting template. This is the data that will be used to create the charts and tables. The output data will be a .pkl file (../intermediate_data/data/economy_charts_mapping_9th_{economy_x}_{FILE_DATE_ID}.pkl) which contains the mapping between the plotting names and the 9th edition data that will be used to plot them. This is used in the next step to create the charts and tables.

2_prepare_9th_workbook.py: this will take in the output from 1_map_9th_data_to_plotting_template and create the charts and tables workbook. It will also create the charts and tables sheets in the workbook. The workbook will be saved in ../output_data/economy_charts_9th_{economy_x}_{FILE_DATE_ID}.xlsx

## Important sheets, pkl and csv files:
config/master_config.xlsx:
- table_id_to_chart > the main config sheet. where you determine what charts are made with what data. the data is made up of 'potting names' which are defined in the below 3 sheets The charts are made so that they are based on sectors and fuels, where there is either a sector which all the fuels are part of, or a fuel which all the sectors are part of. So if you were plotting agricultural energy use, you would have Agricuture as the aggregate and then each fuel you want to plot as the plotting name. 

    - sectors_plotting: This is a mapping for the sector categories used in the visualisation. It is important to note that this (nor the other mappings) is a 1 to many mapping, where the sectors_plotting column (which is its plotting name) contains the 1's and the sectors and subsectors columns contain the many.
    - fuels_plotting: Same as sectors but for fuels, such that the fuels_plotting column corresponds to the plotting names in the table_id_to_chart sheet.
    - transformation_sector_mappings: bit more tricky, the code needs to know if the transformation plotting name is for input or output energy for transforamtion. therefore you need to set input_fuel to TRUE or FALSE.

- plotting_name_to_label: in some cases, such as in transformation_sector_mappings you need to use extra precise plotting names, such as Power_input. This sheet will map between these and what you want the label to be in the chart. 
- colors: mapping from plotting names to colors
- plotting_specifications

- intermediate_data/data/economy_charts_mapping_9th_{}_{}.pkl > created in prepare_9th_data.py and contains the mappings and data which are used directly to create the charts workbooks and tables.

- 01_AUS_charts_2022-07-14-1530 - 8thEdition.xlsx: this is the goal for the code, to plot the 9th data in the same way as the 8th data. 

## Common Column and Variable names:
Plotting names: any time this is referred to, it is the label of an aggregation of data from the 9th data, which is then plotted in a chart with the exact 'Plotting name'. In some cases, like in the mappings: sectors_plotting, fuels_plotting and transformation_sector_mappings, the plotting names might be referred to as sectors_plotting or fuels_plotting. This is just to specify whether the aggregation is based on sectors or fuels. But these are then stacked together in the config sheets: table_id_to_chart, colors_dict where they are all referred to as plotting names.

## todo:
helper aggregates at the end of each table. i.e percentage change, compund grtowth rate like overview




