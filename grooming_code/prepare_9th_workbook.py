import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
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
charts_mapping = pd.read_pickle('../intermediate_data/data/charts_mapping_9th.pkl')
#%% 
#what we want to do here is replicated the workbooks created in the 8th edition code by matt horne. we will do it in a slightly different way because we already have all the data ready, we just need a funciton to iterate through it. 
#first, explore the process of creating excel sheets wiht pyhton:

