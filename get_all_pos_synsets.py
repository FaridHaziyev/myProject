from nltk.corpus import wordnet,stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import pickle
from collections import defaultdict
import pdb


stopWords = set(stopwords.words("english"))
lmtzr = WordNetLemmatizer()

en_vocab_file = open("../created_datas/en.vocab")


for line in en_vocab_file:
    word = lmtzr.lemmatize(line.strip().lower())
    sense = wordnet.synsets(word)
    if sense:
        pdb.set_trace()
