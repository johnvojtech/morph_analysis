#!python3
import sys
import pickle
import stats

with open("morph_classes_new.pickle","rb") as r:
    classes = pickle.load(r)

def clearup_classes(data):
    morphs, morph_stats = stats.statistics(data)
    stems = classes["R"]
    endings = classes["E"]
    affixes = classes["D"]
    root_morphs = [x for y in data for x in y if len(y) == 1]
    ending_morphs = []
    deriv_morphs = []
    morphs = set([x for y in data for x in y])
    for word in data: 
        for i in range(len(word)):
            morph = word[i]
            stats = morph_stats[morph]
            

def roots_endings(word):
    rind = []
    eind = []
    ends = ["a","e","i","o","u","y", "ho", "á"]
    exceptions = ["k", "ck","sk","čt","št","ova","ová"]
    non_roots = ["io"]
    for i in range(len(word)):
        """
        roots = [k for k in classes["stems"].keys() if word[i] in k]
        endings = [k for k in classes["endings"].keys() if word[i] in k]
        affixes = [k for k in classes["affixes"].keys() if word[i] in k]
        rls = [classes["stems"][k] * (len(word[i])/len(k)) for k in roots]
        els = [classes["endings"][k] * (len(word[i])/len(k)) for k in endings]
        als = [classes["affixes"][k] * (len(word[i])/len(k)) for k in affixes]
        sys.exit()
        r = sum(rls) / (len(rls) + 1)
        e = sum(els) / (len(els) + 1)
        a = sum(als) / (len(als) + 1)
        """
        r = classes["R"][word[i]]
        e = classes["E"][word[i]]
        a = classes["D"][word[i]]

        if r == max([r,e,a]) and word[i] not in non_roots:
            rind.append(i)
        elif (e > a  and word[i] not in exceptions) or word[i] in ends:
            eind.append(i)
    if len(rind) == 0:
        ind = word.index(max(word, key=len))
        if ind in eind:
            eind.remove(ind)
        rind.append(ind)
    qlist = [i for i in eind if all(j in eind for j in range(i, len(word)))]
    if len(qlist) > 0:
        q = eind.index(min(qlist))
        eind= eind[q:]
    else:
        eind = []
    return rind, eind

def classify(word):
    roots, endings = roots_endings(word)
    prefixes = [i for i in range(0, roots[0])]
    end_suf = len(word)
    if len(endings) > 0:
        end_suf = endings[0]
    suffixes = [i for i in range(roots[-1] + 1,end_suf)]
    interfixes = []
    unresolved = []
    if len(roots) > 1:
        for i in range(len(roots) - 1):
            if "o" in word[roots[i]:roots[i+1]]:
                j = word[roots[i]:roots[i+1]].index("o")
                interfixes.append( roots[i] + j)
                suffixes += [k for k in range(roots[i]+1, roots[i] + j)]
                prefixes += [k for k in range(roots[i] + j + 1, roots[i+1])]
            else:
                unresolved += [k for k in range(roots[i], roots[i+1])]
    return (prefixes, roots, interfixes, suffixes, endings, unresolved)

def get_signature(word, analysis):
    signature = ["?" for i in range(len(word))]
    for index in analysis[0]:
        signature[index] = "P"
    for index in analysis[1]:
        signature[index] = "R"
    for index in analysis[2]:
        signature[index] = "I"
    for index in analysis[3]:
        signature[index] = "S"
    for index in analysis[4]:
        signature[index] = "E"
    return signature

def analyze(data):
    for word in data:
        analysis = classify(word)
        signature = get_signature(word, analysis)
        print(" ".join(word) + "\t" + "".join(signature))

with open(sys.argv[1], "r") as r:
    data = [m.strip().split("\t")[3].split() for m in r]
    analyze(data)
