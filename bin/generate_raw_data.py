#!/usr/bin/env python

import pandas as pd

selected_company_file = "../data/finance/company_uv_list"

company_list = pd.read_csv(selected_company_file,
                               header=None)

company_list.columns = ['company_id']

def filter_by_list(data_file, company_list):
    raw_data = pd.read_csv(data_file, header=None, sep="\t")

    raw_data.columns = ['company_id',
                            'py_id',
                            'label',
                            'place_holder1',
                            'url_list',
                            'place_holder2',
                            'place_holder3']
    merge_data = pd.merge(company_list,
                          raw_data,
                          how='left',
                          on='company_id')

    return merge_data




file_list = ['../data/finance/visit_data_01_01',
             '../data/finance/visit_data_01_09',
             '../data/finance/visit_data_01_18']


# m1 = filter_by_list('../data/finance/visit_data_01_01',
#                     company_list)

# m1.to_csv('../data/finance/filter_visit_01_01',
#               header=None,
#               index=None,
#               sep="\t")


m2 = filter_by_list('../data/finance/visit_data_01_09',
                   company_list)
m2.to_csv('../data/finance/filter_visit_01_09',
              header=None,
              index=None,
              sep="\t")

m3 = filter_by_list('../data/finance/visit_data_01_18',
                   company_list)

m3.to_csv('../data/finance/filter_visit_01_18',
              header=None,
              index=None,
              sep="\t")
# #
