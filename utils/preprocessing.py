import sys
import os
from collections import defaultdict
import pickle

def load(name):
    names = ["data/"+name+"/form_lemma.pickle", "data/"+name+"/forms.pickle", "data/" + name + "/tags.pickle", "data/" + name + "/form_tags.pickle"]
    if all(os.path.isfile(n) for n in names):
        out = []
        for i in range(4):
            with open(names[i], "rb") as r:
                out.append(pickle.load(r))
        return tuple(out)
    return None

def lemmatize(data,name,tag_sample=1000):
    preprocessed = load(name)
    if preprocessed is not None:
        return preprocessed
    form_lemma = defaultdict(str)
    check_form = set(["".join(item) for item in data])
    #print(check_form)
    forms_dict = defaultdict(list)
    tag_forms = defaultdict(list)
    form_tags = defaultdict(str)
    append = False
    al = 0
    with open("data/czech-morfflex-2.0.tsv", "r") as r:
        lemma = ""
        forms = []
        for line in r:
            item = line.lower().strip().split("\t")
            if len(item) == 3:
                new_lemma = item[0].split("_")[0]
                if len(tag_forms[item[1]]) < tag_sample:
                    tag_forms[item[1]].append(item[2])
                if new_lemma != lemma:
                    if append:
                        forms_dict[lemma] = forms.copy()
                        append = False
                    forms = [item[2]]
                    lemma = new_lemma
                else:
                    forms.append(item[2])
                if item[2] in check_form:
                    form_lemma[item[2]] = lemma
                    form_tags[item[2]] = item[1]
                    al += 1
                    append = True

    os.mkdir("data/"+name)
    with open("data/" + name + "/form_lemma.pickle","wb") as w1:
        pickle.dump(form_lemma, w1)
    with open("data/" + name + "/forms.pickle","wb") as w2:
        pickle.dump(forms_dict, w2)
    with open("data/" + name + "/tags.pickle","wb") as w:
        pickle.dump(tag_forms, w)
    with open("data/"+name + "/form_tags.pickle","wb") as w:
        pickle.dump(form_tags, w)
    return form_lemma, forms_dict, tag_forms
