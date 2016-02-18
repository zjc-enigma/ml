#coding:utf-8
import os
import sys
sys.path.append("../lib")
import numpy as np
import read_conf

industry = sys.argv[1]


#word2vec_training_cmd = """python word2vec.py ../data/finance/user_file ../data/finance/user_model ../data/finance/user_vector"""
#read_conf.exec_cmd(word2vec_training_cmd)
embed_data_path = "../data/" + industry + "/embed_dat"
embed_vocab_path = "../data/" + industry + "/embed_vocab"
vector_model_path = "../data/" + industry + "/user_vector"
if os.path.exists(embed_data_path):
    os.remove(embed_data_path)

if os.path.exists(embed_vocab_path):
    os.remove(embed_vocab_path)

if not os.path.exists(embed_data_path):
    print("Caching word embeddings in memmapped format...")
    from gensim.models.word2vec import Word2Vec
    wv = Word2Vec.load_word2vec_format(vector_model_path,  binary=True)
    print "wv syn0norm shape : " + str(wv.syn0norm.shape)
    fp = np.memmap(embed_data_path, dtype=np.double, mode='w+', shape=wv.syn0norm.shape)
    fp[:] = wv.syn0norm[:]
    with open(embed_vocab_path, "w") as f:
        for _, w in sorted((voc.index, word) for word, voc in wv.vocab.items()):
            f.write(w + "\n")

    del fp, wv
