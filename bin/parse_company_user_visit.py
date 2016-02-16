#!/usr/bin/env python

import sys
import os
import pandas as pd
import urlparse

industry = sys.argv[1]
raw_data_file = "../data/" + industry + "/visit_data"


def parse_domain(url):
    domain = urlparse.urlparse(url).netloc
    domain = domain.replace('.', '_')
    return domain


def parse_action_to_domain_str(action_str):

    action_list = action_str.split('')
    domain_list = []
    for action in action_list:
        arr = action.split('')
        if len(arr) < 2:
            print action
            continue

        action_type = arr[0]
        url = arr[1]
        domain = parse_domain(url)
        domain_list.append(domain)

    if len(set(domain_list)) < 2:
        return "INVALID_ACTION"

    domain_str = ' '.join(domain_list)
    return domain_str

def parse_file(user_visit_file, company_visit_file, thresh_list):

    raw_data = pd.read_csv(raw_data_file, sep='\t', header=None)
    print "raw_data shape:" + str(raw_data.shape)

    raw_data.columns = ['company_id',
                        'py_id',
                        'label',
                        'place_holder1',
                        'url_list',
                        'place_holder2',
                        'place_holder3']

    del raw_data['label']
    del raw_data['place_holder1']
    del raw_data['place_holder2']
    del raw_data['place_holder3']

    raw_data = raw_data.loc[raw_data['company_id'].isin(thresh_list)]

    user_url_data = raw_data.groupby('py_id')['url_list'].apply(lambda x: ''.join(x))
    user_url_data = user_url_data.apply(lambda x: parse_action_to_domain_str(x))
    user_url_data = user_url_data[user_url_data != "INVALID_ACTION"]
    user_url_data.to_csv(user_visit_file, sep='\t', header=None, index=None)


    company_url_data = raw_data.groupby('company_id')['url_list'].apply(lambda x : ''.join(x.apply(str)))
    company_domain_data = company_url_data.apply(parse_action_to_domain_str)
    company_domain_data.to_csv(company_visit_file, sep='\t', header=None)

    company_adv_uv_data = raw_data.groupby('company_id')['py_id'].apply(lambda x: len(pd.unique(x)))

user_file = "../data/" + industry + "/user_file"
company_file = "../data/" + industry + "/company_file"

company_thresh = "../data/" + industry + "/company_thresh_file"
thresh_list = pd.read_csv(company_thresh, sep="\t", header=None)[0]


parse_file(user_file, company_file, thresh_list)
