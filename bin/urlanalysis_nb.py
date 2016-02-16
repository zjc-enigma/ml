#!/usr/bin/python
# coding:utf-8

import sys
import math
import random
import re
import urlparse


poscnt = 0
negcnt = 0
feature2poscnt = {}
feature2negcnt = {}
featurefilename = sys.argv[1]

for line in file(featurefilename) :
        line = line.rstrip()
        arr = line.split('\t')
        #       pyid = arr[0]
        label = arr[99]
        #        features = arr[2]
        adunitid = arr[62]
        orderid = arr[51]
        feature = str(orderid) + "_" + str(adunitid)
#	featureset = set(feature)

        # for url in features.rstrip().split(" "): 
        #         url = url.split(":")
        #         url = url[0]
	# 	featureset.add(url)


	if label == "1" :
		poscnt += 1   #点击的总数
                feature2poscnt.setdefault(feature, 0) 
		feature2poscnt[feature] += 1 #点击的媒体

	if label == "0" :
		negcnt += 1   #没点击的总数
		feature2negcnt.setdefault(feature, 0)
		feature2negcnt[feature] += 1


for feature, cnt in sorted(feature2poscnt.items(), key = lambda x : x[1], reverse = True) :
	if feature not in feature2negcnt : continue 

	ctr = feature2poscnt[feature] * 1.0 / (feature2negcnt[feature] + feature2poscnt[feature])

	posrate = feature2poscnt[feature] * 1.0 / poscnt
	negrate = feature2negcnt[feature] * 1.0 / negcnt
	lift = posrate / (posrate + negrate)
	if feature2poscnt[feature] >= 5 :
		if feature not in feature2negcnt or feature2negcnt[feature] < 5 : continue
                # TODO: add company id
#                order, adunit = feature.split('_')
		print feature, feature2poscnt[feature], poscnt, posrate, feature2negcnt[feature], negcnt, negrate, lift, ctr
