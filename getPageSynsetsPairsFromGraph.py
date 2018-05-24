from igraph import *
import pdb

def get_page_synset_pairs(graph_name, language, output_name):
    """To get the sense tagged vertices from the target language in   (word \t synsets) format"""

    g = Graph.Read_Picklez(graph_name)  #to load the tagged graph
    tagged_vertices = [v for v in g.vs if v["Synsets"] and v["lang"] == language]
    with open(output_name, "w") as fw:
        for vertex in tagged_vertices:
            word = vertex["word"]

            print(f"{word}\t{vertex['Synsets']}", file = fw)
    
    
