import pickle
with open("morph_classes.pickle","rb") as r:
    classes = pickle.load(r)

print(list(classes["endings"].keys())[:100])
print(list(classes["stems"].keys())[:100])
print(list(classes["affixes"].keys())[:100])

