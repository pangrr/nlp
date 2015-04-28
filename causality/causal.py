import yaml
from pprint import pprint
import math
import sys








class Sentences:
    def __init__ (self, file, evils):
        self.sents = self.load (file)
        self.evils = evils

    def load (self, file):
        return yaml.load (open(file, "r").read().replace(" !!causal.ParsedCausalRelation", ""))

    def getAnswer (self):
        a = []
        for sent in self.sents:
            if sent["from"] == "e1":
                a.append(0)
            else:
                a.append(1)
        return a

    def getSent (self, i):
        return self.sents[i]["sentence"]

    # Return the words between two positions.
    # Make sure the words free from evil phrases.

    def getInt (self, i, x, y):
        int = []
        words = self.sents[i]["words"]
        for n in range(x+1, y):
            int.append (words[n]["value"])
        return self.evils.clean (int)


    def getPre (self, i, x):
        pre = []
        words = self.sents[i]["words"]
        for n in range(0, x):
            pre.append (words[n]["value"])
        return self.evils.clean (pre)


    def getPos (self, i, y):
        pos = []
        words = self.sents[i]["words"]
        for n in range(y+1, len(words)):
            pos.append (words[n]["value"])
        return self.evils.clean (pos)


    def getX (self, i):
        return self.sents[i]["words"][self.sents[i]["e1Index"]]["index"]


    def getY (self, i):
        return self.sents[i]["words"][self.sents[i]["e2Index"]]["index"]











class Evils:

    def __init__ (self, file):
        self.phrases = self.load (file)

    def load (self, file):
        return yaml.load (open(file, "r"))

    def clean (self, words):
        string = " ".join(words)
        for evil in self.phrases:
            string = string.replace(evil, "")
        return string.split()










class Templates:
    def __init__ (self, file):
        self.levels = self.load (file)

    def load (self, file):
        return yaml.load (open (file, "r"))











class Classifier:
    def __init__ (self, sents, temps):
        self.sents = sents
        self.temps = temps
        self.answers = []

    # Do the classification and print the misclassified sentences.
    def grade (self):
        stdA = self.sents.getAnswer()
        for i in range(len(stdA)):
            if stdA[i] != self.answers[i]:
                print (self.sents.getSent(i))

    # Write answers to file.
    def writeAnswer (self, file):
        sents = self.sents.sents
        for i in range(len(sents)):
            if self.answers[i] == 0:
                sents[i]["from"] = "e1"
                sents[i]["to"] = "e2"
            else:
                sents[i]["from"] = "e2"
                sents[i]["to"] = "e1"
        outFile = open(file, "w")
        outFile.write(yaml.dump(sents).replace("- e1Index", "- !!causal.ParsedCausalRelation\n  e1Index "))


    # Return a list of causality decision for all sentences.
    def classify (self):
        for i in range(len(self.sents.sents)):
            self.answers.append(self.classSent(i))



    # Return the causality decision for a sentence.
    def classSent (self, i):
        preMatch, intMatch, posMatch = self.matchSent (i)
        nMatch = len(preMatch) + len(intMatch) + len(posMatch)
        if  nMatch == 0:
            return self.dealNoMatch ()
        elif len (intMatch) > 0:
            return self.dealIntMatch (intMatch)
        else:
            return self.dealNoIntMatch ()    # Consider only words in between target words for simplicity.



    def dealNoIntMatch (self):
        return 0

    # Decide on edges or order between two words.
    def dealNoMatch (self):
        return 0    # Ingnore edges for simpliciy.


    def dealPreMatch (self, matches):
        return 0



    def dealPosMatch (self, matches):
        return 0



    def dealIntMatch (self, matches):
        for level in matches:
            maxWeight = -100000
            dir = 0
            for temp in level:
                if temp[1] > maxWeight: # Consider only the reverse weight
                    maxWeight = temp[1]
                    if "0" in temp[2]:
                        dir = 0
                    else:
                        dir = 1
            if maxWeight > -100000:
                break
        return dir







    # Return all match templates for sentence i.
    def matchSent (self, i):
        x = self.sents.getX(i)
        y = self.sents.getY(i)
        preMatch = self.matchWords (self.sents.getPre(i, x))
        intMatch = self.matchWords (self.sents.getInt(i, x, y))
        posMatch = self.matchWords (self.sents.getPos(i, y))
        return (preMatch, intMatch, posMatch)





    # Return all matching templates for words.
    def matchWords (self, words):
        allMatch = []

        for level in self.temps.levels:
            matchesAtThisLevel = []

            for temp in level:
                weight, weightRev = self.locTempInWords (words, temp)
                if weight < 0:
                    matchesAtThisLevel.append((weight, weightRev, temp+" "+level[temp]))

            allMatch.append (matchesAtThisLevel)

        return allMatch









    # Return the weighted sum of index of template token in words in both directions if the template is a subsequence of words.
    # Return 1 otherwise.
    def locTempInWords (self, words, temp):
        tempWords = temp.split()
        j = 0
        weight = 0

        for i in range(len(words)):
            if words[i] == tempWords[j]:
                weight -= (i+1) / math.pow (100, j)
                j += 1
            if j == len(tempWords):
                break

        if j < len(tempWords):
            return (1, 1)

        weightRev = 0
        j = 0
        wordsRev = list(reversed (words))
        tempRev = list(reversed (tempWords))

        for i in range(len(wordsRev)):
            if wordsRev[i] == tempRev[j]:
                weightRev -= (i+1) / math.pow (100, j)
                j += 1
            if j == len(tempRev):
                break

        return (weight, weightRev)












if __name__ == "__main__":
    evils = Evils ("evils.yaml")
    sents = Sentences ("test.yaml", evils)
    temps = Templates ("temp.yaml")
    classifier = Classifier (sents, temps)
    classifier.classify()
    classifier.writeAnswer("answer.yaml")
    #classifier.grade()
