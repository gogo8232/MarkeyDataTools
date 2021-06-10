import sys
sys.path.append('/home/leepark/MarkeyDataTools')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import MarkeyDataTools as mdt


Key = 'ba1c94e9a1b43440cf3ef2bf0b7803ddc39bcf2d'
acs = mdt.acs(Key)

year = 2019
table = 'B08303'
region = 'Tract'
acs.insert_inputs(year = year, table = table, region = region)
acs.gen_dataframe()
df = acs.acs_data
var_desc = acs.gen_group_variable_desc(table).sort_values('name').reset_index(drop = True)
var_desc = var_desc.merge(var_desc.label.str.split('\:\!\!', expand = True).dropna(), left_index = True, right_index = True).drop(0, axis = 1)
total = df[['County', table+'_001E']]
total.columns = ['County','total']
df.drop(table+'_001E', axis = 1, inplace = True)
rename_dict = dict(zip(df.columns[df.columns.str.match(re.compile(f'{table}.*'))].to_series().sort_values().reset_index(drop = True), var_desc.iloc[:, -1]))
df.rename(columns = rename_dict, inplace = True)

class travel:
    def __init__(self):
        self.table = df
        self.total = total
        self.table['total'] = self.total.total.astype(float)
        self.table.iloc[:, 4:] = self.table.iloc[:, 4:].astype(float)
    
    def define_region(self, region = 'tract', return_table = True):
        self.region = region.lower()
        if region.lower() == 'tract':
            if return_table:
                return(self.table)
        elif region.lower() == 'county':
            if return_table:
                return(self.table.groupby(['State','County']).agg(np.sum))
            self.county_level_data_raw = self.table.groupby(['State','County']).agg(np.sum).reset_index()
        else:
            print('It only supports that tract or county level data')
    
    def percentage(self):
        try:
            self.region
        except:
            self.define_region('tract')
        self.perc = True

        if self.region == 'tract':
            self.table_perc = self.table.set_index(['FIPS', 'Tract','County','State']).apply(lambda x: x/(x.total+.000001), axis = 1).drop('total', axis = 1).reset_index()
            return(self.table.set_index(['FIPS', 'Tract','County','State']).apply(lambda x: x/(x.total+.0001), axis = 1).drop('total', axis = 1).reset_index())
        else:
            self.county_level_data_perc = self.table.groupby(['State','County']).agg(sum).apply(lambda x: x/x.total, axis = 1).drop('total', axis = 1).reset_index()
            return(self.county_level_data_perc)
    
    def tract(self, tract_name, perc = False):
        pattern = re.compile(f'.*{tract_name}.*')
        if perc:
            try:
                self.table_perc
            except:
                self.region = 'tract'
                _ = self.percentage()
            n = len(self.table_perc.loc[self.table_perc.Tract.str.match(pattern),:])
            if n > 0:
                return(self.table_perc.loc[self.table_perc.Tract.str.match(pattern),:])
            else:
                return(self.table_perc.loc[self.table_perc.County.str.match(pattern),:])
        else:
            n = len(self.table.loc[self.table.Tract.str.match(pattern),:])
            if n > 0:
                return(self.table.loc[self.table.Tract.str.match(pattern),:])
            else:
                return(self.table.loc[self.table.County.str.match(pattern), :])
            
    def county(self, county_name, perc = False):
        pattern = re.compile(f'.*{county_name}.*')
        self.region = 'county'
        if perc:
            _ = self.percentage()
            return(self.county_level_data_perc.loc[self.county_level_data_perc.County.str.match(pattern),:])
        else:
            self.define_region(region = 'county', return_table = False)
            return(self.county_level_data_raw.loc[self.county_level_data_raw.County.str.match(pattern), :])

