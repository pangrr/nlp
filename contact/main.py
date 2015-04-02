import re
import sys
import yaml
import argparse
from copy import deepcopy




def loadLex(fileName):
    f = open(fileName, "r")
    lex = yaml.safe_load(f)
    f.close()
    return lex



def loadFrame(fileName, rspDict, ontoSet):    # update rspDict and  ontoSet
    f = open(fileName, "r")
    rspDictRaw = yaml.safe_load(f)
    f.close()


    # convert frame from string to list of list
    rspDictPart = {}
    for rsp in rspDictRaw:
        rspDictPart[rsp] = []
        for frameRaw in rspDictRaw[rsp]:
            frame = []
            for position in frameRaw.split():
                frame.append(position.split("/"))
            rspDictPart[rsp].append(frame)


    rspDict.update(rspDictPart)

    # build ontology set
    for rsp in rspDictPart:
        for frame in rspDictPart[rsp]:
            for position in frame:
                for onto in position:
                    ontoSet.add(onto)





def loadCmd(fileName):
    f = open(fileName, "r")
    cmdList = []
    for line in f.readlines():
        try:
            if line.index("?") == 0:
                cmdList.append(re.sub("\#.*", "", line.lstrip("?").lstrip(" ").rstrip("\n")))
        except:
            continue
    f.close()
    return cmdList





def isPhoneNum(string):
    try:
        int(string)
        return True
    except ValueError:
        return False




def isEmailAddr(string):
    try:
        i = string.index("@")
        if i != 0 and i != len(string)-1:
            return True
        else:
            return False
    except ValueError:
        return False




def isPersonName(string, people):
    if string in people:
        return True
    else:
        return False




def parseCmd(cmd, lex, ontoSet, rspDict):
    wordList = cmd.split()
    ontoList = []
    # build  ontology list from command
    for word in wordList:

        # check phone number, email address, lexicon
        if isPhoneNum(word):
            ontoList.append(["valid-phone-number"])
        elif isEmailAddr(word):
            ontoList.append(["valid-email-address"])
        elif word.lower() in lex:
            ontoList.append(lex[word.lower()])

    # compare with frames
    for rsp in rspDict:
        for frame in rspDict[rsp]:
            if matchFrame(ontoList, frame):
                return rsp
    return "FAIL"





def matchFrame(ontoList, frame):
    if len(ontoList) != len(frame):
        return False

    for i in range(len(ontoList)):
        if matchList(ontoList[i], frame[i]) != True:
            return False

    return True





def matchList(l1, l2):
    for e1 in l1:
        for e2 in l2:
            if e1 == e2:
                return True
    return False





def parseCmdList(cmds, lex, ontoSet, rspDict):
    rspList = []
    for cmd in cmds:
        rsp = parseCmd(cmd, lex, ontoSet, rspDict)
        rspList.append(rsp)
    return rspList





def storeRsp(rspList, fileName):
    f = open(fileName, "w")
    for rsp in rspList:
        f.write(rsp + "\n")
    f.close()







# main function
if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(description="Contacts")
    parser.add_argument("-c", "--command_file", help="File that contains the commands")
    args = parser.parse_args()
    if args.command_file:
        cmdList = loadCmd(args.command_file)
    else:
        print("Command file required but not assigned")
        sys.exit()


    # load a bunch of files
    lex = loadLex("lexicon.yaml")

    # load a bunch of frame-response
    rspDict = {}
    ontoSet = set()
    loadFrame("contact_frame.yaml", rspDict, ontoSet)
    loadFrame("phone_frame.yaml", rspDict, ontoSet)
    loadFrame("email_frame.yaml", rspDict, ontoSet)
    loadFrame("text_frame.yaml", rspDict, ontoSet)
    loadFrame("ambiguous_frame.yaml", rspDict, ontoSet)


    # serious work
    rspList = parseCmdList(cmdList, lex, ontoSet, rspDict)


    # write
    storeRsp(rspList, "response")

    print("Done. Check file 'response'.")

