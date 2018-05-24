from collections import defaultdict

word_synsets_dict = defaultdict(set)

with open("deu_tagged.txt", "r") as fr:
    for line in fr:
        parts = line.strip().split("\t")
        word = parts[0]
        synset = parts[1]
        word_synsets_dict[word].add(synset)


with open("eng_deu_tagged.txt", "w") as fw:
    for word,synsets in word_synsets_dict.items():
        print(f"{word}\t{synsets}", file = fw)

