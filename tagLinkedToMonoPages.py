import pickle
import re
import pdb

def tag_linked_pages():
    with open("created_datas/all_page_onlymono_tagged.pkl", "rb") as ft:
        all_pages = pickle.load(ft) #get all pages, where mono pages are tagged

    mapped_pages = {}
    for page in all_pages:
        if page.synset:
            mapped_pages[page.name] = page.synset  #put mapped monosemious pages in a dictionary in word : synset format
    cc = 0

    for page in all_pages:
        if page.synset:
            continue
        for m_p in mapped_pages:
            mparts = re.findall("\w+", m_p)
            if any(p.lower() in page.links for p in mparts):
                sn = mapped_pages[m_p]
                if sn in page.possible_synsets:
                    print(cc)
                    cc += 1
                    page.synset = sn
                    break


    with open("all_page_mono_and_link_tagged.pkl", "wb") as fw:
        pickle.dump(all_pages, fw)
    
    pages_with_synset = []
    for page in all_pages:
        if page.synset:
            pages_with_synset.append(["en : " + page.actual_name, page.synset])

    with open("mono_and_link_tagged_tuple.pkl", "wb") as fm: #to get the list of tuples format  [("en : pagename", page.Synset) ...]
        pickle.dump(pages_with_synset, fm)
