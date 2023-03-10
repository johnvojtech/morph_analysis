#!python3
import sys
import os
import pickle
from collections import defaultdict
import derinet.lexicon as dlex
lexicon = dlex.Lexicon()
lexicon.load('derinet-2-0.tsv')

def load_data(filename, column=0):
    with open(filename, "r+") as r:
        data = [s.strip().split("\t")[column].split() for s in r.readlines()]
        return data

def lemmatize(data):
    if os.path.isfile("form_lemma.pickle") and os.path.isfile("forms.pickle"):
        with open("form_lemma.pickle", "rb") as r:
            fl = pickle.load(r)
        with open("forms.pickle", "rb") as r:
            fs = pickle.load(r)
        return fl, fs
    form_lemma = defaultdict(str)
    check_form = set(["".join(item) for item in data])
    forms_dict = defaultdict(list)
    append = False
    with open("czech-morfflex-2.0.tsv", "r") as r:
        lemma = ""
        forms = []
        for line in r:
            item = line.strip().split("\t")
            new_lemma = item[0].split("_")[0]
            if new_lemma != lemma:
                if append:
                    forms_dict[lemma] = forms.copy()
                    append = False
                forms = []
                lemma = new_lemma
            else:
                forms.append(item[2])
            if item[2] in check_form:
                form_lemma[item[2]] = lemma
                append = True
    with open("form_lemma.pickle","wb") as w1:
        pickle.dump(form_lemma, w1)
    with open("forms.pickle","wb") as w2:
        pickle.dump(forms_dict, w2)
    sys.exit()
    return form_lemma, forms_dict

def statistics(data):
    morphs = list(set([morph for word in data for morph in word]))
    morph_stats = {}
    for morph in morphs:
        cont = [word for word in data if morph in word]
        freq = len(cont) / len(data)
        morph_stats[morph] = (freq,)
    return morphs, morph_stats

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


def word_roots(word, morphs, morph_stats):
    viable = [m for m in word if m in morph_stats.keys()]
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
    root = min(viable, key = lambda x: morph_stats[x][0])
    return ["R:" + item if item == root else item for item in word]

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
            #strout = "-@" + w1[x] + strout
            x -= 1
        else:
            strout = "@" + w2[y] + strout
            y -= 1
    return [w2, known[i][j], strout]


def fit_lemmas(lemma1, lemma2):
    shed = shortest_edit(lemma1, lemma2)
    ls = shed[2].split("@#")
    ls2 = []
    for item in ls:
        if 2 * item.count("@") >= len(item):
            ls2.append("D:" + item.replace("@", ""))
        else:
            ls2.append(item.replace("@", ""))
    return(ls2)

def part_split(form, lemma):
    parts = []
    src = fit_lemmas(lemma, "#".join(form))
    now = False
    deriv = False
    for morph in src:
        if morph[0] == "|":
            morph = morph[1:]
            now = True
        if morph[0] != 'D' and now:
            parts.append(lemma[:len(morph)])
            lemma = lemma[len(morph):]
        else:
            now = False
    if len(lemma) > 0:
        parts.append(lemma)
    return parts

def lemma_forms_split(lemma, forms, ls = None):
    endings = set()
    max_i = 0
    min_j = len(lemma)
    for form in forms:
        index = max([(i, j) for i in range(len(lemma)) for j in range(i,len(lemma) + 1) if  lemma[i:j] in form], key = lambda x: x[1] - x[0])
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
        if index <= max_i or index > min_j:
            parts.append("E:" + lemma[last:index])
        else:
            parts.append(lemma[last:index])
        last = index
    if last < len(lemma):
        parts.append("E:" + lemma[last:])
    return parts

def endings_list(word, forms):
    wc = word.copy()
    endings = lemma_forms_split("".join(word), forms)
    form_endings = [item.replace("E:", "") for item in endings]
    out = []
    last_index = 0
    start = ""
    for i in range(len(form_endings)):
        item = form_endings[i]
        if wc[0] == item:
            out.append(endings[i])
            start = ""
            wc = wc[1:]
            last_index = 0
        elif len(wc[0]) > last_index + len(item):
            if last_index == 0 and endings[i][:2] == "E:":
                start = "E:"
            last_index += len(item)
        else:
            while len(wc) > 0 and len(wc[0]) <= last_index + len(item):
                out.append(start + wc[0])
                start = ""
                last_index -= len(wc[0])
                wc = wc[1:]
            last_index += len(item)
    return out


#ne part_split, lemma_form_split -> derivation

def analyze(data):
    form_lemma, forms_dict = lemmatize(data)
    morphs, morph_stats = statistics(data)
    root_dict = defaultdict(int)
    derivation_dict = defaultdict(int)
    ending_dict = defaultdict(int)
    unresolved = []
    result_by_lemma = defaultdict(list)
    results = []
    a = 0
    for word in data:
        wcopy = word.copy()
        wform = "".join(word)
        lemma = form_lemma[wform]
        if type(lemma) == list:
            lemma = "-"
        forms = forms_dict[lemma]
        endings = word
        if len(forms) > 0:
            endings = endings_list(word, forms)
        derivations = word
        lexemes = lexicon.get_lexemes(lemma=lemma)
        if len(lexemes) > 0:
            roots = [lexeme.get_tree_root() for lexeme in lexemes]
            derivations = fit_lemmas(roots[0].lemma, "#".join(word))
        
        roots = word_roots(word, morphs, morph_stats)
        final = []
        unres = False

        for i in range(len(word)):
            if all(word[j] == endings[j][2:] for j in range(i, len(word))):
                final.append(endings[i])
                ending_dict[word[i]] += 1
            elif word[i] == derivations[i][2:]:
                final.append(derivations[i])
                derivation_dict[word[i]] += 1
            elif  word[i] == roots[i][2:]:
                final.append(roots[i])
                root_dict[word[i]] += 1
            else:
                final.append(word[i])
                unres = True
        results.append(final)
        result_by_lemma[lemma].append(final)
        if unres:
            unresolved.append(a)
        a += 1

    spurious = defaultdict(list)
    for lemma in result_by_lemma.keys():
        batch = result_by_lemma[lemma]
        root_ls = []
        derivation_ls = []
        ending_ls = []
        for w in batch:
            for morph in w:
                if morph[:2] == "R:":
                    root_ls.append(morph[2:])
                elif morph[:2] == "D:":
                    derivation_ls.append(morph[2:])
                elif morph[:2] == "E:":
                    ending_ls.append(morph[2:])
        spurious_roots = [x for x in root_ls if x in ending_ls or x in derivation_ls]
        if len(root_ls) - len(spurious_roots) <= 0:
            spurious_roots.sort(key=lambda x:morph_stats[x][0])
            spurious_roots = spurious_roots[1:]
        for sr in spurious_roots:
            root_ls.remove(sr)
            root_dict[sr] -= 1
        spurious_derivations = [x for x in derivation_ls if x in ending_ls]
        for x in spurious_derivations:
            if ending_dict[x] > derivation_dict[x]:
                derivation_ls.remove(x)
                derivation_dict[x] -= 1
            elif x in ending_ls:
                ending_ls.remove(x)
                ending_dict[x] -= 1

        new_w = []
        form = ""
        for w in batch:
            for morph in w:
                real_morph = morph.replace("R:","").replace("E:","").replace("D:","")
                form += real_morph
                if real_morph in root_ls:
                    new_w.append("R:" + real_morph)
                elif real_morph in derivation_ls:
                    new_w.append("D:" + real_morph)
                elif real_morph in ending_ls:
                    new_w.append("E:" + real_morph)
                else:
                    new_w.append(real_morph)

        spurious[form] = new_w

    for index in unresolved:
        word = results[index]
        form = "".join(word).replace("R:","").replace("E:","").replace("D:","")
        wf = "#".join(word).replace("R:","").replace("E:","").replace("D:","")
        wf = wf.split("#")
        if form in spurious.keys():
            word = spurious[form]
        lemma = form_lemma[form]
        similar = form_lemma
        new_word = []
        if all(morph[:2] != "R:" for morph in word):
             rt = max(wf, key = lambda x: morph_stats[x][0])
             for i in range(len(word)):
                 if word[i] == rt:
                     word[i] = "R:" + word[i]
                    
        for i in range(len(word)):
            morph = word[i]
            if morph[:2] in ["R:", "D:","E:"]:
                new_word.append(morph)
            else:
                r,d,e = root_dict[morph], derivation_dict[morph], ending_dict[morph]
                if e == max([r,d,e]) and all(ending_dict[word[j]] > max([root_dict[word[j]], derivation_dict[word[j]]]) for j in range(i, len(word))):
                    new_word.append("E:" + morph)
                elif r/(d+1) < 10  or r/(e+1) < 10:
                    new_word.append("D:" + morph)
                else:
                    new_word.append("R:" + morph)
            results[index] = new_word
    out = {"R":defaultdict(int), "D":defaultdict(int), "E":defaultdict(int)}
    for word in results:
        wordform = [s.split(":")[1] for s in word]
        schema = [s.split(":")[0] for s in word]
        for i in range(len(wordform)):
            out[schema[i]][wordform[i]] += 1
        print(" ".join(wordform) + "\t" + "".join(schema))
    with open("morph_classes_new.pickle","wb") as w:
        pickle.dump(out, w)
data = load_data(sys.argv[1], 3)
analyze(data)
