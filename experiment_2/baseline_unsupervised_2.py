import sys
import random
import pickle
from collections import defaultdict
import utils.morph_analyzer as ma
#from nltk.tag import CRFTagger

def load_data(filename, column=0):
    with open(filename, "r+") as r:
        return [s.strip().split("\t")[column].split() for s in r]

def first_analyze(data, stats_data):
    new_data = []
    statistics = ma.statistics(data + stats_data)
    ptags = defaultdict(list)
    root_dict = defaultdict(int)
    deri_dict = defaultdict(int)
    infl_dict = defaultdict(int)
    for word in data + stats_data:
        roots = ma.find_roots(word, statistics)
        derivations = ma.find_derivations(word)
        inflections = ma.find_endings(word)
        for i in range(len(word)):
            ptag = []
            if any(x[1] == i for x in roots):
                ptag.append("R")
                root_dict[word[i]] += 1
            if any(x[1] == i for x in inflections):
                ptag.append("I")
                infl_dict[word[i]] += 1
            elif any(x[1] == i for x in derivations):
                ptag.append("D")
                deri_dict[word[i]] += 1
            ptags["".join(word)].append(ptag)
    def best_root(morph, word):
        r = root_dict[morph]
        return r == max(root_dict[morph2]/(root_dict[morph2] + deri_dict[morph2]+ infl_dict[morph2])for morph2 in word)

    for word in data:
        tag = ""
        first_root = False
        for i in range(len(word)):
            morph = word[i]
            poss = ptags["".join(word)][i]
            new_tags = []
            r, d, f = root_dict[morph], deri_dict[morph], infl_dict[morph]

            td = {"R":r, "D":d, "I":f}
            if r == max([r,d,f]):
                tag += "R"
                first_root = True
            elif (f == max([r,d,f]) and (i == 0 or i == len(word) - 1)):
                tag += "I"
            else:# d  == max([r,d,f]):
                if first_root:
                    tag += "S"
                else:
                    tag += "P"
        print(" ".join(word) + "\t" + tag)
        
data = load_data(sys.argv[1])
stats_data = load_data(sys.argv[2])
first_analyze(data, stats_data)

