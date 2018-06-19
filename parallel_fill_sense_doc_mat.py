#In this Module wikipairs are used and pages are
#created for each pair, and in this pages content 
#of english and german wikipage is also added,

from xml.dom.minidom import parse, parseString
from nltk.corpus import wordnet,stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import pdb
import re
import pickle
import multiprocessing as mp

stopWords = set(stopwords.words("english"))
lmtzr = WordNetLemmatizer()


with open("../created_datas/vocab_weights.pkl", "rb") as fr:
    vocab_weights = pickle.load(fr)

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
    links_child = page.getElementsByTagName("Links")[0].firstChild
    if not links_child:
        return set()
    links = links_child.data
    links = links.replace("\n", " ").replace("\t"," ")
    links = set(re.findall("\w+", links))
    return links

def get_cattegories(page):
    categories_child = page.getElementsByTagName("English_Categories")[0].firstChild
    if not categories_child:
        return set()
    cattegories = categories_child.data
    cattegories = cattegories.replace("\n", " ").replace("\t", " ")
    cattegories = set(re.findall("\w+", cattegories))
    return cattegories

def get_content(page, language):
    #here prepositions should be removed
    contents = page.getElementsByTagName(language)[0].firstChild.data
    contents = contents.replace("\n", " ").replace("\t", " ")
    contents = re.findall("\w+", contents)
    return contents  
    

def get_possible_words(eng_content, german_content, deu_en_dict): 
    """words that have sense in wordnet and translation in german"""
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
            content_translations.items() if translations and len(word) > 2}
 
def getSynsetId(synset):
    return (8-len(str(synset.offset())))*"0" + str(synset.offset()) + "-" + synset.pos()

def get_sense_contexts(synsets):
    sense_contexts = {}  
    for s in synsets:
        hypernyms = s.hypernyms()
        synonyms = [x for x in synsets if x != s]
        sisterhood = []

        for h in hypernyms:
            hyponyms = [x for x in h.hyponyms() if x != s]
            sisterhood.extend(hyponyms)
        
        allsenses = set(hypernyms + synonyms + sisterhood + s.hyponyms() +
                s.member_meronyms() + s.substance_meronyms() + s.part_meronyms() +
                s.member_holonyms() + s.substance_holonyms() + s.part_holonyms()) 
        sense_lemmas = []
        for syn_s in allsenses:
            lemmas = syn_s.lemmas()
            sense_lemmas.extend(lemmas)
        sense_lemmas = set(sense_lemmas)
        sense_lemmas = set(map(lambda x: x.name(), sense_lemmas))
        
        s_context = [x.lower() for x in sense_lemmas if x not in stopWords and len(x) > 3]
       
        sense_contexts[s] = set(s_context)

    return sense_contexts

def get_word_count(english_content):
    word_count = {}
    for w in english_content:
        word_count[w] = word_count.get(w,0) + 1
    return word_count

def get_definition_words(synset):
    definition = synset.definition()
    pdb.set_trace()
    return set(re.findall("\w+", definition))

def calc_avg_score(a,b):
    if check_avg_score(a,b):
        return (a+b)/2
    return 0

def calc_def_score(sense_context, page_context):
    intersection = sense_context.intersection(page_context)
    score = 0

    for word in intersection:
        score += vocab_weights.get(word,0)

    return score

def check_avg_score(a,b):
    if a == 0 and b == 0:
        return False
    return True    

def get_champ(pos_synsets, page_context):
    max_score = [0,None]

    for synset in pos_synsets:
        sense_context = get_definition_words(synset)
     
        score = calc_def_score(sense_context, page_context)
        
        if score > max_score[0]:
            max_score[0] = score
            max_score[1] = synset.name()

    if max_score[0] > 0:
        return max_score[1]


def tag_content(possible_words_dict, wn, english_content):
    tagged_content = {}

    for word in possible_words_dict:
        pos_synsets = wn.synsets(word)
        def_synset = get_champ(pos_synsets,english_content)

        if def_synset:
            tagged_content[word] = def_synset
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
        possible_words_dict = get_possible_words(eng_content, deu_content, deu_en_dict)

        tagged_english_words = tag_content(possible_words_dict, wordnet, 
                                           eng_content)

        senses_found = list(tagged_english_words.values())

        for sense in senses_found:
            print(sense + "\t" + str(index), file = fw)

        index += 1



if __name__ == "__main__":
    all_pages = []
    with open("../merged_eng_deu_dict.pkl", "rb") as dep:
        deu_en_dict = pickle.load(dep)

    wikipages = load_xml_data("../created_datas/x1")  #to load wikipages
    wikipairs = get_all_pairs(wikipages) #to get all wikipairs
    print(len(wikipairs))
    fill_sense_doc_mat(wikipairs, 1,0)
    """n = 800
    threads = []
    p_length = len(wikipairs) // n
    threads = []
    for i in range(n):
        start = i*p_length
        if i == n - 1:
            end = len(wikipairs)           
            threads.append(mp.Process(target= fill_sense_doc_mat, args = (wikipairs[start:end],
                i, p_length,)))
        else:
            end = i*p_length + p_length
            threads.append(mp.Process(target= fill_sense_doc_mat, args = (wikipairs[start:end],
                i, p_length,)))
    a = 40
    b = 20
    for x in range(a):
        for y in range(b):
            threads[x*b+y].start()
        for z in range(b):
            threads[x*b+z].join()"""
