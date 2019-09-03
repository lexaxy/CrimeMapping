import bs4 as bs
import urllib.request
import time

maxPages = 117
urlList = list()
headlineList = list()
dateList = list()

for i in range(maxPages):
    sauce = urllib.request.urlopen('https://www.straitstimes.com/singapore/courts-crime?page='+str(i))
    soup = bs.BeautifulSoup(sauce,'lxml')

    stories = soup.body.find_all('span', {'class':'story-headline'})
    dates = soup.body.find_all('div',{'class':'node-postdate'})

    for story in stories:
        urlList.append(story.a.get('href'))
        headlineList.append(story.a.string)

    for date in dates:
       dateList.append(date.string)

    time.sleep(1)

