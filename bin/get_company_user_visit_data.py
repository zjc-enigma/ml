#!/usr/bin/env python
import sys
sys.path.append("../lib")
import read_conf
import logging
#-*-coding:utf-8-*-

import os
import time
import datetime

industry = sys.argv[1]
date_str = sys.argv[2]

#generate_date_str("2016/01/01", 1)

def generate_date_str(begin_date_str, day_num, ignore_list=[]):

    format_str = "%Y/%m/%d"


    begin_date_obj = datetime.datetime.strptime(begin_date_str, format_str)
    date_obj_list = [begin_date_obj + datetime.timedelta(days=x) for x in range(0, day_num)]
    date_str_list = map(lambda x: datetime.datetime.strftime(x, format_str),
                        date_obj_list)


    date_str = "{" + ",".join(date_str_list) + "}"
    return date_str


def generate_company_str(industry):

    company_id_file = "../data/" + industry + "/company_id"
    company_id_list = []

    fd = open(company_id_file)

    for line in fd:
        company_id = line.strip('\n')
        company_id_list.append(company_id)

    fd.close()

    company_str = "{" + ",".join(company_id_list) + "}"
    return company_str


def stat_company_size(output_file):

    visit_data = pd.read_csv(output_file, sep="\t", header=None)
    visit_data.columns = ['company_id',
                          'pyid',
                          'label',
                          'action']

    visit_data = visit_data[[visit_data.label==1]]



company_str = generate_company_str(industry)
output_file = "../data/" + industry + "/visit_data"

param_dict = {'date_str': date_str, 'company_list': company_str, 'output_file':output_file }

get_hdfs_data_cmd = """hadoop fs -cat "/user/liang.ming/online/base_data_othercompany_v6.1/{date_str}/positive/*/{company_list}/p*" > {output_file}"""

read_conf.exec_cmd(get_hdfs_data_cmd.format(**param_dict))
