from scipy.sparse import lil_matrix, csc_matrix
import scipy.sparse as sp
import pdb
import pickle
import math

rows = []
cols = []
data = []


deu_vocab = {}
index_dict = {}
v_index = 0
index = -1
real_index = 0

with open("../created_datas/de.vocab") as voc:
    for line in voc:
        word = line.strip()
        if not any(x.isdigit() for x in word):
            deu_vocab[real_index] = word
            index_dict[v_index] = real_index
            real_index += 1

        v_index += 1

flag = False
with open("../created_datas/de.matrix", "r") as de_mtx:
    for line in de_mtx:
        parts = line.strip().split(" ")
        if len(parts) == 2 and flag:
            rows.append(index_dict[index])
            cols.append(int(float(parts[0])))
            data.append((math.log10(1+int(float(parts[1]))))*math.log10(852311/doc_in))
        
        elif len(parts) == 1:
            doc_in = int(parts[0])
            index += 1
            if index in index_dict:
                flag = True
            else:
                flag = False

            print(index)
pdb.set_trace()
with open("deu_word_index_dict.pkl","wb") as dw:
    pickle.dump(deu_vocab, dw)

term_doc_mtx = csc_matrix((data, (rows, cols)), shape=(len(index_dict), 852311))
sp.save_npz('deu_term_doc_matrix.npz', term_doc_mtx)
