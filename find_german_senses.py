from sklearn.preprocessing import normalize
import scipy.sparse as sp
import pickle
import numpy as np
from nltk.corpus import wordnet
import pdb

deu_matr = sp.load_npz("../created_datas/deu_term_doc_matrix.npz")
eng_sense_matr = sp.load_npz("../created_datas/en_sense_doc_matrix.npz")

with open("../created_datas/en_sense_index_dict.pkl", "rb") as esd:
    eng_sense_index = pickle.load(esd)

eng_index_sense = {v:k for k,v in eng_sense_index.items()}

with open("../created_datas/deu_word_index_dict.pkl", "rb") as dwi:
    deu_word_ind = pickle.load(dwi)

deu_matr = deu_matr.tocsr()
eng_sense_matr = eng_sense_matr.tocsr().transpose()

deu_norm = normalize(deu_matr, norm="l2", axis=1)
eng_norm = normalize(eng_sense_matr, norm = "l2", axis = 0)

"""a1 = deu_matr[0:1000,:].dot(eng_sense_matr)
a2 = np.argmax(a1, axis = 1)
a3 = [x[0] for x in a2.tolist()]
pdb.set_trace()"""

a1 = deu_norm.dot(eng_norm)
pdb.set_trace()
a2 = np.argmax(a1, axis = 1)
a3 = [x[0] for x in a2.tolist()]
pdb.set_trace()
a4 = [(x,a3[x]) for x in range(len(a3))]

def getSynsetId(syn):
    synset = wordnet.synset(syn)
    return (8-len(str(synset.offset())))*"0" + str(synset.offset()) + "-" + synset.pos()

fw = open("../resuls_deu.txt", "w")
"""for index,val in enumerate(a3):
    print(deu_word_ind[index] + "\t" + str(eng_index_sense[val]), file = fw)"""

for x in a4:
    print(deu_word_ind[x[0]] + "\t" + getSynsetId(str(eng_index_sense[x[1]])), file = fw)

