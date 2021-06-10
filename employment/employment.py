#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 11:05:36 2021

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


class employment:
    def __init__(self):
        Key = 'ba1c94e9a1b43440cf3ef2bf0b7803ddc39bcf2d'
        acs = mdt.acs(Key)
        year = 2019
        table = 'B23025'
        region = 'Tract'
        acs.insert_inputs(year = year, table = table, region = region)
        acs.gen_dataframe()
        df = acs.acs_data
        df.iloc[:,4:] = df.iloc[:,4:].astype(float)
        df = df.loc[:, df.columns[:4].to_list()+ ['B23025_004E','B23025_005E', 'B23025_003E']]
        df.rename(columns = dict(zip(  ['B23025_004E','B23025_005E', 'B23025_003E'] ,
                                     ['employed', 'unemployed', 'total'])), inplace = True)

        self.table = df
        self.table.iloc[:, 4:]  = self.table.iloc[:, 4:].astype(float)
        self.region = 'tract'
        self.define_region()
        
        
    def define_region(self, region = 'tract', return_table = True):
        self.region = region.lower()
        if region.lower() == 'tract':
            if return_table:
                return(self.table)
        elif region.lower() == 'county':
            self.county_level_data_raw = self.table.drop(['Tract', 'FIPS'], axis = 1).groupby(['State','County']).agg(np.sum).reset_index()
            if return_table:
                return(self.table.drop(['Tract', 'FIPS'], axis = 1).groupby(['State','County']).agg(np.sum))
        else:
            print('It only supports that tract or county level data')
    
    def percentage(self):
        try:
            self.region
        except:
            self.define_region('tract')

        if self.region == 'tract':
            self.table_perc = self.table.set_index(['FIPS', 'Tract','County','State']).apply(lambda x: x/(x.total+.000001), axis = 1).drop('total', axis = 1).reset_index()
            return(self.table.set_index(['FIPS', 'Tract','County','State']).apply(lambda x: x/(x.total+.0001), axis = 1).drop('total', axis = 1).reset_index())
        else:
            self.county_level_data_perc = self.table.drop(['Tract', 'FIPS'], axis = 1).groupby(['State','County']).agg(np.sum).apply(lambda x: x/x.total, axis = 1).drop('total', axis = 1).reset_index()
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
        