import data.preprocessing as dp
from collections import defaultdict
import trie

form_lemma, forms, tag_forms = dp.lemmatize([])

def get_endings():
    derivations_list = ["ck","sk","čt","št", "ovy","ový"]
    form_endings = defaultdict(list)
    for batch in tag_forms.values():
        print(batch)
        if len(batch) <= 1:
            continue
        ends = trie.get_ending_segments(batch, witness=2)
        for form in batch:
            poss_ends = [x for x in ends if "".join(form[-1 * len(x):]) in x]
            form_endings[form] = max(poss_ends, key=len)
    print("PART_2")
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

get_endings()
