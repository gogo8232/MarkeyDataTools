#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 14:00:41 2021

@author: leepark
"""

import sys
sys.path.append('/home/leepark/MarkeyDataTools')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import MarkeyDataTools as mdt

class gen_ind_table:
    def __init__(self, group):
        Key = 'ba1c94e9a1b43440cf3ef2bf0b7803ddc39bcf2d'
        acs = mdt.acs(Key)
        year = 2019
        table = group
        region = 'Tract'
        acs.insert_inputs(year = year, table = table, region = region)
        acs.gen_dataframe()
        df = acs.acs_data
        var_desc = acs.gen_group_variable_desc(table).sort_values('name').reset_index(drop = True)
        var_desc = var_desc.merge(var_desc.label.str.split('\:\!\!', expand = True).dropna(), left_index = True, right_index = True).drop(0, axis = 1)
        total = df[['County', table+'_001E']]
        total.columns = ['County','total']
        self.total = total
        df.drop(table+'_001E', axis = 1, inplace = True)
        rename_dict = dict(zip(df.columns[df.columns.str.match(re.compile(f'{table}.*'))].to_series().sort_values().reset_index(drop = True), var_desc.iloc[:, -1]))
        df.rename(columns = rename_dict, inplace = True)
        df['total'] = total.total
        self.df = df
        
    def __repr__(self):
        return repr(self.df)
    
    
    def gen_df(self):
        return self.df
    
    def gen_total(self):
        return self.total
    
    
    
if __name__ == '__main__':
    t = gen_ind_table('B15003')