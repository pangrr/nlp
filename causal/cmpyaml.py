from __future__ import print_function
import yaml
import sys

fileA = yaml.load(open(sys.argv[1], "r").read().replace(" !!causal.ParsedCausalRelation", ""))
fileB = yaml.load(open(sys.argv[2], "r").read().replace(" !!causal.ParsedCausalRelation", ""))

if len(fileA) != len(fileB):
    print ("Inequal number of sentences: " + str(len(fileA)) + " " + str(len(fileB)))
    sys.exit()

identical = 1

for i in range(len(fileA)):
    if fileA[i]["from"] != fileB[i]["from"] or fileA[i]["to"] != fileB[i]["to"]:
        identical = 0
        print (fileA[i]["sentence"])

if identical == 1:
    print ("Identical content.")



