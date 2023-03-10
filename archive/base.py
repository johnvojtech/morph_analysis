#!python3
import derinet.lexicon as dlex
import pickle

def get_morphs(lexeme):
    return {lexeme.lemma[segm["Start"]:segm["End"]]:segm["Type"] for segm in lexeme.segmentation}

def common_root(segm_dict, lexeme):
    morphs = get_morphs(lexeme)
    roots = [root for root in morphs.keys() if morphs[root] == "Root"]
    return all(root in segm_dict[lexeme.lemma] for root in roots)

with open("annotated/derinet2.pickle", "rb") as r:
    raw = pickle.load(r)
with open("segmented.pickle", "rb") as r2:
    segmented = pickle.load(r2)

segm_dict = {}
for segments in segmented:
    segm_dict["".join(segments)] = segments

raw = [w for w in raw if w.lemma in segm_dict.keys() and common_root(segm_dict, w)]
clear = [(lexeme.lemma, segm_dict[lexeme.lemma], get_morphs(lexeme)) for lexeme in raw]
for item in clear:
    print(item)
print(len(clear))

with open("cs_gold.pickle", "wb") as w:
    pickle.dump(clear, w)
