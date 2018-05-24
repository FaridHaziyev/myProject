from igraph import *
import pickle
import pdb


def add_synsets(graph_name, eng_tagged_pages, output_name):
    #this graph contains all the pairs from the wikipairs. However synsets are not added.
    g = Graph.Read_Picklez(graph_name)

    print("graph is loaded")
    #previously tagged english wikinames are extracted
    with open(eng_tagged_pages, "rb") as f:                             
        taggeds_ = pickle.load(f)
    
    taggeds = {}
    for p_t in taggeds_:
        taggeds[p_t[0]] = p_t[1] 

   
    print("english pages are loaded")

    #all the vertices that are in the tagged dictionary are tagged with corresponding synsets
    for vertex in g.vs:                                                     
        if vertex["name"] in taggeds:                                         
            vertex["Synsets"] = taggeds[vertex["name"]]

    print("English synsets are added to the graph")


    """while True:
        changed = 0
        for e in g.es():
            source, target = g.vs[e.source], g.vs[e.target]

            if source["Synsets"] and target["Synsets"] is None:
                changed += 1
                pdb.set_trace()     
                target["Synsets"] = source["Synsets"]

            elif target["Synsets"] and source["Synsets"] is None:
                changed += 1
                pdb.set_trace()     
                source["Synsets"] = target["Synsets"]     

        print(f"{changed} vertices are mapped with synsets")
        if not changed:
            break"""
    f_deu_eng = open("english_deu_prr.txt", "w")
    for e in g.es():
        source, target = g.vs[e.source], g.vs[e.target]

        if source["Synsets"] and target["Synsets"] is None:
            if source["lang"] == "de" or target["lang"] == "de":   
                print(f"{source['name']}\t{target['name']}", file = f_deu_eng)
            target["Synsets"] = source["Synsets"]

        elif target["Synsets"] and source["Synsets"] is None:
            if source["lang"] == "de" or target["lang"] == "de":   
                print(f"{source['name']}\t{target['name']}", file = f_deu_eng)
            source["Synsets"] = target["Synsets"]

    g.write_picklez(output_name)
