#!python3
import sys
import pickle
import math
from collections import defaultdict
import derinet.lexicon as dlex


lexicon = dlex.Lexicon()
lexicon.load('derinet/tools/data-api/derinet2/derinet-2-0.tsv')


def load_data(filename):
    with open(filename, "r") as reader:
        return [[w.strip().split(), w.replace("(","").replace(")","").strip().split()] for w in reader]
        

def c_e(p_ij, p_j):
    if p_ij > 0 and p_j > 0:
        return p_ij*math.log(p_ij/p_j)
    return 0

def statistics(data):
    def ce_s(p_ij, p_j):
        return p_ij * math.log(p_ij/p_j)
    bigrams = defaultdict(lambda:defaultdict(int))
    N = 0
    for word in data:
        word_2 = ["<S>"] + word + ["<E>"]
        for i in range(len(word_2) - 1):
            bigrams[word_2[i]][word_2[i+1]] += 1
            N += 1

    morphs = list(set([morph for word in data for morph in word]))
    morph_stats = {}

    left_counts = {morph:sum([bigrams[morph][j] for j in bigrams[morph].keys()]) for morph in morphs}
    right_counts = {morph:sum([bigrams[i][morph] for i in bigrams.keys()]) for morph in morphs}

    root_lemmas = []
    
        
    for root in lexicon.iter_trees():
        root_lemmas.append(root.lemma)

    for morph in morphs:
        #print(morph)
        cont = [word for word in data if morph in word]
        freq = len(cont) / len(data)
        length = len(morph)
              


        entropy_left = - sum([c_e(bigrams[i][morph]/N, right_counts[morph]/N) for i in bigrams.keys()])
        entropy_right = - sum([c_e(bigrams[morph][j]/N, left_counts[morph]/N) for j in bigrams.keys()])

        
        morph_stats[morph] = (freq, length, max(entropy_left, entropy_right), any(morph in rlemma for rlemma in root_lemmas))
   
    return morphs, morph_stats


def r_1(word, morphs, morph_stats):
    """longest"""
    if len(word) == 1:
        return [word[0]]
    else:
        max_len=max([len(m) for m in word])
        return [m for m in word if len(m) == max_len]

def r_2(word, morphs, morph_stats):
    """lowest freq"""
    viable = [m for m in word if m in morph_stats.keys()]
    return [min(viable, key = lambda x:morph_stats[x][0])]

def r_3(word, morphs, morph_stats):
    """min max LEFT, RIGHT PERPLEXITY"""
    viable = [m for m in word if m in morph_stats.keys()]
    return [min(viable, key = lambda x: morph_stats[x][2])]

def good(schema, shortest, lemmas):
    OK = True
    for lemma in lemmas:
        OK = any(all(lemma[j + i] == shortest[i] for i in schema) for j in range(-schema[0], len(lemma) - schema[-1]))
        if not OK:
            return False
    return True
                    
def variants(schema, shortest, lemmas):
    schemata = []
    start = 0
    if len(schema)>0:
        start = schema[-1] + 1
    for j in range(start, len(shortest)):
        new_schema = schema + [j]
        if good(new_schema, shortest, lemmas):
            schemata.append(new_schema)
    return(schemata)

def prune(schemata, m):
    grouped = [[schema for schema in schemata if schema[-1] == i] for i in range(m)]
    return [max(i_schemata, key=len) for i_schemata in grouped if len(i_schemata) > 0]

def get_schemata(lemmas):
    shortest = min(lemmas, key=len)
    schemata = [[]]
    max_len = -1
    new_max = 0
    new = []
    while(max_len < new_max):
        max_len = new_max
        for schema in schemata.copy():
            new_schemata = variants(schema, shortest, lemmas)
            if len(new_schemata)>0 and schema in schemata:
                schemata.remove(schema)
            schemata = schemata + new_schemata
        if len(schemata[0]) == 0:
            return []
        schemata = prune(schemata, len(shortest))
        new_max = len(max(schemata, key=len))
   
    schemata = [schema for schema in schemata if len(schema) == max_len]
    return [[(i - schema[0], shortest[i]) for i in schema] for schema in schemata]

def agrees(morph, schema):
    return any(all(morph[item[0] + j] == item[1] for item in schema) for j in range(len(morph) - schema[-1][0]))

def similarity(morph, schema):
    return min([0] + [sum([int(morph[item[0] + j] == item[1]) for item in schema]) for j in range(len(morph) - schema[-1][0])])

def subtree(lexeme, changes=1):
    r = lexeme
    while r.parent is not None and len(get_schemata([r.parent.lemma, r.lemma])) > len(r.lemma) - changes:
        r = r.parent
    return r

def r_4(word, morphs, morph_stats):
    """common features of derived words"""
    viable = [m for m in word if m in morph_stats.keys()]
    lexemes = lexicon.get_lexemes(lemma="".join(word))
    roots = [lexeme.get_tree_root() for lexeme in lexemes]
    for root in roots:
        # lemmas = [segm["Morph"].lower() for child in root.iter_subtree() for segm in child.segmentation if segm["Type"] == "Root"]
        lemmas = [child.lemma.lower() for child in root.iter_subtree()]
        # print(lemmas)
        #        common = [seg for seg in word if all(seg in lemma for lemma in lemmas)]
        schemata = get_schemata(lemmas)
        if len(schemata) > 0:
            candidates = [seg for seg in word if any(agrees(seg, schema) for schema in schemata)]#[min(word, key=lambda x: sum([similarity(x, schema)/len(schemata) for schema in schemata if len(schema) > 0]))]
            #print(candidates)
            if len(candidates) > 0:
                return candidates
            return [seg for seg in word if agrees(seg, get_schemata(lemmas)[0])]
        return [max(word, key=len)] #!!!!!!!!!!!
    
    #return [max(viable, key = lambda x: abs(morph_stats[x][3] - 1/2) - morph_stats[x][4])]  #LANGUAGE DEPENDENT

def r_5(word, morphs, morph_stats):
    """MIN FREQ"""
    viable = [m for m in word if m in morph_stats.keys()]
    return [min(viable, key = lambda x: morph_stats[x][0])]

def r_6(word, morphs, morph_stats):
    viable = [m for m in word if m in morph_stats.keys() and morph_stats[morph][3]]
    lexemes = lexicon.get_lexemes(lemma="".join(word))
    roots = [lexeme.get_tree_root() for lexeme in lexemes]
    for root in roots:
        lemmas = [child.lemma.lower() for child in root.iter_subtree()]
        schemata = get_schemata(lemmas)
        candidates = []
        if len(schemata) > 0:
            candidates = [seg for seg in word if any(agrees(seg, schema) for schema in schemata)]
        if len(candidates) == 0:
            candidates = viable
        return r_5(candidates, morphs, morph_stats)

def r_7(word, morphs, morph_stats):
    viable = [m for m in word if m in morph_stats.keys() and morph_stats[morph][7]]
    

#def r_7((word, morphs, morph_stats):
    

def morph_tag(data, r_fs):
    ms, mss = statistics(data)
    for w in data:
        ws = []
        for r_f in r_fs:
            word = []
            roots = r_f[0](w, ms, mss)
            for item in w:
                if item in roots:
                    word.append(item + ":root")
                else:
                    word.append(item)
            ws.append(" ".join(word))
        print("\t".join(ws))


def ev(f_e):
    if f_e["TP"] == 0:
        return 0, 0, 0
    precision = f_e["TP"]/(f_e["TP"] + f_e["FP"])
    recall = f_e["TP"]/(f_e["TP"]+f_e["FN"])
    F = (2*precision*recall)/(precision+recall)
    return precision, recall, F

def ev2(f_e):
    if f_e["FP"] + f_e["FN"] > 0:
        return 0
    return 1

data = load_data(sys.argv[1])
test_data = [item[1] for item in data]
tested = [(r_1, "r1"), (r_2, "r2"), (r_3, "r3"), (r_4, "r4"), (r_5, "r5"), (r_6, "r6")]
eval_data = {"".join(item[1]):item[0] for item in data}
eval_dict = {func[1]:[0,0,0,0,0] for func in tested}

print("STATS")
ms, mss = statistics(test_data)
print("TEST")
for item in test_data:
    for func in tested:
        roots = func[0](item, ms, mss)
        gold = eval_data["".join(item)]
        f_e = {"FP":0, "FN": 0, "TP":0, "TN": 0}
        for morph in item:
            if morph in roots and "(" + morph + ")"  in gold: #.keys() and gold[morph] == "Root":
                f_e["TP"] += 1
            elif morph in roots and "(" + morph  + ")" not in gold: #.keys() or gold[morph] != "Root"):
                f_e["FP"] += 1
            elif morph not in roots and morph in gold: #or gold[morph] != "Root"):
                f_e["TN"] += 1
            elif morph not in roots and morph not in gold: #and gold[morph] == "Root":
                f_e["FN"] += 1
        p, r, F = ev(f_e)

        #if func[1] == "r4" and F < 1:
        #    print(gold)
        #    print(roots)

        #print("{} -> {}: {} {} {}".format(func[1], "".join(item), p, r, F))
        eval_dict[func[1]][0] += p
        eval_dict[func[1]][1] += r
        eval_dict[func[1]][2] += F
        eval_dict[func[1]][3] += 1
        eval_dict[func[1]][4] += ev2(f_e)

for func in eval_dict.keys():
    f_e = eval_dict[func]
    print(func)
    print("Accuracy: " + str(f_e[4]/f_e[3]))
    print("Average precision: " + str(f_e[0]/f_e[3]))
    print("Average recall: " + str(f_e[1]/f_e[3]))
    print("Average F-measure: " + str(f_e[2]/f_e[3]))
