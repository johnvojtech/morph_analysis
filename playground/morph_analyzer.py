#python3
import sys
import pickle
from collections import defaultdict
import derinet.lexicon as dlex
import trie
import data.preprocessing as dp


lexicon = dlex.Lexicon()
lexicon.load('derinet-2-0.tsv')

endings = defaultdict(int)
stems = defaultdict(int)
affixes = defaultdict(int)
endings_list = []

form_lemma = defaultdict(str)
lemma_forms = defaultdict(list)
tag_forms = defaultdict(list)

def process_batch(forms,tags, lemma):
    def shortest_common(batch):
        lcs = ""
        shortest = min(batch, key=len)
        for i in range(len(shortest)):
            for j in range(i + len(lcs), len(shortest) + 1):
                if all(shortest[i:j] in x for x in batch):
                    lcs = shortest[i:j]
        return lcs
    if len(batch) == 0:
        return
    
    lemma_forms[lemma] = forms
    for item in forms:
         form_lemma[item] = lemma

    
    vowels = "aeiouyáéíóúůýě"
    consonants = []
    consonants.append(item.translate(str.maketrans('','',vowels)))

    
    lcs = shortest_common(forms)
    stems[lcs] += 1
    lccs = shortest_common(consonants)
    precursors = []
    lexemes = lexicon.get_lexemes(lemma=lemma.split("_")[0].split("-")[0])
    viable_derivations = []
    while len(lexemes) > 0:
        precursors.append(lexemes[0].lemma)
        lexemes = lexemes[0].all_parents
    for i in range(len(precursors) - 1):
        lcs = shortest_common([precursors[i], precursors[i+1]])
        viable_derivations += precursors[i].replace(lcs, "#").split("#")
    for deri in viable_derivations:
        affixes[deri] += 1
    pre_forms = [form.replace(lcs, "#").split("#") for form in forms] 
    viable_endings = [form[-1] for form in pre_forms if form[-1] not in viable_derivations]
    for ending in viable_endings:
        endings[ending] += 1

def get_endings():
    derivations_list = ["ck","sk","čt","št", "ovy","ový"]
    form_endings = defaultdict(list)
    for batch in tag_forms.values():
        if len(batch) <= 1:
            continue
        ends = trie.get_ending_segments(batch, witness=2)
        for form in batch:
            poss_ends = [x for x in ends if "".join(form[-1 * len(x):]) in x]    
            form_endings[form] = max(poss_ends, key=len)
    for batch in lemma_forms.values():
        if len(batch) <= 1:
            continue
        all_ends = [[form, form_endings[form]]for form in batch]
        beginnings = set([ends[1][0] for ends in all_ends if ends[1][0] not in derivations_list])
        while len(beginnings) == 1:
            for item in all_ends:
                item[1] = item[1][1:]
            beginnings = set([ends[1][0] for ends in all_ends if ends[1][0] not in derivations_list])
        for item in all_ends:
            form_endings[item[0]] = item[1]
    print(set(form_endings.values()))
    return form_endings
st(affixes.keys()):
    for i in range(len(key)):
        if key[i:] in endings.keys() and affixes[key[i:]]/endings[key[i:]]<2:
            affixes[key[i:]] += affixes[key]
            affixes[key] = 0
with open("morph_classes.pickle","wb") as w:
    pickle.dump({"stems":stems, "affixes":affixes,"endings":endings},w)
