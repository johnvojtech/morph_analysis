#!python3
import sys
import utils.morph_analyzer as ma
from collections import defaultdict

def load_data(filename, column=0):
    with open(filename, "r+") as r:
        data = [s.strip().split("\t")[column].split() for s in r.readlines()]
        return data

def first_analysis(data):
    morphs, mstats = ma.statistics(data)
    analysed = []

    root_dict = defaultdict(int)
    derivation_dict = defaultdict(int)
    ending_dict = defaultdict(int)
    morph_dict = defaultdict(int)
    for word in data:
        roots = ma.find_roots(word, mstats)
        endings = ma.find_endings(word)
        derivations = ma.find_derivations(word)
        analysed_morphs = []
        root_out = []
        derivation_out = []
        ending_out = []
        for i in range(len(word)):
            morph = word[i]
            morph_dict[morph] += 1
            if any(item[1] == i for item in roots):
                analysed_morphs.append((morph, "R"))
                root_dict[morph] += 1
            elif any(item[1] == i for item in endings):
                analysed_morphs.append((morph, "E"))
                ending_dict[morph] += 1
            elif any(item[1] == i for item in derivations):
                analysed_morphs.append((morph, "D"))
                derivation_dict[morph] += 1
            else:
                analysed_morphs.append((morph, "?"))
        analysed.append(analysed_morphs)
        #print(analysed_morphs)
    return analysed, root_dict, derivation_dict, ending_dict, morph_dict, mstats

def clean_signatures(analysed, root_dict, derivation_dict, ending_dict, morph_dict, stats):
    spurious = defaultdict(list)
    root_ls = []
    derivation_ls = []
    ending_ls = []
    for a in range(len(analysed)):
        w = analysed[a]
        for morph in w:
            if morph[1] == "R":
                root_ls.append(morph)
            elif morph[1] == "D:":
                    derivation_ls.append(morph)
            elif morph[1] == "E:":
                    ending_ls.append(morph)
    
        spurious_roots = [x for x in root_ls if x[1] in ending_ls or x[1] in derivation_ls]
        if len(root_ls) - len(spurious_roots) <= 0:
            spurious_roots.sort(key=lambda x:stats[x][0])
            spurious_roots = spurious_roots[1:]
        for sr in spurious_roots:
            root_ls.remove(sr)
            root_dict[sr] -= 1
        spurious_derivations = [x for x in derivation_ls if x[1] in ending_ls]
        for x in spurious_derivations:
            if ending_dict[x] > derivation_dict[x]:
                derivation_dict[x] -= 1
            elif x in ending_ls:
                ending_dict[x] -= 1
        new_w = []
        for i in range(len(w)):
            real_morph = w[i]
            morph = real_morph[0]
            if real_morph in root_ls:
                new_w.append((morph, "R"))
            elif real_morph in derivation_ls:
                new_w.append((morph, "D"))
            elif real_morph in ending_ls:
                new_w.append((morph, "E"))
            else:
                new_w.append((morph, "?"))
        analysed[a] = new_w
    return analysed, root_dict, derivation_dict, ending_dict, morph_dict
        

def fill_in(analysis, root_dict, derivation_dict, ending_dict, morph_dict, correction=3):
    prefixes = defaultdict(int)
    suffixes = defaultdict(int)
    unresolved = []
    rde_ls = [sum(list(root_dict.values())),sum(list(derivation_dict.values())),sum(list(ending_dict.values()))]
    rde_m_ls = [len(list(root_dict.keys())),len(list(derivation_dict.keys())),len(list(ending_dict.values()))]
    for j in range(len(analysis)):
        analysed_word = analysis[j]
        signature = []
        first_root = len(analysed_word)
        last_root = 0

        for i in range(len(analysed_word)):
            morph, tag = analysed_word[i]
            rde = [root_dict[morph], derivation_dict[morph], ending_dict[morph]]
            if max(rde) > correction * sum(rde) / 3:
                analysed_word[i] = ["R","D","E"][rde.index(max(rde))]

        if not any(item[1] == "R" for item in analysed_word):
            maxitem = max(analysed_word, key=lambda x: root_dict[x[0]]/(root_dict[morph]+derivation_dict[morph]+ending_dict[morph]))
            analysed_word[analysed_word.index(maxitem)] = (maxitem[0], "R")

        for i in range(len(analysed_word)):
            morph, tag = analysed_word[i]
            if tag == "?":
                if root_dict[morph] > derivation_dict[morph] and root_dict[morph] > ending_dict[morph]:
                    analysed_word[i] = (morph, "R")
                    last_root = i
                    if i < first_root:
                        first_root = i
                elif all(ending_dict[morph_1] >= derivation_dict[morph_1] for morph_1 in analysed_word[i:]):
                    analysed_word[i] = (morph, "E")
                else:
                    analysed_word[i] = (morph, "D")
            elif tag == "R":
                if i < first_root:
                    first_root = i
                last_root = i
        # před prvním kořenem -> předpony
        # za první koncovkou po posledním kořenu -> koncovky
        # po posledním kořenu, derivace -> přípony
         
        end = False
        for i in range(len(analysed_word)):
            morph, tag = analysed_word[i]
            if end or (tag == "E" and i > last_root):
                end = True
                analysis[j][i] = (morph, "E")
            elif i < first_root:
                prefixes[morph] += 1
                analysis[j][i] = (morph, "P")
            elif i > last_root:
                suffixes[morph] += 1
                analysis[j][i] = (morph, "S")
            else:
                unresolved.append(i)
        for index in unresolved:
            analysed_word = analysis[index]
            word = "".join([item[0] for item in analysed_word])
            roots = [i for i in range(len(analysed_word)) if analysed_word[i][1] == "R"]
            if len(roots) > 1:
                for i in range(len(roots) - 1):
                    inter = [item for item in analysed_word[roots[i]:roots[i+1]] if item[0] == "o"]
                    if len(inter) > 0:
                        j = analysed_word[roots[i]:roots[i+1]].index(inter[0])
                        analysis[index][j][1] = "I"
                        for k in range(roots[i]+1, roots[i] + j):
                            analysis[index][k][1] = "S"
                        for k in range(roots[i] + j + 1, roots[i+1]):
                            analysis[index][k][1] = "P"
                    else:
                        probs = []
                        for j in range(roots[i],roots[i+1]):
                            prefix_probs = [prefixes[item[0]]/(prefixes[item[0]] + suffixes[item[0]]) for item in analysed_word[j:roots[i+1]]]
                            suffix_probs = [suffixes[item[0]]/(prefixes[item[0]] + suffixes[item[0]]) for item in analysed_word[roots[i]:j]]
                            first_prefix_prob = (sum(suffix_probs) / len(suffix_probs)) * (sum(prefix_probs) / len(prefix_probs))
                            probs.append((first_prefix_prob, j))
                        probs.sort(key = lambda x: x[0], reverse=True)
                        if len(probs) > 0:
                            first_prefix = probs[0][1]
                        for j in range(roots[i],roots[i+1]):
                            if j < first_prefix:
                                analysis[index][j][1] = "S"
                            else:
                                analysis[index][j][1] = "P"
    return analysis

def analyze(data):
    analysed, root_dict, derivation_dict, ending_dict, morph_dict, stats = first_analysis(data)
    analysed, root_dict, derivation_dict, ending_dict, morph_dict = clean_signatures(analysed, root_dict, derivation_dict, ending_dict, morph_dict, stats)
    analysis = fill_in(analysed, root_dict, derivation_dict, ending_dict, morph_dict)
    for word_tag in analysis:
        word = " ".join([item[0] for item in word_tag])
        signature = "".join([item[1] for item in word_tag])
        print(word + "\t" + signature)

data = load_data(sys.argv[1], 3)
analyze(data)
