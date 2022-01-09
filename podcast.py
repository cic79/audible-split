#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from datetime import datetime

from bs4 import BeautifulSoup

# Url condiviso contenente i podcast:
# https://www.dropbox.com/sh/2zbtmzxkk44qmgk/AACfbAgwyD0A9TAB3EdANO9ja?dl=0
CONTENT = '''
<html>
<table role="table" class="mc-table sl-list-container"></table>
</html>
'''
performer = title = ''
podcasts = []
xml_name = xml_link = img_name = img_link = None
soup = BeautifulSoup(CONTENT, 'html.parser')
results = soup.find(class_='mc-table').find_all('a', class_='')
for result in results:
    link = result.attrs['href'].split('?')[0] + '?dl=1'
    filename = result.attrs['aria-label']
    name, extension = filename.rsplit('.', 1)
    if extension == 'xml':
        xml_name = filename
        xml_link = link
    elif extension in ('png', 'jpg'):
        performer, title = name.split(' - ', 1)
        img_name = filename
        img_link = link
    else:
        podcasts.append({'name': name, 'link': link})

if not(xml_name and xml_link and img_name and img_link):
    sys.stderr.write('ERROR: Houston we have a problem! At least one file not found (xml or image).')
    exit(1)

audible_start = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:itunes="https://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:googleplay="https://www.google.com/schemas/play-podcasts/1.0" xmlns:atom="http://www.w3.org/2005/Atom"
     version="2.0" xml:lang="it-IT">
    <channel>
        <atom:link href="{xml_link}" rel="self" type="application/rss+xml"></atom:link>
        <title><![CDATA[{title}]]></title>
        <itunes:author>{performer}</itunes:author>
        <language>it-it</language>
        <itunes:name>{title}</itunes:name>
        <itunes:image href="{img_link}"></itunes:image>
        <googleplay:image href="{img_link}"></googleplay:image>
'''
audible_item = '''
        <item>
            <title><![CDATA[%(podcast_name)s]]></title>
            <link>%(podcast_link)s</link>
            <description>%(title)s</description>
            <itunes:author>%(performer)s</itunes:author>
            <itunes:image href="%(img_link)s"></itunes:image>
            <googleplay:image href="%(img_link)s"></googleplay:image>
            <enclosure length="10000" type="audio/mpeg" url="%(podcast_link)s"></enclosure>
            <pubDate>%(date_now)s</pubDate>
            <guid>%(podcast_link)s</guid>
        </item>
'''
audible_end = '''
    </channel>
</rss>'''
audible = audible_start
for podcast in podcasts:
    date_now = datetime.now().strftime('%a, %-d %b %Y %X +0100')
    audible += audible_item % {'performer': performer, 'title': title, 'img_link': img_link, 'date_now': date_now,
                               'podcast_name': podcast['name'], 'podcast_link': podcast['link']}
audible += audible_end
with open('podcast.xml', 'w') as f:
    f.write(audible)

sys.stdout.write(f'\npodcast.xml available at:\n{xml_link}')
