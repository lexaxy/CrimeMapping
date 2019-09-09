import bs4 as bs
import urllib.request
import time
import pandas as pd

maxPages = 1

urlList = list()
headlineList = list()
dateList = list()
fullTextList = list()

for i in range(maxPages):
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

for url in urlList:
    sauce = urllib.request.urlopen(url)
    soup = bs.BeautifulSoup(sauce, 'lxml')
    articleBody = soup.body.find('div', {'itemprop': 'articleBody'})
    text = articleBody.find_all('p')
    textWOTags = ""
    for i in text:
        i = i.contents
        textWOTags += (str(i[0]))
        textWOTags += " "
    fullTextList.append(textWOTags)
    time.sleep(1)
