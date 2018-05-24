from nltk.corpus import wordnet,stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import pickle
from collections import defaultdict
import pdb


stopWords = set(stopwords.words("english"))
lmtzr = WordNetLemmatizer()

en_vocab_file = open("../created_datas/en.vocab")
en_vocab_with_senses = {}
en_word_senses = defaultdict(list) #to keep all senses of a word in a dictionary

for line in en_vocab_file:
    word = lmtzr.lemmatize(line.strip().lower())
    senses =  wordnet.synsets(line.strip())

    if senses:
        for sense in senses:
            en_word_senses[word].append(sense.name())
            en_vocab_with_senses[sense.name()] = []



with open("../created_datas/en_vocab_with_senses.pkl", "wb") as fw:
    pickle.dump(en_vocab_with_senses, fw)

with open("../created_datas/en_words_wsynsets.pkl", "wb") as ws:
    pickle.dump(en_word_senses, ws)
