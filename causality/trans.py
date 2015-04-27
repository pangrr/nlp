import yaml

infile = yaml.load(open("templates.yaml", "r"))
out = []

for level in infile:
    newLevel = {}
    for temp in level:
        newLevel[" ".join(temp["template"])] = str(temp["direction"])
    out.append(newLevel)

outfile = open ("temp", "w")
outfile.write(yaml.dump(out))

