import matplotlib.pyplot as plt 
from django.urls import reverse
import csv 
  
x = [] 
y = [] 
  
with open('Weatherdata.csv','r') as csvfile: 
    lines = csv.reader(csvfile, delimiter=',') 
    for row in lines: 
        x.append(row[0]) 
        y.append(int(row[1])) 
  
plt.plot(x, y, color = 'g', linestyle = 'dashed', 
         marker = 'o',label = "Weather Data") 
  
plt.xticks(rotation = 25) 
plt.xlabel('Dates') 
plt.ylabel('Temperature(°C)') 
plt.title('Weather Report', fontsize = 20) 
plt.grid() 
plt.legend() 
plt.show() 
