import os
import sys
sys.path.append("../lib")
import read_conf

from time import time
import pickle
import sys
import pdb
import pandas as pd
import numpy as np
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
import functools
from pyemd import emd
from gensim.models.word2vec import Word2Vec
from scipy.spatial.distance import cosine

import logging

#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def nBOW(document, vocab):
    '''
    Compute nBOW representation of a document

    Input:
    doc:        Document, list of words (strings).
    vocab:      Set of words in all documents.

    Returns:    List of floats, nBow representation.
    '''
    doc_len = len(document)
    f = []
    for i, t in enumerate(vocab):
        f.append(document.count(t) / float(doc_len))

    return f

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

def calc_wmd_dist(d1, d2, dm, vob_index_dict):

    u1 = set(d1.keys())
    u2 = set(d2.keys())
    du = u1.union(u2)

    f1 = np.array(nBOW_dict(d1, du))
    f2 = np.array(nBOW_dict(d2, du))


    dul = len(du)
    dum = np.zeros((dul, dul), dtype=np.float)
    du_list = list(du)
    processed_list = []
    for i, t1 in enumerate(du_list):
        processed_list.append(i)

        for j, t2 in enumerate(du_list):
            if j in processed_list:
                continue

            dist_matrix_x = vob_index_dict[t1]
            dist_matrix_y = vob_index_dict[t2]
            dist = dm[dist_matrix_x, dist_matrix_y]

            dum[i][j] = dist
            dum[j][i] = dist

    return emd(f1, f2, dum)



def calc_wmd(d1, d2, dm, vob_index_dict):

    u1 = set(d1)
    u2 = set(d2)
    du = u1.union(u2)

    f1 = np.array(nBOW(d1, du))
    f2 = np.array(nBOW(d2, du))


    dul = len(du)
    dum = np.zeros((dul, dul), dtype=np.float)
    du_list = list(du)
    processed_list = []
    for i, t1 in enumerate(du_list):
        processed_list.append(i)

        for j, t2 in enumerate(du_list):
            if j in processed_list:
                continue

            dist_matrix_x = vob_index_dict[t1]
            dist_matrix_y = vob_index_dict[t2]
            dist = dm[dist_matrix_x, dist_matrix_y]

            dum[i][j] = dist
            dum[j][i] = dist

    return emd(f1, f2, dum)

def get_comp_dict(comp_domain_file):

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

def filter_company_by_list(comp_dict, selected_company_list = []):
    comp_list = comp_dict.keys()

    for comp_id in comp_list:
        s = comp_dict[comp_id]
        s = [x for x in s if x in vocab_list]
        comp_dict[comp_id] = s
        if comp_id not in selected_company_list:
            del comp_dict[comp_id]

def filter_company_by_user_num(comp_dict, min_pv, min_uv):

    comp_list = comp_dict.keys()

    for comp_id in comp_list:
        s = comp_dict[comp_id]
        s = [x for x in s if x in vocab_list]
        comp_dict[comp_id] = s

        if(len(s) < min_pv):
            del comp_dict[comp_id]

        if(len(np.unique(s)) < min_uv):
            del comp_dict[comp_id]

def filter_company_by_vocab(comp_dict, vocab_list):
    comp_list = comp_dict.keys()

    for comp_id in comp_list:
        s = comp_dict[comp_id]
        s = [x for x in s if x in vocab_list]
        comp_dict[comp_id] = s



def calc_dist(x, y):
    return cosine(x, y)
#    return np.sqrt(np.sum((x - y)**2))




def get_vocab_dist_matrix(vocab_list, model):
    loop = 0
    step = 0
    print 'prepare multi task'
    pool = Pool(processes=9)

    vocab_len = len(vocab_list)
    all_num = vocab_len*vocab_len/2

    dm = np.zeros((vocab_len, vocab_len), dtype=np.float)
    dm_processed_dict = {}


    for i, t1 in enumerate(vocab_list):
#        dm_processed_dict[t1] = 1
#        for j, t2 in enumerate(vocab_list):
#            if t2 in dm_processed_dict:
#                continue
        rest_list = []
        for v in vocab_list[i+1:vocab_len]:
            rest_list.append(model[v])

        get_res = functools.partial(calc_dist, y=model[t1])
        result_dist = pool.map(get_res, rest_list)

        dm[i, i+1:vocab_len] = result_dist
        dm[i+1:vocab_len, i] = result_dist
#        dist = cosine(model[t1], model[t2])
#            dist = np.sqrt(np.sum((model[t1] - model[t2])**2))
#            dm[i][j] = dist
#            dm[j][i] = dist
        print "loop : " + str(loop)
        loop += 1
#            gap = loop - step
#            if gap > 0:
#                print "percent : " + str(float(100*loop/all_num)) + "%" + "\t" + "loop : " + str(loop) + " in all : " + str(all_num)
#                step += 100000
#            dm[i][j] = cosine(model[t1], model[t2])

    return dm

def filter_action_by_uv(comp_dict, uv=100):
    action_uv = {}
    from collections import Counter

    for comp in comp_dict:
        action_list = comp_dict[comp]
        action_dict = Counter(action_list)
        comp_dict[comp] = {k:v for (k, v) in action_dict.items() if v > uv}

def mutli_run_wmd(comp_dict, dm, vocab_list, vob_index_dict):

    wmd_pool = Pool(10)
    comp_process_list = comp_dict.keys()
    comp_num = len(comp_process_list)
    out_file = "result10"
    wfd = open(out_file, 'w+')
    for i, comp1 in enumerate(comp_process_list):
        rest_comp_list = comp_process_list[i+1:comp_num]
        d1_list = []

        for comp in rest_comp_list:
            d1_list.append(comp_dict[comp])
            get_wmd = functools.partial(calc_wmd, d2=comp_dict[comp1], dm=dm, vob_index_dict=vob_index_dict)

            dist_res_list = wmd_pool.map(get_wmd, d1_list)

        for j, dist in enumerate(dist_res_list):
            comp2 = comp_process_list[i+j+1]
            out = str(comp1) + "\t" + str(comp2) + "\t" + str(dist)
            print out
            wfd.write(out + "\n")


def calc_company_dist(res_file, comp_dict, dm, vob_index_dict):

    wfd = open(res_file, 'w+')

    processed_comp_list = []

    for comp1 in comp_dict:
        if comp1 in processed_comp_list:
            continue

        processed_comp_list.append(comp1)

        for comp2 in comp_dict:
            if comp2 in processed_comp_list:
                continue


            dist = calc_wmd_dist(comp_dict[comp1],
                                 comp_dict[comp2],
                                 dm, vob_index_dict)

            out = str(comp1) + "\t" + str(comp2) + "\t" + str(dist)
            wfd.write(out + "\n")

    wfd.close()
















def main():
    industry = sys.argv[1]
    vocab_file = "../data/" + industry + "/embed_vocab"
    model_file = "../data/" + industry + "/user_model"
    # load vocab list
    with open(vocab_file) as f:
        vocab_list = map(str.strip, f.readlines())
    # load model
    model = Word2Vec.load(model_file)

    # build vocab index dict
    vob_index_dict = {}
    for i, vob in enumerate(vocab_list):
        vob_index_dict[vob] = i

    # calc vocab dist
    logging.info("calucating vocab dist matrix")
    dm = get_vocab_dist_matrix(vocab_list, model)

    # get company domain list dict
    comp_domain_file = "../data/" + industry + "/company_file"
    comp_dict = get_comp_dict(comp_domain_file)
    logging.info("company dict generated : " + str(comp_dict.keys()))

    # delete domain not exist in vocab list
    filter_company_by_vocab(comp_dict, vocab_list)

    # filter company domain by uv : default uv > 100
    filter_action_by_uv(comp_dict, 100)

    # calc dist between two company
    res_file = "../data/" + industry + "/company_dist"
    calc_company_dist(res_file, comp_dict, dm, vob_index_dict)


# company_list_file = "../data/" + industry + "/company_uv_list"
# fd = open(company_list_file)
# selected_company_list = []

# for line in fd:
#     company_id = line.strip()
#     selected_company_list.append(company_id)
# fd.close()

# filter_company_by_list(comp_dict, selected_company_list)

# filter_company_by_vocab(comp_dict, vocab_list)
# mutli_run_wmd(comp_dict, dm, vocab_list, vob_index_dict)


if __name__ == "__main__":
    main()
