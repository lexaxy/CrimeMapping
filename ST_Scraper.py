## Step 1: Extract all the links to crime articles from straitstimes.com/singapore/courts-crime link pages
## Set maxPages variable which determines how far back to scrape (max is usually ~117)

import bs4 as bs
import urllib.request
import time
import pandas as pd

#### user-defined variables
maxPages = 12

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

        time.sleep(0.2)

    df['url'] = urlList
    df['headline'] = headlineList
    df['date'] = dateList

    return df


## main body

print("pages to run through: " + str(maxPages))
df = readContentsPages(maxPages)
print("completed reading all contents pages")


## Step 2: Using links that were extracted, visit each page and extract the full text incl. headline
## If webpage is in non-standard format, it is flagged out for manual inspection
 
from datetime import date

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
            time.sleep(0.2)
        except:
            print("non-standard webpage found: " + url)
            fullTextList.append(None)
            pass
        counter += 1
        if counter%10 == 0:
            print("..." + str(int(counter/10)) + "/" + str(maxPages) + "...")

    dataframe['full Text'] = fullTextList
    dataframe['full Text'] = dataframe['headline'] + ' - ' + dataframe['full Text']
    return dataframe

## main body

df = extractFullTextwithTitles(df)
df.to_csv("STscraper_full_" + today.strftime("%d%b") + ".csv")
