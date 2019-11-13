import pandas as pd

def runCounter(dataframe):
    # Checks the full texts from the articles for whether they contain mention of the area. The list
    # of areas is obtained from the data.gov.sg MRT station names with duplicates removed and simplified.
    # The full list of areas considered can be found in the .csv file
    stationNames = pd.read_csv('train-station-names.csv', usecols=["station-names"])
    areaCounter = dict.fromkeys(stationNames['station-names'], 0)

stationNames = pd.read_csv('train-station-names.csv', usecols=["station-names"])
areaCounter = dict.fromkeys(stationNames['station-names'], 0)

violent = frozenset({"murder", "dies", "death", "kidnap", "assault", "manslaughter", "weapon"})

theft = frozenset({"theft","rob","property","burgl", "shoplift"})

commercial = frozenset({"embezzl", "fraud", "corrupt", "bribe"})

sexual = frozenset({"rape", "abuse", "molest", "voyeur", "modesty"})

cheating = frozenset({"cheating", "scam"})

drug = frozenset({"drug", "traffick"})

petty = frozenset({"drunk", "vandal", "speed", "accident"})

crimeCat = {violent, theft, commercial,sexual,cheating,drug,petty}

crimeCounter = dict()

for area in areaCounter.keys():
    for category in crimeCat:
        label = area + "-" + str(category)
        crimeCounter[label] = 0

    
try:
    for text in df['full Text']:
        for area in areaCounter.keys():
            if area in text:
                areaCounter[area] += 1
                for category in crimeCat:
                    for crime in category:
                        if crime in text:
                            label = area + "-" + str(category)
                            crimeCounter[label] += 1
                            break
except:
    pass
        
        
