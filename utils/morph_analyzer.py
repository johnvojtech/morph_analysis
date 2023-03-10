#!python3
import os
import utils.common_sub as cs
import utils.preprocessing as dp
from collections import defaultdict
import pickle
import utils.stats as stats
import derinet.lexicon as dlex

lexicon = dlex.Lexicon()
lexicon.load('derinet/tools/data-api/derinet2/derinet-2-0.tsv')
d = dp.load("old_sigmorphon22")
form_lemma, forms, tag_forms, form_tags = d[0], d[1], d[2], d[3]
#tag_ending = tag_endings()

def statistics(data):
    return stats.statistics(data, "old_sigmorphon22", lexicon)

def load_data(filename):
    with open(filename, "r") as reader:
        return [item.strip().split() for item in reader]

def tag_endings():
    if os.path.isfile("data/tag_schemata.pickle"):
        with open("data/tag_schemata.pickle","rb") as r:
            return(pickle.load(r))
    tag_schemata = defaultdict(list)
    for tag in list(tag_forms.keys()):
        batch = tag_forms[tag]
        if len(batch) > 2:
            schemata = cs.get_schemata(batch)
            if True or len(schemata) == 0:
                batch.sort(key=lambda x: x[-1])
                batches = defaultdict(list)
                for item in batch:
                    batches[item[-1]].append(item)
                for new_batch in batches.values():
                    if len(new_batch) >= len(batch)/5:
                        schemata.append(cs.get_schemata(new_batch)[-1])
            tag_schemata[tag] = schemata
    with open("data/tag_schemata.pickle","wb") as w:
        pickle.dump(tag_schemata, w)
    return tag_schemata

tag_ending = tag_endings()

def find_roots(word, mstats):
    viable = [m for m in word if m in mstats.keys()]
    lexemes = lexicon.get_lexemes(lemma="".join(word))
    roots = [lexeme.get_tree_root() for lexeme in lexemes]
    for root in roots:
        lemmas = [child.lemma.lower() for child in root.iter_subtree()]
        schemata = cs.get_schemata(lemmas)
        candidates = []
        if len(schemata) > 0:
            candidates = [seg for seg in word if any(cs.agrees(seg, schema) for schema in schemata)]
        if len(candidates) == 0:
            candidates = viable
    root = min(viable, key = lambda x: mstats[x][1])   #THIS COULD BE TRAINED
    return [(root, word.index(root))]

def find_derivations(word):
    lemma = form_lemma["".join(word)].split("-")[0]
    lexemes = lexicon.get_lexemes(lemma=lemma)
    #print("D")
    #print(word)
    #print(lemma)
    #print(lexemes)
    if len(lexemes) > 0:
        root = lexemes[0].get_tree_root()
        depth = 0
        current = lexemes[0]
        while len(current.all_parents) > 0:
            parent = current.all_parents[0]
            #f len(parent.lemma) < len(current.lemma):
            #   depth += 1
            current = parent
        derivations = stats.fit_lemmas(root.lemma, "#".join(word))#:depth]
        return derivations
    return []

def find_endings_backup(word):
    lemma = form_lemma["".join(word)]
    fs = forms[lemma]
    w = "".join(word)
    #print(fs)
    endings = set()
    max_i = 0
    min_j = len(w)
    for form in fs:
        index = max([(i, j) for i in range(len(w)) for j in range(i,len(w) + 1) if  w[i:j] in form], key = lambda x: x[1] - x[0])
        endings.add(index[0])
        endings.add(index[1])
        if index[0] > max_i:
            max_i = index[0]
        if index[1] < min_j:
            min_j = index[1]
    indices = list(endings)
    if 0 in indices:
        indices.remove(0)
    indices.sort()
    parts = []
    last = 0
    for index in indices:
        if index > min_j:
            parts.append(w[last:index])         
        last = index
    if last < len(lemma):
        parts.append(w[last:])

    end_morphs = []
    w_ending = len("".join(word)) - len("".join(parts))
    for i in range(len(word)):
        if w_ending <= 0:
            end_morphs.append((word[i], i))
        w_ending -= len(word[i])
     
    return end_morphs


def find_endings(word):
    possible = form_tags["".join(word)]
    possible_tags = []
    for item in possible:
        if type(item) == list:
            possible_tags += item
        else:
            possible_tags.append(item)
    possible_endings = [tag_ending[tag] for tag in possible_tags]
    possible_endings = [ending for t_endings in possible_endings for ending in t_endings]
    
    end = ""
    end_morphs = possible_endings
    for ending in possible_endings:
        ls = [j for j in range(len(ending)) if len(ending[j:]) == ending[-1][0] - ending[j][0]]
        if len(ls) == 0:
            continue
        q = min(ls)
        ending = "".join([item[1] for item in ending[q:]])
        if len(ending) > len(end):
            end = ending
    w_ending = len("".join(word)) - len(end)
    for i in range(len(word)):
        w_ending -= len(word[i])
        if w_ending < 0:
            end_morphs.append((word[i], i))
    #print(word)
    #print(possible_tags)
    #print(possible_endings)
    #print(end_morphs)
    if len(end_morphs) == 0:
        return find_endings_backup(word)
    return [x for y in end_morphs for x in y]

find_endings_backup(["nej", "do", "ved", "n", "ějš", "ích"])
