import re
from xml.dom import minidom
from nltk.corpus import wordnet, stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import pdb
import pickle

#-----------------------PARAMETERS--------------------------------------------------
id_pattern = re.compile('<articlePair id=".+">')
eng_name_pattern = re.compile('<article lang="en" name=".+">')
category_pattern = re.compile('<categories name.+')
deu_name_pattern = re.compile('<article lang="de" name=".+">')
link_pattern = re.compile("<link target=[^>]+")
#------------------------------------------------------------------------------------------

stopWords = set(stopwords.words("english"))
german_stop_words = set(stopwords.words("german"))

lmtzr = WordNetLemmatizer()
tree = minidom.Document()
root = tree.createElement("DATA")
tree.appendChild(root)

with open("wikicomp-2014_deen.xml.bz2?dl=0.out") as pair_text:
    flag = False
    cc = 0    
    for line in pair_text:
        pdb.set_trace()
        if re.match("<content>", line):
            flag  = True
            continue
        elif re.match("</content>", line):
            flag = False
            continue
        links = re.findall(link_pattern, line)
        if re.match(id_pattern, line):  #to get pairs from wikipedia
            print(cc)
            cc += 1
            pid = re.search("\d+", line).group() #to get the pair id
            pair = tree.createElement("Pair")
            pairid = tree.createElement("Pair_Id")
            pairid.appendChild(tree.createTextNode(pid))
            pair.appendChild(pairid)
            root.appendChild(pair)
        
        elif re.match(eng_name_pattern, line): #to get english page name of the pair
            p_name = re.search('name="[^>]+', line).group()
            p_name = p_name.replace('name="', "").replace('"', "")
            
            actual_pname = p_name
                
            if "(" in p_name:
                parts = p_name.split(" (")
                if len(parts) > 1:
                    definition = parts[1][:-1]
                    def_words = re.findall("\w+", definition)
                    p_name = parts[0]
               
            name = lmtzr.lemmatize(p_name)
            name_node = tree.createElement("Name")
            actual_name_node = tree.createElement("Actual_Name")
            name_node.appendChild(tree.createTextNode(name))
            actual_name_node.appendChild(tree.createTextNode(actual_pname))
            lang = tree.createElement("Target")
            pair.appendChild(lang)
            lang.appendChild(name_node)
            lang.appendChild(actual_name_node)
            links_node = tree.createElement("Links")
            content_node = tree.createElement("English_Content")
            categories_node = tree.createElement("English_Categories")

            lang.appendChild(links_node)
            lang.appendChild(content_node)
            lang.appendChild(categories_node)

        elif re.match(deu_name_pattern, line): #to get german page name of the pair
            p_name = re.search('name="[^>]+', line).group()
            p_name = p_name.replace('name="', "").replace('"', "")
               
            name = lmtzr.lemmatize(p_name)
            name_node = tree.createElement("Name")
            actual_name_node = tree.createElement("Actual_Name")
            name_node.appendChild(tree.createTextNode(name))
            actual_name_node.appendChild(tree.createTextNode(actual_pname))
            lang = tree.createElement("Source")
            pair.appendChild(lang)
            lang.appendChild(name_node)
            lang.appendChild(actual_name_node)
            links_node = tree.createElement("Links")
            content_node = tree.createElement("German_Content")
            categories_node = tree.createElement("German_Categories")

            lang.appendChild(links_node)
            lang.appendChild(content_node)
            lang.appendChild(categories_node)

        elif re.match(category_pattern, line): #to get the categories
           #to select categories line and tokenize for the words
            stopWords = german_stop_words if categories_node.nodeName == "German_Categories" else stopWords
            
            categories = re.search("name[^/]+", 
                    line).group().replace('name="', "")[:-1].split("|")
           
            words = [word for category in categories for word in
                                     list(map(lambda x: lmtzr.lemmatize(x.lower()), 
                                          re.findall(r"\b[^\d\W]{3,}\b",category))) 
                                     if word not in  stopWords]
                          
            categories_node.appendChild(tree.createTextNode(",".join(words)))
            
        elif flag: #to get the content
            stopWords = german_stop_words if content_node.nodeName == "German_Content" else stopWords

            tochange = {"<p>":" ", "</link>":" ", "</p>":" ",
                    "<cell>":" ","</cell>":" ", "\n":" ", "\t":" "}
            pattern = re.compile("|".join(tochange.keys()))
            text = pattern.sub(lambda m: tochange[m.group()], line)

            words =  [x for x in [lmtzr.lemmatize(word.lower()) for 
                                word in re.findall(r"\b[^\d\W]{3,}\b",
                                re.sub("<link target=.+?>","",text))] 
                                if x not in stopWords]

            content_node.appendChild(tree.createTextNode(",".join(words)))

        if links:
            links = [link.replace('<link target="', "")[:-1] for link in links]
            links_str = ",".join([word for link in links 
                                for word in 
                                    [lmtzr.lemmatize(x.lower())  
                                    for x in re.findall(r"\b[^\d\W]{3,}\b", link)] 
                                if word not in stopWords])
            
            links_node.appendChild(tree.createTextNode(links_str))
                
#xml_str = tree.toprettyxml(indent = "\t")

tree.writexml(open("almancaingilize.xml","w"))


"""with open(save_path_file, "w", encoding = "utf-8") as f:
    f.write(xml_str)"""
