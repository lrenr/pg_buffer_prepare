import matplotlib.pyplot as plt 
from django.urls import reverse
import csv 

def avg_func(row, index):
    avg_value = 0
    counter = 0
    for i, elements in enumerate(row):
        if i%5 == index:
            avg_value += float(str(elements).replace(",", "."))
            counter += 1

    return avg_value / counter

def readCSV(path, index):
    output = []
    with open(path,'r') as csvfile: 
        lines = csv.reader(csvfile, delimiter=';')
        skip = True
        for row in lines: 
            if skip:
                skip = False
                continue

            if index == 0:
                output.append(row[0])
            else:
                output.append(avg_func(row, index))
    return output

x = readCSV('pgdefault.csv', 0)
y_pgdefault_shared_hits = readCSV('pgdefault.csv', 3)
y_coldstart_shared_hits = readCSV('coldstart.csv', 3)
y_hotstart_shared_hits = readCSV('hotstart.csv', 3)


y_bonus = []
for i in range(len(y_coldstart_shared_hits)):
    y_bonus.append(y_coldstart_shared_hits[i]-y_hotstart_shared_hits[i])
y_shared_reads = []

  
#plt.plot(x, y_pgdefault_shared_hits, color = 'g', linestyle = 'dashed', marker = 'o',label = "pgdefault") 
#plt.plot(x, y_coldstart_shared_hits, color = 'b', linestyle = 'dashed', marker = 'o',label = "coldstart")
#plt.plot(x, y_hotstart_shared_hits, color = 'r', linestyle = 'dashed', marker = 'o',label = "hotstart")
plt.plot(x, y_bonus, color = 'g', linestyle = 'dashed', marker = 'o',label = "hotstart")
  
plt.xticks(rotation = 90) 
plt.xlabel('Queries') 
plt.ylabel('Shared Hits') 
plt.title('Shared Hits', fontsize = 20)
plt.grid() 
plt.legend() 
plt.show() 
