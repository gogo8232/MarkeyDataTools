#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 11:40:17 2021

@author: leepark
"""

import sys
sys.path.append('../')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import MarkeyDataTools as mdt
import gen_ind_table as git




class means:
    def __init__(self):
        Key = 'ba1c94e9a1b43440cf3ef2bf0b7803ddc39bcf2d'
        acs = mdt.acs(Key)
        year = 2019
        table = 'B08141'
        region = 'Tract'
        acs.insert_inputs(year = year, table = table, region = region)
        acs.gen_dataframe()
        df = acs.acs_data
        df = df[df.columns.to_list()[:4] + ['B08141_002E','B08141_003E','B08141_004E','B08141_005E','B08141_001E']]
        
        df = df.rename(columns = dict(zip(['B08141_002E','B08141_003E','B08141_004E','B08141_005E','B08141_001E'],
                                     ['No vehicle', '1 vehicle','2 vehicles', '3 vehicles', 'total'])))
        df.iloc[:,4:] = df.iloc[:,4:].astype(float)
        
        df['>1 vehicle']  = df[['1 vehicle','2 vehicles', '3 vehicles']].apply(np.sum, axis = 1)
        df.drop(['1 vehicle','2 vehicles', '3 vehicles'], axis = 1, inplace =True)
        
        df = df.iloc[:, [0,1,2,3,4,6,5]]
        df.iloc[:,4:] = df.iloc[:,4:].astype(float)
        self.table = df
    
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
        