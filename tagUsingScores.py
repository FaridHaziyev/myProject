import pickle
import re
import pdb


def tag_with_scores():
    with open("created_datas/all_page_onlymono_tagged.pkl", "rb") as ft:
        all_pages = pickle.load(ft) #get all pages, where mono pages are tagged

    mapped_pages = {}
    for page in all_pages:
        if page.synset:
            mapped_pages[page.name] = page.synset  #put mapped monosemious pages in a dictionary in word : synset format


    for page in all_pages:
        if page.name in mapped_pages:
            continue
        else:
            max_score = [0,None]
            for synset in page.possible_synsets:
                cntx = page.cattegories + page.links + page.explanations
                inters = set(cntx).intersection(page.sense_contexts[synset])
                
                count = len(inters) / len(cntx)

                if count > max_score[0]:
                    max_score[0] = count
                    max_score[1] = synset

            if max_score[0] > 0:
                page.synset = max_score[1]
                
                
    with open("all_pages_mono_link_and_score_tagged.pkl", "wb") as fw:
        pickle.dump(all_pages, fw)
    
    pages_with_synset = []
    for page in all_pages:
        if page.synset:
            pages_with_synset.append(["en : " + page.actual_name, page.synset])

    with open("mono_and_score_tagged_tuple.pkl", "wb") as fm: #to get the list of tuples format  [("en : pagename", page.Synset) ...]
        pickle.dump(pages_with_synset, fm) 
