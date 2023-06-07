import sys
with open(sys.argv[1], "r") as r:
    lines = [line.split("\t") for line in r]
    morphs = list(set([x for m in lines for x in m[0].strip().split()]))
    tags =  list(set([x[i:i+1] for m in lines for x in m[1].strip().split() for i in range(len(x))]))
    with open("vocab.json","w") as w:
        w.write("[")
        w.write("\"" + morphs[0] + "\"")
        for morph in morphs[1:]:
            w.write(", ")
            w.write("\"" + morph + "\"")
        w.write("]")
    with open("tags.json", "w") as w:
        w.write("[")
        w.write("\"" + tags[0] + "\"")
        for tag in tags[1:]:
            w.write(", ")
            w.write("\"" + tag + "\"")
        w.write("]")
    with open("dataset.txt","w") as w:
        for line in lines:
            w.write("[\"" + line[0].replace(" ","\", \"") + "\"]")
            w.write("\t")
            taglist = [line[1].strip()[i:i+1] for i in range(len(line[1]) - 1)]
            w.write("[")
            w.write("\"" + taglist[0] + "\"")
            for tag in taglist[1:]:
                w.write(", ")
                w.write("\"" + tag + "\"")
            w.write("]")
            w.write("\n")

