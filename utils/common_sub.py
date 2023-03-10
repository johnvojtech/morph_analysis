#!python3
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

