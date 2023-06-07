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

#    root_lemmas = []
    
        
#    for root in lexicon.iter_trees():
#        root_lemmas.append(root.lemma)

    for morph in morphs:
        #print(morph)
        cont = [word for word in data if morph in word]
        freq = len(cont) / len(data)
        length = len(morph)
             
        entropy_left = - sum([c_e(bigrams[i][morph]/N, right_counts[morph]/N) for i in bigrams.keys()])
        entropy_right = - sum([c_e(bigrams[morph][j]/N, left_counts[morph]/N) for j in bigrams.keys()])
       
        morph_stats[morph] = (freq, 1/length, max(entropy_left, entropy_right))#any(morph in rlemma for rlemma in root_lemmas))
   
    return morphs, morph_stats


def r_1(word, morphs, morph_stats):
    """longest"""
    if len(word) == 1:
        return [word[0]]
    else:
        max_len=max([len(m) for m in word])
        return ["(" + m + ")" if len(m) == max_len else m for m in word]

def r_2(word, morphs, morph_stats):
    """lowest freq"""
    viable = [m for m in word if m in morph_stats.keys()]
    rts = [min(viable, key = lambda x:morph_stats[x][0])]
    return ["(" + m + ")" if m in rts else m for m in word]

def r_3(word, morphs, morph_stats):
    """min max LEFT, RIGHT PERPLEXITY"""
    viable = [m for m in word if m in morph_stats.keys()]
    rts = [min(viable, key = lambda x: morph_stats[x][2])]
    return ["(" + m + ")" if m in rts else m for m in word]

def r_4(word, morphs, morph_stats):
    viable = [m for m in word if m in morph_stats.keys()]
    ms = [sum([morph_stats[x][i] for x in viable]) for i in range(3)]
    rts = [min(viable, key = lambda x: sum([morph_stats[x][i]/(ms[i] + 0.00000000001) for i in [0,1,2]]))]
    return ["(" + m + ")" if m in rts else m for m in word]

def shortest_edit(w1, w2):
    known = defaultdict(lambda: defaultdict(int))
    strout = ""
    for i in range(len(w1)):
        known[i][-1] = i+1
    for j in range(len(w2)):
        known[-1][j] = j+1
    for i in range(len(w1)):
         for j in range(len(w2)):
             a = known[i-1][j-1]
             if w1[i] != w2[j]:
                 a += 1
             b = known[i][j-1]+1
             c = known[i-1][j]+1
             res = min([a,b,c])
             known[i][j] = res
    x = i
    y = j
    while x > -1 or y > -1:
        a = known[x-1][y-1]
        b = known[x-1][y]
        c = known[x][y-1]
        res = min([a,b,c])
        if res == a and x > -1 and y > -1:
            strout = w2[y] + strout
            x -= 1
            y -= 1
            if w1[x+1] != w2[y+1]:
                strout = "@" + strout
        elif (res == b and b > c)or y < 0:
            x -= 1
        else:
            strout = "@" + w2[y] + strout
            y -= 1
    return [w2, known[i][j], strout]

def r_5(word, morphs, morph_stats):
    lexemes = lexicon.get_lexemes(lemma="".join(word))
    if len(lexemes) == 0:
        return r_4(word, morphs, morph_stats)
    lexeme = lexemes[0].get_tree_root()
    ws = [lexeme.lemma] + [lex.lemma for lex in lexeme.children]
    minm = min(word, key=lambda x: sum([shortest_edit(x, c)[1] for c in ws]))
    return ["(" + m + ")" if m == minm else m for m in word]

def r_6(word, morphs, morph_stats):
    lexemes = lexicon.get_lexemes(lemma="".join(word))
    if len(lexemes) == 0:
        return r_4(word, morphs, morph_stats)
    lexeme = lexemes[0].get_tree_root()
    ws = [lexeme.lemma] + [lex.lemma for lex in lexeme.children]
    scored = {x: sum([shortest_edit(x, c)[1] for c in ws]) for x in word}
    snorm = sum(scored.values())

    viable = [m for m in word if m in morph_stats.keys()]
    ms = [sum([morph_stats[x][i] for x in viable]) for i in range(3)]
    minm = min(viable, key = lambda x: scored[x]/(snorm + 0.00000000001) + sum([morph_stats[x][i]/(ms[i] + 0.00000000001) for i in [0,1,2]]))
    return ["(" + m + ")" if m == minm else m for m in word]


def good(schema, shortest, lemmas):
    """lemma contains the substring specified by "schema", "shortest" """
    OK = True
    for lemma in lemmas:
        OK = any(all(lemma[j + i] == shortest[i] for i in schema) for j in range(-schema[0], len(lemma) - schema[-1]))
        if not OK:
            return False
    return True

def variants(schema, shortest, lemmas):
    """generates possible variants of the schema"""
    schemata = []
    start = 0
    if len(schema)>0:
        start = schema[-1] + 1
    for j in range(start, len(shortest)):
        new_schema = schema + [j]
        if good(new_schema, shortest, lemmas):
            schemata.append(new_schema)
    return(schemata)

#def prune(schemata, m):
#    """groups schemata ending on the same position, returns the longest one"""
#    grouped = [[schema for schema in schemata if schema[-1] == i] for i in range(m)]
#    return [max(i_schemata, key=len) for i_schemata in grouped if len(i_schemata) > 0]

def get_schemata(lemmas):
    """for lemmas, returns longest common substring (with wildcards)"""
    shortest = min(lemmas, key=len)
    schemata = [[]]
    max_len = -1
    new_max = 0
    new = []
    while(max_len < new_max):
        max_len = new_max
        for schema in schemata.copy():
            new_schemata = variants(schema, shortest, lemmas)
            if len(new_schemata) > 0 and schema in schemata:
                schemata.remove(schema)
            schemata = schemata + new_schemata
        if len(schemata[0]) == 0:
            return []
        #chemata = prune(schemata, len(shortest))
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

def r_7(word, morphs, morph_stats):
    viable = [m for m in word if m in morph_stats.keys()]
    lexemes = lexicon.get_lexemes(lemma="".join(word))
    if len(lexemes) == 0:
       return r_4(word, morphs, morph_stats)
    root = lexemes[0].get_tree_root()
    lemmas = [child.lemma.lower() for child in root.iter_subtree()]
    schemata = get_schemata(lemmas)
    candidates = []
    if len(schemata) > 0:
        candidates = [seg for seg in word if any(agrees(seg, schema) for schema in schemata)]
    if len(candidates) == 0:
        candidates = viable
    ws = [root.lemma] + [lex.lemma for lex in root.children]

    scored = {x: sum([shortest_edit(x, c)[1] for c in ws]) for x in word}
    snorm = sum(scored.values())
    viable = candidates
    ms = [sum([morph_stats[x][i] for x in viable]) for i in range(3)]
    minm = min(viable, key = lambda x: scored[x]/(snorm + 0.00000000001) + sum([morph_stats[x][i]/(ms[i] + 0.00000000001) for i in [0,1,2]]))
    return  ["(" + m + ")" if m == minm else m for m in word]

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
tested = [(r_1, "r1"), (r_2, "r2"), (r_3, "r3"), (r_4, "r4"), (r_5, "r5"), (r_6,"r6"),(r_7, "r7")]
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
        for i in range(len(item)):
            if roots[i] == gold[i] and gold[i][:1] ==  "(": #.keys() and gold[morph] == "Root":
                f_e["TP"] += 1
            elif  roots[i] != gold[i] and roots[i][:1] ==  "(": #.keys() or gold[morph] != "Root"):
                f_e["FP"] += 1
            elif  roots[i] == gold[i] and gold[i][:1] !=  "(": #or gold[morph] != "Root"):
                f_e["TN"] += 1
            elif roots[i] != gold[i] and gold[i][:1] ==  "(": #and gold[morph] == "Root":
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
