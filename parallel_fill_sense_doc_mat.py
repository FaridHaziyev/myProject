#In this Module wikipairs are used and pages are
#created for each pair, and in this pages content 
#of english and german wikipage is also added,
#most frequent 10 words in the content are added.

from xml.dom.minidom import parse, parseString
from nltk.corpus import wordnet,stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import pdb
import re
import pickle
import multiprocessing as mp

stopWords = set(stopwords.words("english"))
lmtzr = WordNetLemmatizer()

class Page:
    def __init__(self, page_id, source_actual,target_actual,lemmatized_name,
                       source_content, target_content, words_context, pos_synsets, s_contexts, possible_words):

        self.page_id = page_id
        self.source_actual_name = source_actual
        self.target_actual_name = target_actual
        self.target_lemmatized_name = lemmatized_name
        self.possible_words = possible_words #words that may be tagged
        self.source_content = source_content
        self.target_content = target_content
        self.words_context = words_context
        self.possible_synsets = pos_synsets
        self.sense_contexts = s_contexts
    def __repr__(self):
        return f"Page id : {str(self.page_id)}\nPage name : {self.name}\nWords Context : {self.words_context}"


def load_xml_data(data_name):
    wikipairs_data = parse(data_name)
    return wikipairs_data

def get_all_pairs(xml_tree):
    all_pairs = xml_tree.getElementsByTagName("Pair")
    return all_pairs


def get_page_id(pair):
    p_id = pair.getElementsByTagName("Pair_Id")[0]
    return p_id.firstChild.data

def get_source(pair):
    source = pair.getElementsByTagName("Source")[0]
    return source

def get_target(pair):
    target = pair.getElementsByTagName("Target")[0]
    return target

def get_page_actual_name(page):
    page_ = page.getElementsByTagName("Actual_Name")[0]
    return page_.firstChild.data

def get_page_name(page):
    page_ = page.getElementsByTagName("Name")[0]
    return page_.firstChild.data


def check_existence_in_wordnet_bool(page_name):
    """Remove the pages, whose name can not be in wordnet"""
    synsets = wordnet.synsets(page_name)
    
    if synsets:
        return True
    return False

            
def get_definitions(page_actual_name):        
    definition = page_actual_name.split(" (")
    if len(definition) == 1:
        return None
    definition_words = re.findall("\w+", definition[1].replace(")", ""))
    return definition_words    

        
def get_possible_synsets(definition_words, page_name):
    """If none of the words in the definition of synset matches the"""
    """definition words then remove that synset"""
    synsets = wordnet.synsets(page_name)
    pos_synsets = synsets.copy()
    if definition_words is None:
        return pos_synsets
    for synset in synsets:
        if not any(exp.lower() in synset.definition() for exp in definition_words):
            pos_synsets.remove(synset)

    return pos_synsets


def get_links(page):
    links = page.getElementsByTagName("Links")[0].firstChild.data
    links = links.replace("\n", " ").replace("\t"," ")
    links = set(re.findall("\w+", links))
    return links

def get_cattegories(page):
    cattegories = page.getElementsByTagName("English_Categories")[0].firstChild.data
    cattegories = cattegories.replace("\n", " ").replace("\t", " ")
    cattegories = set(re.findall("\w+", cattegories))
    return cattegories

def get_content(page, language):
    #here prepositions should be removed
    contents = page.getElementsByTagName(language)[0].firstChild.data
    contents = contents.replace("\n", " ").replace("\t", " ")
    contents = re.findall("\w+", contents)
    return contents  
    

def get_possible_words(eng_content, german_content, deu_en_dict, prepositions): 
    """words that have sense in wordnet and translation in german"""
    #content_count = [(word,eng_content.count(word)) for word in eng_content]
    #content_top = [word for (word,count) in sorted(content_count, key = lambda x: x[1], reverse = True)]
    #if len(content_top) > 10:
        #content_top = content_top[0:10]

    #check if the word is in wordnet
    content_top = eng_content  
    content_pos = [x for x in content_top if wordnet.synsets(x)]     
    
    #get translations of those words from bilingual dictionary
    content_translations = [(x, deu_en_dict.get(x)) for x in content_pos]
    content_translations = {word:translations for (word,translations) in content_translations if
            translations}
    
    #get only the words that have a translation in the german part
    for word in content_translations:
        translations = content_translations[word].copy()
        for translation in content_translations[word]:
            if translation not in german_content:
                translations.remove(translation)

        content_translations[word] = translations
        
                
    
    return {word:translations for word, translations in
            content_translations.items() if translations and word not in prepositions}
 
def getSynsetId(synset):
    return (8-len(str(synset.offset())))*"0" + str(synset.offset()) + "-" + synset.pos()

def get_sense_contexts(synsets):
    sense_contexts = {}  
    for s in synsets:
        alsenses = []
        hypers = s.hypernyms()
        alsenses.extend(hypers)
        alsenses.extend(s.hyponyms())
        
        synonyms = [x for x in synsets if x != s]
        alsenses.extend(synonyms)
        sisterhood = []

        for hyper in hypers:
            hyp = hyper.hyponyms()
            hyp = [x for x in hyp if x != s]
            sisterhood.extend(hyp)
        
        alsenses.extend(sisterhood)
        sense_lemmas = []
        for syn_s in alsenses:
            lemmas = syn_s.lemmas()
            sense_lemmas.extend(lemmas)
        sense_lemmas = set(sense_lemmas)
        sense_lemmas = set(map(lambda x: x.name(), sense_lemmas))
        
        s_context = [x.lower() for x in sense_lemmas if x not in stopWords and len(x) > 1]
        sn = getSynsetId(s)
        sense_contexts[sn] = s_context

    return sense_contexts


def get_definition_words(synset):
    definition = synset.definition()
    return set(re.findall("\w+", definition))

def tag_content(possible_words_dict, wn, english_content):
    tagged_content = {}
    for word in possible_words_dict:
        pos_synsets = wn.synsets(word)
        max_score = [0, None]
        for synset in pos_synsets:
            def_words = get_definition_words(synset)
            intersection = len(def_words.intersection(english_content))
            score = intersection / len(english_content)
            if score > max_score[0]:
                max_score[0] = score
                max_score[1] = synset.name()
        
        if max_score[0] > 0:
            tagged_content[word] = max_score[1]

    return tagged_content

def map_eng_to_deu(tagged_eng, eng_deu_translations_dict):
    deu_tagged = {}
    for eng_word in tagged_eng:
        if len(eng_deu_translations_dict[eng_word]) > 1:
            continue 
        deu_tagged[list(eng_deu_translations_dict[eng_word])[0]] = tagged_eng[eng_word]

    return deu_tagged


def fill_sense_doc_mat(part, count, part_len):
    index = count*part_len

    fw = open("files/" + str(count) + ".txt", "w")
    for pair in part:
        source = get_source(pair) # to get the source language part
        target = get_target(pair) #to get the target language part
        eng_content = get_content(target, "English_Content")
        deu_content = set(get_content(source, "German_Content"))
        
        #returns words with translations word:translations
        possible_words_dict = get_possible_words(eng_content, deu_content, deu_en_dict, prepositions)

        tagged_english_words = tag_content(possible_words_dict, wordnet,
            eng_content)
        senses_found = list(tagged_english_words.values())

        #results = []
        for sense in senses_found:
            print(sense + "\t" + str(index), file = fw)
            #results.append((sense, index))
        index += 1
    #return results



if __name__ == "__main__":
    all_pages = []
    prepositions = {'despite', 'beyond', 'around', 'through', 'after', 'off', 'until', 'near', 'concerning', 'across', 'up', 'below', 'in', 'except', 'without', 'from', 'instead', 'before', 'beneath', 'inspite', 'upon', 'by', 'of', 'outside', 'against', 'over', 'on', 'but', 'within', 'throughout', 'among', 'behind', 'with', 'during', 'into', 'underneath', 'for', 'to', 'about', 'under', 'besides', 'along', 'out', 'beside', 'at', 'above', 'toward', 'inside', 'since', 'between', 'regarding', 'like', 'front', 'because', 'onto', 'down', "the", "and",
"that","than", "is", "he", "she", "it", "we", "you", "they", "a","an", "am", "are", "or","term", "much", "many","any", "have","has", "had",
"having"}

    with open("../eng_deu_dict.pkl", "rb") as dep:
        deu_en_dict = pickle.load(dep)

    with open("../created_datas/sense_doc_dict_empty.pkl", "rb") as ev:
        sense_doc_dict = pickle.load(ev)

    wikipages = load_xml_data("../created_datas/wikipair_de_en.xml")  #to load wikipages
    wikipairs = get_all_pairs(wikipages) #to get all wikipairs

    n = 20
    threads = []
    p_length = len(wikipairs) // n

    for i in range(n):
        start = i*p_length
        if i == n - 1:
            end = len(wikipairs)           
            mp.Process(target= fill_sense_doc_mat, args = (wikipairs[start:end],
                i, p_length,)).start()
        else:
            end = i*p_length + p_length
            mp.Process(target= fill_sense_doc_mat, args = (wikipairs[start:end],
                i, p_length,)).start()

    """with open("some_file.txt", "w") as sf:
        print(f"Index:{index}")
    
    with open("sense_doc_dict_updated.pkl", "wb") as su:
        pickle.dump(sense_doc_dict, su)"""
