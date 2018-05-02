# coding: utf-8
# In[53]:
import json
import re

import requests
import scrapy

# In[54]:

headers = {'User-Agent': 'Annie G'}

# In[55]:
base_url = 'https://www.billboard.com/charts'
url = base_url + '/artist-100/'

# In[56]:
resp = requests.get(url, headers=headers)
body_str = resp.content.decode('utf-8')
sel = scrapy.Selector(text=body_str)
table = sel.css('div.chart-data')

rows = table.css('article.chart-row')[0:]

chartName = sel.css('div.chart-header-headline').css('h1.chart-name').css('span').xpath('text()').extract_first()
curWeek = sel.css('div.chart-data-header').css('nav.chart-nav').css('time').xpath('@datetime').extract_first()
fileName = chartName.replace(" ", "_").lower() +"-" + curWeek.replace("-","_")

# In[66]:

songs = []
primary = rows.css('div.chart-row__primary')
secondary = rows.css('div.chart-row__secondary')
for i, r in enumerate(rows):
    data = {}
    data["rank"] = i+1

    mainDisplay = primary.css('div.chart-row__main-display')[i]
    container = mainDisplay.css('div.chart-row__container')

    #TITLE
    title = container.css('div.chart-row__title').css('h2.chart-row__song').xpath('text()').extract_first()
    if "album" in url:
        data["album"] = title
    elif "artist" not in url:
        data["song"] = title


    #ARTIST & #HREF
    artist = container.css('div.chart-row__title').css('a.chart-row__artist').xpath('text()').extract()
    href = container.css('div.chart-row__title').css('a.chart-row__artist').xpath('@href').extract_first()
    if (len(artist) < 1):
        artist = container.css('div.chart-row__title').css('span.chart-row__artist').xpath('text()').extract()
        data["href"] = None
    else:
        data["href"] = base_url + href
    data["artist"] = re.search('(?<=\\n)(.*?)(?=\\n)', artist[0]).group(0) #extract first here

    #IMG
    imgText = primary.css('div.chart-row__image').extract()[i]
    image = re.search('(?<=url\()(.*?)(?=\))', imgText)
    if image is not None:
        data["img"] = image.group(0)
    else:
        imgText = primary.css('div.chart-row__image')[i].xpath('@data-imagesrc').extract_first()
        data["img"] = imgText

    stats = secondary.css('div.chart-row__stats')[i]
    #LAST WEEK
    # lastWeek = mainDisplay.css('div.chart-row__rank').css('span.chart-row__last-week').xpath('text()').extract_first()
    lastWeek = stats.css('div.chart-row__last-week').css('span.chart-row__value').xpath('text()').extract_first()
    try:
        data["last_week"] = int(lastWeek)
    except ValueError:
        data["last_week"] = None

    #WEEKS ON CHART
    woc = stats.css('div.chart-row__weeks-on-chart').css('span.chart-row__value').xpath('text()').extract_first()
    try:
        data["weeks_on_chart"] = woc
    except ValueError:
        data["weeks_on_chart"] = None

    #PEAK POSITION
    pp = stats.css('div.chart-row__top-spot').css('span.chart-row__value').xpath('text()').extract_first()
    try:
        data["peak_position"] = pp
    except ValueError:
        data["peak_position"] = None

    print("ADDED " + str(data["rank"]) + " " + data["artist"] + " to JSON")

    songs.append(data)

# to_django
django = []
for i, d in enumerate(songs):
    data = {}
    data["pk"] = i+1
    data["model"] = "bbsite.Artist"
    data["fields"] = d
    django.append(data)

to_dump = [p.copy() for p in songs]
with open(fileName + ".json", 'w') as f:
    json.dump(to_dump, f)

with open(fileName + "_DJANGO.json", 'w') as f:
    json.dump(django, f)
