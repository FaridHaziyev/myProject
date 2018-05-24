#get the page names of the target language from wikipedia
from igraph import *
import pickle

def getNames(graph, lang, output_name):
    g = Graph.Read_Picklez(graph)
    
    page_names = [x["word"] for x in g.vs if x["lang"] == lang] #get vertice names for the given language
    with open(output_name, "wb") as fw:
        pickle.dump(page_names, fw)

