#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import sys
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests

# Url condiviso contenente i podcast:
basic_url = 'https://static.stage.quentrix.com/ow4geqh4/upfiles/pd/'
podcast_dir = os.path.join(os.path.expanduser('~'), 'Downloads/audible/podcast')
podcast_xml = os.path.join(podcast_dir, 'podcast.xml')
podcast_zip = f'{podcast_dir}.zip'
title_base = performer_base = 'Libriami'
xml_link = urljoin(basic_url, 'podcast.xml')
img_link_base = urljoin(basic_url, 'podcast.png')

performer = title = ''
podcasts = []
img_link = {}
for directory in sorted(os.listdir(podcast_dir)):
    absolute_directory = os.path.join(podcast_dir, directory)
    if os.path.isdir(absolute_directory):
        basic_url_directory = urljoin(basic_url, f'{directory}/')
        for filename in sorted(os.listdir(absolute_directory)):
            absolute_filename = os.path.join(absolute_directory, filename)
            if os.path.isfile(absolute_filename):
                link = urljoin(basic_url_directory, filename)
                name, extension = filename.rsplit('.', 1)
                if extension in ('png', 'jpg'):
                    performer, title = name.split(' - ', 1)
                    img_name = filename
                    img_link[directory] = link
                else:
                    podcasts.append({'name': name, 'link': link, 'directory': directory})

audible_start = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:itunes="https://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:googleplay="https://www.google.com/schemas/play-podcasts/1.0" xmlns:atom="http://www.w3.org/2005/Atom"
     version="2.0" xml:lang="it-IT">
    <channel>
        <atom:link href="{xml_link}" rel="self" type="application/rss+xml"></atom:link>
        <title><![CDATA[{title_base}]]></title>
        <itunes:author>{performer_base}</itunes:author>
        <language>it-it</language>
        <itunes:name>{title_base}</itunes:name>
        <itunes:image href="{img_link_base}"></itunes:image>
        <googleplay:image href="{img_link_base}"></googleplay:image>
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
date = date_now = datetime.now() - timedelta(days=1 * len(podcasts))
date_delta = timedelta(days=1)
for podcast in podcasts:
    date_now = date.strftime('%a, %-d %b %Y %X +0100')
    audible += audible_item % {'performer': performer, 'title': title, 'img_link': img_link[podcast['directory']],
                               'date_now': date_now, 'podcast_name': podcast['name'], 'podcast_link': podcast['link']}
    date += date_delta
audible += audible_end
# todo: controllare se il file esiste già
with open(podcast_xml, 'w') as f:
    f.write(audible)
# todo: controllare se il file esiste già
shutil.make_archive(os.path.splitext(podcast_zip)[0], 'zip', podcast_dir)

with open(podcast_zip, 'rb') as f:
    files = {'file': f}
    response = requests.post('https://bashupload.com', files=files)
print(response.text)
sys.stdout.write(f'\npodcast.xml available at:\n{xml_link}')
