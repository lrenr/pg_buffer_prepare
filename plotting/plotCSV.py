import matplotlib.pyplot as plt
import csv
import numpy as np
from enum import Enum

class Attr():
    QUERY_NAME = 0
    PLANNER_TIME = 1
    EXECUTION_TIME = 2
    SHARED_HITS = 3
    SHARED_READS = 4
    PAGEFAULTS = 0

class OpMode(Enum):
    ATTRIBUTES = 0
    AVG = 1
    SUM = 2

def avg_func(row, index):
    avg_value = 0
    counter = 0
    for i, elements in enumerate(row):
        if i == 0:
            continue

        if i%5 == index:
            avg_value += float(str(elements).replace(",", "."))
            counter += 1

    return avg_value / counter

def readCSV(path, attribute, mode):
    output = []
    with open(path,'r') as csvfile: 
        lines = csv.reader(csvfile, delimiter=';')
        skip = True
        for row in lines: 
            if skip:
                skip = False
                continue
            
            if mode == OpMode.ATTRIBUTES:
                output.append(row[0])
            elif mode == OpMode.AVG or mode == OpMode.SUM:
                output.append(avg_func(row, attribute))

    if mode == OpMode.SUM:
        sum = 0
        for i in output:
            sum += i
        return sum

    return output

def queryToIndex(query):
    queryNames = readCSV('coldstart.csv', Attr.QUERY_NAME, OpMode.ATTRIBUTES)
    for i in range(len(queryNames)):
        if queryNames[i] == query:
            return i
    return -1

def queryToIndexFromTo(start, end):
    queryNames = readCSV('coldstart.csv', Attr.QUERY_NAME, OpMode.ATTRIBUTES)
    count = False
    output = []
    for i in range(len(queryNames)):
        if count == True:
            output.append(i)
            if queryNames[i] == end:
                count = False
        if count == False:
            if queryNames[i] == start:
                count = True
                output.append(i)        
    return output

def subtract(y1, y2):
    y_bonus = []
    for i in range(len(y1)):
        y_bonus.append(y1[i]-y2[i])
    return y_bonus

def plot_Exp1_sum():
    #attr = readCSV('coldstart.csv', Attr.QUERY_NAME , OpMode.ATTRIBUTES)
    shared_hits_coldstart = readCSV('coldstart.csv', Attr.SHARED_HITS, OpMode.SUM)
    shared_reads_coldstart = readCSV('coldstart.csv', Attr.SHARED_READS, OpMode.SUM)
    shared_hits_hotstart = readCSV('hotstart.csv', Attr.SHARED_HITS, OpMode.SUM)
    shared_reads_hotstart = readCSV('hotstart.csv', Attr.SHARED_READS, OpMode.SUM)

    queries = ('coldstart', 'hotstart')
    values = {
        'shared hits': [shared_hits_coldstart, shared_hits_hotstart],
        'shared reads': [shared_reads_coldstart, shared_reads_hotstart],
    }
    width = 0.6  # the width of the bars: can also be len(x) sequence


    fig, ax = plt.subplots()
    bottom = np.zeros(2)

    for labels, count in values.items():
        p = ax.bar(queries, count, width, label=labels, bottom=bottom)
        bottom += count

        ax.bar_label(p, label_type='center', fontsize=14)

    ax.set_title('Relation between sum of average shared hits an sum of shared reads for coldstart and hotstart mode', fontsize=20)
    ax.legend()
    plt.yscale('linear')
    plt.show()

def plot_Exp1_query(queryName):
    #attr = readCSV('coldstart.csv', Attr.QUERY_NAME , OpMode.ATTRIBUTES)
    shared_hits_coldstart = readCSV('coldstart.csv', Attr.SHARED_HITS, OpMode.AVG)
    shared_reads_coldstart = readCSV('coldstart.csv', Attr.SHARED_READS, OpMode.AVG)
    shared_hits_hotstart = readCSV('hotstart.csv', Attr.SHARED_HITS, OpMode.AVG)
    shared_reads_hotstart = readCSV('hotstart.csv', Attr.SHARED_READS, OpMode.AVG)

    queries = ('coldstart', 'hotstart')
    values = {
        'shared hits': [shared_hits_coldstart[queryToIndex(queryName)], shared_hits_hotstart[queryToIndex(queryName)]],
        'shared reads': [shared_reads_coldstart[queryToIndex(queryName)], shared_reads_hotstart[queryToIndex(queryName)]],
    }
    width = 0.6  # the width of the bars: can also be len(x) sequence


    fig, ax = plt.subplots()
    bottom = np.zeros(2)

    for labels, count in values.items():
        p = ax.bar(queries, count, width, label=labels, bottom=bottom)
        bottom += count

        ax.bar_label(p, label_type='center', fontsize=14)

    ax.set_title(f'Comparison of average shared reads and shared hots for query {queryName} in coldstart and hotstart mode', fontsize=20)
    ax.legend()
    plt.yscale('linear')
    plt.show()


def plot_Exp1_reads():
    x = readCSV('pgdefault.csv', Attr.QUERY_NAME, OpMode.ATTRIBUTES)
    y_pgdefault_shared_reads = readCSV('pgdefault.csv', Attr.SHARED_READS, OpMode.AVG)
    y_coldstart_shared_reads = readCSV('coldstart.csv', Attr.SHARED_READS, OpMode.AVG)
    
    plt.plot(x, y_pgdefault_shared_reads, color = 'r', linestyle = 'dotted', marker = 'x',label = "pgdefault")
    plt.plot(x, y_coldstart_shared_reads, color = 'b', linestyle = 'dashdot', marker = 'x',label = "coldstart")

    plt.xticks(rotation = 90) 
    plt.xlabel('queries') 
    plt.ylabel('shared reads') 
    plt.title('Comparision of shared reads', fontsize = 20)
    plt.grid() 
    plt.legend() 
    plt.show() 

def plot_Exp2_planner():
    x = readCSV('pgdefault.csv', Attr.QUERY_NAME, OpMode.ATTRIBUTES)

    labelsToPrint = []
    for i in range(len(x)):
        if len(x[i]) == 6 and x[i][1:][:1] == 'a':
            labelsToPrint.append(i)
        if len(x[i]) == 7 and x[i][2:][:1] == 'a':
            labelsToPrint.append(i)


    y_pgdefault_planner_time = readCSV('pgdefault.csv', Attr.PLANNER_TIME, OpMode.AVG)
    y_coldstart_planner_time = readCSV('coldstart.csv', Attr.PLANNER_TIME, OpMode.AVG)
    y_hotstart_planner_time = readCSV('hotstart.csv', Attr.PLANNER_TIME, OpMode.AVG)
    
    plt.plot(x, y_pgdefault_planner_time, color = '#faa405', linestyle = '', marker = 's',label = "pgdefault")
    plt.plot(x, y_coldstart_planner_time, color = '#152cd4', linestyle = '', marker = 'o',label = "coldstart")
    plt.plot(x, y_hotstart_planner_time, color = '#db0909', linestyle = '', marker = '^',label = "hotstart")
    

    # calculate averages
    avgPgdefault = 0
    avgHotstart = 0
    avgColdstart = 0
    for i in range(len(y_hotstart_planner_time)):
        avgPgdefault += y_pgdefault_planner_time[i]
        avgHotstart += y_hotstart_planner_time[i]
        avgColdstart += y_coldstart_planner_time[i]

    avgPgdefault = avgPgdefault/len(y_pgdefault_planner_time)
    avgHotstart = avgHotstart/len(y_pgdefault_planner_time)
    avgColdstart = avgColdstart/len(y_pgdefault_planner_time)

    print(f'avgPgdefault: {avgPgdefault}')
    print(f'avgColdstart: {avgColdstart}')
    print(f'avgHotstart: {avgHotstart}')



    plt.gca().axes.yaxis.set_ticklabels([])

    plt.xticks(labelsToPrint, rotation = 90)
    plt.xlabel('queries') 
    plt.ylabel('planner times (ms)') 
    plt.title('Comparision of planner times regarding to the three different modes', fontsize = 20)
    plt.grid() 
    plt.legend() 
    plt.show()

def plot_Exp2_executor(queries):

    indexes = []
    for i in queries:
        indexes.append(queryToIndex(i))

    x = readCSV('hotstart.csv', Attr.QUERY_NAME, OpMode.ATTRIBUTES)
    y_pgdefault_execution_time = readCSV('pgdefault.csv', Attr.EXECUTION_TIME, OpMode.AVG)
    y_coldstart_execution_time = readCSV('coldstart.csv', Attr.EXECUTION_TIME, OpMode.AVG)
    y_hotstart_execution_time = readCSV('hotstart.csv', Attr.EXECUTION_TIME, OpMode.AVG)
    queries = []
    y_pgdefault = []
    y_coldstart = []
    y_hotstart = []

    for i in indexes:
        queries.append(x[i])
        y_pgdefault.append(y_pgdefault_execution_time[i])
        y_coldstart.append(y_coldstart_execution_time[i])
        y_hotstart.append(y_hotstart_execution_time[i])

    times = {
        'pgdefault': (y_pgdefault),
        'coldstart': (y_coldstart),
        'hotstart': (y_hotstart),
    }

    x = np.arange(len(queries))
    width = 0.25

    multiplier = 0
    fig, ax = plt.subplots(layout='constrained')

    index = 0
    for attribute, measurement in times.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute, color=['#faa405', '#152cd4', '#db0909'][index%3])
        ax.bar_label(rects, rotation=90, padding=5)
        multiplier += 1
        index += 1

    ax.set_ylabel('Execution Time (ms)')
    ax.set_title('Average execution time of chosen queries')
    ax.set_xticks(x + width, queries, rotation=45)
    ax.legend(loc='upper left', ncols=3)

    # calculate averages
    avgPgdefault = 0
    avgHotstart = 0
    avgColdstart = 0
    for i in range(len(y_hotstart_execution_time)):
        avgPgdefault += y_pgdefault_execution_time[i]
        avgHotstart += y_hotstart_execution_time[i]
        avgColdstart += y_coldstart_execution_time[i]

    avgPgdefault = avgPgdefault/len(y_pgdefault_execution_time)
    avgHotstart = avgHotstart/len(y_pgdefault_execution_time)
    avgColdstart = avgColdstart/len(y_pgdefault_execution_time)

    print(f'avgPgdefault: {avgPgdefault}')
    print(f'avgColdstart: {avgColdstart}')
    print(f'avgHotstart: {avgHotstart}')

    plt.show()

def plot_Exp2_executiontimes(queries):

    indexes = []
    for i in queries:
        indexes.append(queryToIndex(i))

    x = readCSV('hotstart.csv', Attr.QUERY_NAME, OpMode.ATTRIBUTES)

    labelsToPrint = []
    for i in range(len(x)):
        if len(x[i]) == 6 and x[i][1:][:1] == 'a':
            labelsToPrint.append(i)
        if len(x[i]) == 7 and x[i][2:][:1] == 'a':
            labelsToPrint.append(i)


    y_pgdefault_execution_time = readCSV('pgdefault.csv', Attr.EXECUTION_TIME, OpMode.AVG)
    y_coldstart_execution_time = readCSV('coldstart.csv', Attr.EXECUTION_TIME, OpMode.AVG)
    y_hotstart_execution_time = readCSV('hotstart.csv', Attr.EXECUTION_TIME, OpMode.AVG)
    
    queries = []
    y_pgdefault = []
    y_coldstart = []
    y_hotstart = []
    for i in indexes:
        queries.append(x[i])
        y_pgdefault.append(y_pgdefault_execution_time[i])
        y_coldstart.append(y_coldstart_execution_time[i])
        y_hotstart.append(y_hotstart_execution_time[i])


    plt.plot(queries, y_pgdefault, color = '#faa405', linestyle = '', marker = 's',label = "pgdefault")
    plt.plot(queries, y_coldstart, color = '#152cd4', linestyle = '', marker = 'o',label = "coldstart")
    plt.plot(queries, y_hotstart, color = '#db0909', linestyle = '', marker = '^',label = "hotstart")

    #plt.gca().axes.yaxis.set_ticklabels([])

    plt.xticks(rotation = 90)
    plt.xlabel('queries') 
    plt.ylabel('execution time (ms)') 
    plt.title('Comparision of average execution times regarding to the three different modes', fontsize = 12)
    plt.grid() 
    plt.legend() 
    plt.show()

def plot_Exp3_pagefaults(queries):

    indexes = []
    for i in queries:
        indexes.append(queryToIndex(i))

    x = readCSV('hotstart.csv', Attr.QUERY_NAME, OpMode.ATTRIBUTES)

    labelsToPrint = []
    for i in range(len(x)):
        if len(x[i]) == 6 and x[i][1:][:1] == 'a':
            labelsToPrint.append(i)
        if len(x[i]) == 7 and x[i][2:][:1] == 'a':
            labelsToPrint.append(i)


    y_pgdefault_execution_time = readCSV('pgdefault.csv', Attr.PAGEFAULTS, OpMode.AVG)
    y_coldstart_execution_time = readCSV('coldstart.csv', Attr.PAGEFAULTS, OpMode.AVG)
    y_hotstart_execution_time = readCSV('hotstart.csv', Attr.PAGEFAULTS, OpMode.AVG)
    
    queries = []
    y_pgdefault = []
    y_coldstart = []
    y_hotstart = []
    for i in indexes:
        queries.append(x[i])
        y_pgdefault.append(y_pgdefault_execution_time[i])
        y_coldstart.append(y_coldstart_execution_time[i])
        y_hotstart.append(y_hotstart_execution_time[i])


    plt.plot(queries, y_pgdefault, color = '#faa405', linestyle = '', marker = 's',label = "pgdefault")
    plt.plot(queries, y_coldstart, color = '#152cd4', linestyle = '', marker = 'o',label = "coldstart")
    plt.plot(queries, y_hotstart, color = '#db0909', linestyle = '', marker = '^',label = "hotstart")

    #plt.gca().axes.yaxis.set_ticklabels([])

    plt.xticks(rotation = 90)
    plt.xlabel('queries') 
    #plt.yticks(ticks=[min(y_coldstart), max(y_coldstart)])
    plt.ylabel('pagefaults') 
    plt.title('Comparision of average pagefaults regarding to the three different modes', fontsize = 12)
    plt.grid() 
    plt.legend() 
    plt.show()

#plot_Exp1_query('1a.sql')
#plot_Exp1_query('17b.sql')
#plot_Exp1_sum()
#plot_Exp2_planner()
#plot_Exp2_executor(["1a.sql", "5c.sql", "11a.sql", "14b.sql", "21b.sql", "22a.sql", "27c.sql", "28c.sql", "32b.sql", "33c.sql"])
#plot_Exp2_executor(["6a.sql", "9b.sql", "16c.sql", "19a.sql", "25b.sql", "26c.sql", "29b.sql", "31b.sql"])
plot_Exp2_executiontimes(["6a.sql", "6b.sql", "6c.sql", "6d.sql", "6e.sql", "6f.sql", "18b.sql", "18c.sql", "25a.sql", "25b.sql", "25c.sql", "30a.sql", "30b.sql", "30c.sql"])
plot_Exp3_pagefaults(["6a.sql", "6b.sql", "6c.sql", "6d.sql", "6e.sql", "6f.sql", "18b.sql", "18c.sql", "25a.sql", "25b.sql", "25c.sql", "30a.sql", "30b.sql", "30c.sql"])
  
