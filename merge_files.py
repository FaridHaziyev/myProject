import os
import csv
import pdb
import pickle
from collections import defaultdict

files = os.listdir("files")

all_merged = defaultdict(set)

with open("../created_datas/sense_doc_dict_empty.pkl", "rb") as ev:
    sense_doc_dict = pickle.load(ev)

for f_ in files:
    with open("files/" + f_, "r") as fr:
        for line in fr:
            sense_doc = line.strip().split("\t")
            if sense_doc[0] not in sense_doc_dict:
                continue

            all_merged[sense_doc[0]].add((int(sense_doc[2]), int(sense_doc[1])))

with open("sense_doc_dict.pkl", "wb") as fw:
    pickle.dump(all_merged, fw)
