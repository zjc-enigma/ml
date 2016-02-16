import os
import sys
sys.path.append("../lib")
import read_conf

from time import time
import pickle
import sys
import pdb

import numpy as np

from pyemd import emd
from gensim.models.word2vec import Word2Vec
from scipy.spatial.distance import cosine
import logging


def nBOW_dict(document_dict, vocab):
    '''
    Compute nBOW representation of a document

    Input:
    doc:        Document, list of words (strings).
    vocab:      Set of words in all documents.

    Returns:    List of floats, nBow representation.
    '''
    doc_len = sum(document_dict.itervalues())
    f = []
    for i, t in enumerate(vocab):
        count = 0
        if t in document_dict:
            count = document_dict[t]

        f.append(count / float(doc_len))

    return f



def get_comp_dict():
    comp_domain_file = "../data/finance/company_file"
    comp_dict = {}

    fd = open(comp_domain_file)
    for line in fd:
        line = line.strip()
        arr = line.split('\t')
        if len(arr) < 2:
            print "arr size < 2"
            continue

        comp_id = arr[0]
        comp_action = arr[1]
        comp_dict[comp_id] = comp_action.split(' ')
    fd.close()
    return comp_dict

def filter_action_by_uv(comp_dict, uv=100):
    action_uv = {}
    from collections import Counter

    for comp in comp_dict:
        action_list = comp_dict[comp]
        action_dict = Counter(action_list)
        comp_dict[comp] = {k:v for (k, v) in action_dict.items() if v > uv}


def calc_dist(x, y):
    return cosine(x, y)
#    return np.sqrt(np.sum((x - y)**2))

def calc_nb_dist(d1, d2):
    u1 = set(d1.keys())
    u2 = set(d2.keys())
    du = u1.union(u2)

    f1 = np.array(nBOW_dict(d1, du))
    f2 = np.array(nBOW_dict(d2, du))
    dist = calc_dist(f1, f2)
    return dist

print "get company dict"
comp_dict = get_comp_dict()
filter_action_by_uv(comp_dict, 5)

res_file = "../data/finance/company_nb_cosine"
wfd = open(res_file, 'w+')
processed_comp_list = []

for comp1 in comp_dict:

    processed_comp_list.append(comp1)

    for comp2 in comp_dict:
        if comp2 in processed_comp_list:
            continue


        dist = calc_nb_dist(comp_dict[comp1],
                            comp_dict[comp2])


        out = str(comp1) + "\t" + str(comp2) + "\t" + str(dist)
        print out

        wfd.write(out + "\n")


wfd.close()
