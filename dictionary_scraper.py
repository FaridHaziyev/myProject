import requests
from bs4 import BeautifulSoup
import pickle
import pdb
import re



with open("../created_datas/enfa_en_vocab.pkl", "rb") as fr:
    eng_words = pickle.load(fr)



def get_words(enwords):
    fw = open("tired.txt", "w")
    for word in enwords:
        try:
            r = requests.post("https://aryanpour.com/English-to-Persian.php", data=dict(
                keyword = word))
            souped = BeautifulSoup(r.text, "html.parser")
            words = souped.find("td").getText()

            if "Your keyword was not found" not in words:
                words = re.findall(r"\b[^\W\da-zA-Z]{3,}\b", words)
                print(f"{word}\t{words}", file = fw)
        except:
            continue


get_words(eng_words)
