#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 14:28:30 2021

@author: leepark
"""


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
table = ['B19013H', 'B19013B', 'B19013I','B19013'] 
region = 'Tract'
acs.insert_inputs(year = year, table = table, region = region)
acs.gen_dataframe()
df = acs.acs_data
df.replace('-666666666', np.nan, inplace = True)
names = ['median_income_white', 'median_income_black', 'median_income_hisp', 'median_income_total']
df.rename(columns = dict(zip([x + '_001E' for x in table], names)), inplace = True)
df.iloc[:,4:] = df.iloc[:,4:].astype(float)

class income:
    def __init__(self):
        self.table = df
        self.define_region()        

    def define_region(self, region = 'tract', return_table = True):
        self.region = region.lower()
        if region.lower() == 'tract':
            if return_table:
                return(self.table)
        elif region.lower() == 'county':
            if return_table:
                return(self.table.replace(np.nan, 0).groupby(['State','County']).agg(np.sum).replace(0, np.nan).reset_index())
            self.county_level_data_raw = self.table.replace(np.nan, 0).groupby(['State','County']).agg(np.sum).replace(0, np.nan).reset_index()
        else:
            print('It only supports that tract or county level data')


    def tract(self, tract_name):
        pattern = re.compile(f'.*{tract_name}.*')
        n = len(self.table.loc[self.table.Tract.str.match(pattern),:])
        if n > 0:
            return(self.table.loc[self.table.Tract.str.match(pattern),:])
        else:
            return(self.table.loc[self.table.County.str.match(pattern), :])
            
    def county(self, county_name, perc = False):
        pattern = re.compile(f'.*{county_name}.*')
        self.region = 'county'
        self.define_region(region = 'county', return_table = False)
        return(self.county_level_data_raw.loc[self.county_level_data_raw.County.str.match(pattern), :])

    