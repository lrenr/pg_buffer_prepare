import copy
from pathlib import Path
import functools
import sys

SEP = "; "
#MODE = "pgdefault"
#MODE = "coldstart"
MODE = "hotstart"

queriesPathList = Path("./postgres/queries/").glob('**/*.sql')
tmpPath = "./postgres/queries-outp/" + MODE
jsonPathList = Path(tmpPath).glob('**/*.json')

def convertQueryHelper(letter):
    if letter == 'a':
        return float(0.1)
    if letter == 'b':
        return float(0.2)
    if letter == 'c':
        return float(0.3)
    if letter == 'd':
        return float(0.4)
    if letter == 'e':
        return float(0.5)
    if letter == 'f':
        return float(0.6)
    if letter == 'g':
        return float(0.7)
    return float(0.0)

def sortQueries(q1, q2):
    q1 = str(q1).split(".")[0]
    q2 = str(q2).split(".")[0]
    if len(q1) == 2:
        # q1=1a
        q1 = float(q1[:1]) + float(convertQueryHelper(q1[-1:]))
    elif len(q1) == 3:
        # q1=10a
        q1 = float(q1[:2]) + convertQueryHelper(q1[-1:])

    if len(q2) == 2:
        # q1=1a
        q2 = float(q2[:1]) + convertQueryHelper(q2[-1:])
    elif len(q2) == 3:
        # q1=10a
        q2 = float(q2[:2]) + convertQueryHelper(q2[-1:])

    if q1 < q2:
        return -1
    else:
        return 1
    
def getJsonFiles(query):

    #print("getJsonFiles")
    
    jsonFiles = []
    tmpPath = "./postgres/queries-outp/" + MODE
    for file in Path(tmpPath).glob('**/*.json'):
        if str(file).split("/")[-1:][0][:-5] == str(query):
            jsonFiles.append(str(file))
    return jsonFiles

def getAttrFromJson(path):
    with open(path, "r") as f:
        data = f.read()

        plannerTime = float(data.split("PlanningTime")[1].split(",")[0][2:])
        executionTime = float(data.split("ExecutionTime")[1].split(",")[0][2:].split("}")[0])
        sharedHits = int(data.split("SharedHitBlocks")[1].split(",")[0][2:])
        sharedReads = int(data.split("SharedReadBlocks")[1].split(",")[0][2:])

        f.close()

    memstatStart = 0
    pathMemstat = str(path)[:-5] + "_memstat_start"
    with open(pathMemstat, "r") as f:
        #print(pathMemstat)
        #print("---" + f.read()[8:].replace("\n", "") + "---")
        memstatStart = int(f.read()[8:].split("\n")[0])
        f.close()

    memstatEnd = 0
    pathMemstat = str(path)[:-5] + "_memstat_end"
    with open(pathMemstat, "r") as f:
        memstatEnd = int(f.read()[8:].split("\n")[0])
        f.close()

    pgfaults = memstatEnd-memstatStart

    return (plannerTime, executionTime, sharedHits, sharedReads, pgfaults)


# get query names
queriesList = []
for query in queriesPathList:
    queriesList.append(str(query).split("/")[2])

queriesList = sorted(queriesList, key=functools.cmp_to_key(sortQueries))
#print(queriesList)

csvOutput = "Query; PlannerTime_1; ExecutionTime_1; SharedHits_1; SharedReads_1; PageFaults_1 \
                    ; PlannerTime_2; ExecutionTime_2; SharedHits_2; SharedReads_2; PageFaults_2 \
                    ; PlannerTime_3; ExecutionTime_3; SharedHits_3; SharedReads_3; PageFaults_3 \
                    ; PlannerTime_4; ExecutionTime_4; SharedHits_4; SharedReads_4; PageFaults_4 \
                    ; PlannerTime_5; ExecutionTime_5; SharedHits_5; SharedReads_5; PageFaults_5 \
                    ; PlannerTime_6; ExecutionTime_6; SharedHits_6; SharedReads_6; PageFaults_6 \
                    ; PlannerTime_7; ExecutionTime_7; SharedHits_7; SharedReads_7; PageFaults_7 \
                    ; PlannerTime_8; ExecutionTime_8; SharedHits_8; SharedReads_8; PageFaults_8 \
                    ; PlannerTime_9; ExecutionTime_9; SharedHits_9; SharedReads_9; PageFaults_9 \
                    ; PlannerTime_10; ExecutionTime_10; SharedHits_10; SharedReads_10; PageFaults_10\n"

for query in queriesList:
    csvOutput += query

    jsonFiles = getJsonFiles(query)
    #print(query)
    #print(jsonFiles)
    for file in jsonFiles:
        values = getAttrFromJson(file)
        csvOutput += SEP + str(values[0]).replace(".", ",")
        csvOutput += SEP + str(values[1]).replace(".", ",")
        csvOutput += SEP + str(values[2])
        csvOutput += SEP + str(values[3])
        csvOutput += SEP + str(values[4])
    #print("--------------------------")

    csvOutput += "\n"

#print(csvOutput)

tmpPath = "./postgres/queries-outp/" + MODE + "/" + MODE + ".csv"
with open(tmpPath, "w") as f:
    f.write(csvOutput)
    f.close