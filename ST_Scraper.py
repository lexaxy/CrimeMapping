import bs4 as bs
import urllib.request
import time
import pandas as pd

## global variables
maxPages = 114

## function definitions

def readContentsPages(maxpages):
    # this function scrapes the contents pages of courts-crime articles on Straits Times and
    # returns data frame of URLs, headlines, and dates of articles

    df = pd.DataFrame()
    urlList = list()
    headlineList = list()
    dateList = list()

    for i in range(maxpages):
        sauce = urllib.request.urlopen('https://www.straitstimes.com/singapore/courts-crime?page='+str(i))
        soup = bs.BeautifulSoup(sauce,'lxml')

        stories = soup.body.find_all('span', {'class':'story-headline'})
        dates = soup.body.find_all('div',{'class':'node-postdate'})

        for story in stories:
            urlList.append('https://www.straitstimes.com'+ story.a.get('href'))
            headlineList.append(story.a.string)

        for date in dates:
           dateList.append(date.string)

        time.sleep(1)

    df['url'] = urlList
    df['headline'] = headlineList
    df['date'] = dateList

    return df

def extractFullTextwithTitles(dataframe):
    # this function takes as input the data frame generated from readContentsPages, and visits the article URL
    # and adds another column with the full text of the article to the data frame
    fullTextList = list()
    counter = 0

    for url in dataframe['url']:
        try:
            sauce = urllib.request.urlopen(url)
            soup = bs.BeautifulSoup(sauce, 'lxml')
            articleBody = soup.body.find('div', {'itemprop': 'articleBody'})
            text = articleBody.find_all('p')
            textWOTags = ""
            for para in text:
                sentence = para.contents
                textWOTags += (str(sentence[0]))
                textWOTags += " "
            fullTextList.append(textWOTags)
            time.sleep(1)
            dataframe['full Text'] = fullTextList
            dataframe['full Text'] = dataframe['headline'] + ' - ' + dataframe['full Text']

        except:
            print(url)
            pass
        counter += 1
        if counter%10 == 0:
            print(counter/10)

    return dataframe

def runAreaCounter(dataframe):
    # Checks the full texts from the articles for whether they contain mention of the area. The list
    # of areas is obtained from the data.gov.sg MRT station names with duplicates removed and simplified.
    # The full list of areas considered can be found in the .csv file
    stationNames = pd.read_csv('train-station-names.csv', usecols=["station-names"])
    areaCounter = dict.fromkeys(stationNames['station-names'], 0)

    for text in dataframe['full Text']:
        for area in areaCounter.keys():
            if area in text:
                areaCounter[area] += 1

    print(areaCounter)

## main body

df = readContentsPages(maxPages)
df = extractFullTextwithTitles(df)
runAreaCounter(df)



