from sklearn.preprocessing import normalize
import scipy.sparse as sp
import pickle
import numpy as np
from nltk.corpus import wordnet
import pdb
from collections import defaultdict

deu_matr = sp.load_npz("../created_datas/deu_term_doc_matrix.npz")
eng_sense_matr = sp.load_npz("../created_datas/en_sense_doc_matrix.npz")


with open("../created_datas/en_sense_index_dict.pkl", "rb") as esd:
    eng_sense_index = pickle.load(esd)


def tag_words(deu_m, eng_m):
    word_sense_matr = deu_m.dot(eng_m)
    word_sense_matr = word_sense_matr.tocoo()
    w_s_dict = defaultdict(list)

    temp = []
    rn = 0
    for (row,col,score) in zip(word_sense_matr.row, word_sense_matr.col, word_sense_matr.data):
        if row != rn:
            temp_sorted = sorted(temp, key = lambda x:x[1], reverse = True)
            
            if len(temp_sorted) > 10:
                temp_sorted = temp_sorted[:10]
            w_s_dict[rn] = temp_sorted
            rn = row
            temp = []
        temp.append((col, score))


    word_tag = defaultdict(list) #key-word value-synsets

    for w, senses in w_s_dict.items():
        word = deu_word_ind[w]
        for s in senses:
            s_ = eng_index_sense[s[0]]
            ws = wordnet.synset(s_) #synset in the wordnet

            lemmas = [lem.name() for lem in ws.lemmas()]
            if any(x for x in lemmas if x in deu_eng[word]):
                synset_ = getSynsetId(s_)
                word_tag[word].append(synset_)

    fw = open("tagged_file.txt", "w")
    for word, synset in word_tag.items():
        print(f"{word}\t{synset}", file = fw)

def getSynsetId(syn):
    synset = wordnet.synset(syn)
    return (8-len(str(synset.offset())))*"0" + str(synset.offset()) + "-" + synset.pos()




if __name__ == "__main__":
    eng_index_sense = {v:k for k,v in eng_sense_index.items()}

    with open("../created_datas/deu_word_index_dict.pkl", "rb") as dwi:
        deu_word_ind = pickle.load(dwi)

    with open("../merged_deu_eng_dict.pkl", "rb") as f:
        deu_eng = pickle.load(f)

    deu_matr = deu_matr.tocsr()
    eng_sense_matr = eng_sense_matr.tocsr().transpose()

    tag_words(deu_matr, eng_sense_matr)











