# In[100]:

## Requires ST Scraper.py to scrape crime articles from straitstimes.com into a .csv file first
## Analyzes full text of crime articles from .csv file to determine:
## Firstly, number of crimes in vicinity of each MRT/LRT location
## Secondly, most common types of crimes in vicinity of each MRT/LRT location

import pandas as pd

df = pd.read_csv('STscraper_full_14Nov.csv')

# In[101]:

## Presenting three ways of analyzing the text obtained
## First implementation of a counter of crime in each area using a dictionary

def runAreaCounter(dataframe):
    # Checks the full texts from the articles for whether they contain mention of the area. The list
    # of areas is obtained from the data.gov.sg MRT station names with duplicates removed and simplified.
    # The full list of areas considered can be found in train-station-names.csv file
    stationNames = pd.read_csv('train-station-names.csv', usecols=["station-names"])
    areaCounter = dict.fromkeys(stationNames['station-names'], 0)
    
    try:
        for text in dataframe['full Text']:
            for area in areaCounter.keys():
                if area in text:
                    areaCounter[area] += 1
    except:
        pass

  
    print(areaCounter)
    
runAreaCounter(df)


# In[102]:

## Second implementation of a counter of crime in each area using a PD instead of a dict for easy manipulation

def runAreaCounter(dataframe):
    # Checks the full texts from the articles for whether they contain mention of the area. The list
    # of areas is obtained from the data.gov.sg MRT station names with duplicates removed and simplified.
    # The full list of areas considered can be found in train-station-names.csv file
    stationNames = pd.read_csv('train-station-names.csv', usecols=["station-names"])
    areaCounter = pd.Series(0, index = stationNames['station-names'])

    try:
        for text in dataframe['full Text']:
            for index,value in areaCounter.items():
                if index in text:
                    areaCounter[index] += 1
    except:
        pass

    print(areaCounter)
    print(sum(areaCounter))
    
runAreaCounter(df)


# In[103]:

## Third implementation. Why? So as to get not only counter of crime in each area but also types of crime in each area
## Uses a dictionary of dictionaries that maps area to (1) crimeCount, (2) full crimeText, and (3) crimeWords picked up

#### User-defined crime categories 

violent = {"murder", "kidnap", "assault", "manslaughter", "weapon", "dies", "dead", "fight","gang"}
theft = {"theft","rob","property","burgl", "shoplift","steal"}
commercial = {"embezzl", "fraud", "corrupt", "bribe", "moonlighting", "false", "contravene"}
sexual = {"rape", "abuse", "molest", "voyeur", "outrage of modesty", "grope", "underage",
         "having sex", "upskirt", "lingerie", "undergarment", "flashing", "sleaze", "sexual", "indecent"}
cheating = {"cheating", "scam", "extort", "tax"}
drugandcustoms = {"drug", "traffick", "vape", "contraband", "smuggle"}
car = {"drunk", "speed", "hit-and-run", "collide"}
petty = {"vandal", "non-compliance","accident","unlicensed", "contravened","rash act", "prank", "breach"}

crimeWordList = set.union(violent,theft,commercial,sexual,cheating,drugandcustoms,car,petty)

# Checks the full texts from the articles for whether they contain mention of the area from train-station-names.csv file
# If area exists, analyzes full text for crimeWord and maps that to the area
# If no crimeWord was picked up, text is printed out for manual inspection if a keyword can be added to the categories above

stationNames = pd.read_csv('train-station-names.csv', usecols=["station-names"])

areaCounterCrime = {i:{'crimeCount':0, 'crimeText':[], 'crimeWords':[]} for i in stationNames["station-names"]}
try:
    for text in df['full Text']:
        for area in areaCounterCrime.keys():
                if area in text:
                    areaCounterCrime[area]['crimeCount'] += 1
                    areaCounterCrime[area]['crimeText'].append(text)
                    crimes = []
                    for crimeWord in crimeWordList:
                        if crimeWord in text:
                            crimes.append(crimeWord)
                    if len(crimes) == 0:
                        print("...Not picked up...")
                        print(text)
                    else:
                        areaCounterCrime[area]['crimeWords'].append(crimes)
                    
except:
    pass


# In[104]:

## Let's see what keywords we picked up for crimes in Woodlands

print(areaCounterCrime['Woodlands']['crimeCount'])
for crime in areaCounterCrime['Woodlands']['crimeWords']:
    print(crime)


# In[105]:

## Let's see what keywords we picked up for crimes in Jurong East

print(areaCounterCrime['Jurong East']['crimeCount'])
for crime in areaCounterCrime['Jurong East']['crimeWords']:
    print(crime)


# In[106]:

## Let's see what keywords we picked up for crimes in Clementi


print(areaCounterCrime['Clementi']['crimeCount'])
for crime in areaCounterCrime['Clementi']['crimeWords']:
    print(crime)


# In[107]:

## We will use two methods of visualisation. Firstly a wordcloud, and secondly a bar chart. First for wordcloud

from wordcloud import WordCloud
import matplotlib.pyplot as plt

wcWoodlands = WordCloud().generate(' '.join(sum(areaCounterCrime['Woodlands']['crimeWords'],[])))

plt.imshow(wcWoodlands)
plt.axis("off")
plt.show()


# In[108]:

## From wordcloud, seems that Woodlands has highest drugs and violent cases, and moderate theft and sexual cases
## To see if this is really true, let's look at a bar chart of crime types in Woodlands. 

# To do so, we first map each crimeWord to a category using a dictionary called crimeTypes

crimeTypes = dict()

crimeCats = [violent,theft,commercial,sexual,cheating,drugandcustoms,car,petty]
crimeCatNames = ["violent","theft","commercial","sexual","cheating","drugandcustoms","car","petty"]

for i in range(len(crimeCats)):
    crimeTypes.update(dict.fromkeys(crimeCats[i],crimeCatNames[i]))

crimeTypes


# In[127]:

# Next we count the number of crimes in each category and plot the total in each category

crimeWordCounter = dict.fromkeys(crimeWordList, 0)

for j in (sum(areaCounterCrime['Woodlands']['crimeWords'],[])):
    crimeWordCounter[j] += 1

catCounter = dict.fromkeys(crimeCatNames, 0)

for k,v in crimeWordCounter.items():
    catCounter[crimeTypes[k]] += v

fig = plt.figure(1, [10,8])

plt.bar(range(len(catCounter)), list(catCounter.values()), align='center')
plt.xticks(range(len(catCounter)), list(catCounter.keys()))

plt.show()


# In[129]:

## Doing the same for Orchard

# Wordcloud
wcOrchard = WordCloud().generate(' '.join(sum(areaCounterCrime['Orchard']['crimeWords'],[])))

plt.imshow(wcOrchard)
plt.axis("off")
plt.show()

# Bar Chart

crimeWordCounter = dict.fromkeys(crimeWordList, 0)

for j in (sum(areaCounterCrime['Orchard']['crimeWords'],[])):
    crimeWordCounter[j] += 1

catCounter = dict.fromkeys(crimeCatNames, 0)

for k,v in crimeWordCounter.items():
    catCounter[crimeTypes[k]] += v

fig = plt.figure(1, [10,8])

plt.bar(range(len(catCounter)), list(catCounter.values()), align='center')
plt.xticks(range(len(catCounter)), list(catCounter.keys()))

plt.show()


# In[130]:

## Bedok

# Wordcloud

wcBedok = WordCloud().generate(' '.join(sum(areaCounterCrime['Bedok']['crimeWords'],[])))

plt.imshow(wcBedok)
plt.axis("off")
plt.show()

# Bar Chart

crimeWordCounter = dict.fromkeys(crimeWordList, 0)

for j in (sum(areaCounterCrime['Bedok']['crimeWords'],[])):
    crimeWordCounter[j] += 1

catCounter = dict.fromkeys(crimeCatNames, 0)

for k,v in crimeWordCounter.items():
    catCounter[crimeTypes[k]] += v

fig = plt.figure(1, [10,8])

plt.bar(range(len(catCounter)), list(catCounter.values()), align='center')
plt.xticks(range(len(catCounter)), list(catCounter.keys()))

plt.show()


# In[131]:

## Now for all areas

# Wordcloud

allAreas =[]
for area in areaCounterCrime:
    allAreas = sum(areaCounterCrime[area]['crimeWords'], allAreas)
    

wcOverall = WordCloud().generate(' '.join(allAreas))

plt.imshow(wcOverall)
plt.axis("off")
plt.show()

# Bar Chart

crimeWordCounter = dict.fromkeys(crimeWordList, 0)

for j in allAreas:
    crimeWordCounter[j] += 1

catCounter = dict.fromkeys(crimeCatNames, 0)

for k,v in crimeWordCounter.items():
    catCounter[crimeTypes[k]] += v

fig = plt.figure(1, [10,8])

plt.bar(range(len(catCounter)), list(catCounter.values()), align='center')
plt.xticks(range(len(catCounter)), list(catCounter.keys()))

plt.show()

