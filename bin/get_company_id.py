#!/usr/bin/env python
#coding:utf-8

import pandas as pd
import pymysql
import os
import sys

industry_name = sys.argv[1]

conn = pymysql.connect(
    host='192.168.144.237',
    user='data',
    passwd='PIN239!@#$%^&8',
    db='category',
    charset='utf8')


industry_dir = "../data/{0}".format(industry_name)

if not os.path.exists(industry_dir):
    os.makedirs(industry_dir)

find_advertiser_id_sql = '''select    DISTINCT
                                             adrule.advertiser_id
                                      FROM
                                             advertiser_vertical_tag_inner adtag,
                                             advertiser_vertical_rule adrule
                                      WHERE
                                             adtag.category_id = adrule.category_id
                                      AND
                                             adtag.RAW_DATA
                                      LIKE   \"%{0}%\";'''.format(industry_name)


find_company_id_sql = '''select       DISTINCT
                                             company_id
                                      FROM
                                             advertiser_vertical_tag_inner adtag,
                                             advertiser_vertical_rule adrule
                                      WHERE
                                             adtag.category_id = adrule.category_id
                                      AND
                                             adtag.RAW_DATA
                                      LIKE   \"%{0}%\";'''.format(industry_name)



company_id_data = pd.read_sql(find_company_id_sql, conn)
company_id_file = "../data/{0}/company_id".format(industry_name)
company_id_data.to_csv(company_id_file,
                           encoding='utf-8',
                           index=False,
                           header=False,
                           sep="\t")

find_detail_sql = '''select    DISTINCT
                                             adrule.name, CATEGORY_NAME, adtag.RAW_DATA, advertiser_id, company_id
                                      FROM
                                             advertiser_vertical_tag_inner adtag,
                                             advertiser_vertical_rule adrule
                                      WHERE
                                             adtag.category_id = adrule.category_id
                                      AND
                                             adtag.RAW_DATA
                                      LIKE   \"%{0}%\";'''.format(industry_name)

detail_file = "../data/{0}/detail".format(industry_name)

detail_data = pd.read_sql(find_detail_sql, conn)
detail_data.to_csv(detail_file,
                       encoding='utf-8',
                       index=False,
                       header=False,
                       sep="\t")



conn.close()
