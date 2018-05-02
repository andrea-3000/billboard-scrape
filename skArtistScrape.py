import json
import re

import requests
import scrapy
import songkick

songkick = Songkick(apikey='s9jRvOcn6wAC8gME')

events = songkick.event_search.query(artist_name='Cardi B')

# iterate over the list of events
for event in events:
    print(event.display_name)        # Coltrane Motion at Arlene's Grocery (June 2, 2010)
    print(event.location.city)       # New York, NY, US
    print(event.venue.display_name)  # Arlene's Grocery
