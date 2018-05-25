import pickle
import scipy.sparse as sp
import math
import pdb

with open("sense_doc_dict.pkl", "rb") as sd:
    sense_doc_dict = pickle.load(sd)

index = 0
rows = []
cols = []
data = []
sense_index_dict = {} #sense and its index in sparse matrix

for sense in sense_doc_dict:
    sense_index_dict[sense] = index
    for doc in sense_doc_dict[sense]:
        rows.append(index)
        cols.append(doc)
        data.append(math.log10(2)*math.log10(852311/len(sense_doc_dict[sense])))
    index += 1
    print(index)


sense_doc_mtx = sp.csc_matrix((data, (rows, cols)), shape=(len(set(rows)), 852311))
sp.save_npz('../created_datas/en_sense_doc_matrix.npz', sense_doc_mtx)
 
sense_index_file = open("../created_datas/en_sense_index_dict.pkl", "wb")

pickle.dump(sense_index_dict, sense_index_file)

