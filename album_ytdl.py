# -*- coding: utf-8 -*-

"""
Requires "youtube-dl" and "mp3splt" for command line
Created on Sun May  8 14:57:22 2016
@author: andrej
"""

import sys
import os
import re
from urlparse import urlparse
from urllib import urlopen

musicdir = os.path.expanduser('~/Music/')

# Get URL from command argument
if len(sys.argv) > 1:
    url = sys.argv[1]
if len(sys.argv) > 2:
    musicdir = sys.argv[2]

# Get URL from clipboard
try:
    # Python2
    import Tkinter as tk
except ImportError:
    # Python3
    import tkinter as tk
root = tk.Tk()
# keep the window from showing

root.withdraw()
c = root.clipboard_get()
if urlparse(c).netloc == 'www.youtube.com':
    url = c

#
#  Extract Information from YouTube page
#
html = urlopen(url).read()
videotitlesec = re.search('watch-title"\s.+>', html).group(0)

videotitle = re.search('title=".+">', videotitlesec).group(0)[7:-2]
videotitle = re.sub(
    '\s?\(?([Nn]ew\s)?[Ff]ull\s[Aa]lbum\s?\)?', '', videotitle, re.IGNORECASE)
titlesplits = re.split('\s?[-|\xe2\x80\x8e\xe2\x80\x93]\s?', videotitle)
if len(titlesplits) > 1:

    interpret, album = titlesplits[0], titlesplits[1]
else:
    interpret = 'N/A'

    album = 'N/A'
print '\n' + 'Interpreter: ' + interpret
# if raw_input('Correct? [Y/n]: ') in ['N','n']:

newinterp = raw_input('Skip or type in correct INTERPRETER: ')
if newinterp != '':
    interpret = newinterp

print '\n' + 'Album: ' + album
newalbum = raw_input('Skip or type in correct ALBUM name: ')
if newalbum != '':

    album = newalbum
description = re.search('eow-description.+</div>', html).group(0)
lines = re.split('<br />', description)

if not os.path.isdir(musicdir + interpret):
    os.mkdir(musicdir + interpret)

albumdir = musicdir + interpret + '/' + album
if not os.path.isdir(albumdir):
    os.mkdir(albumdir)

#
#  Extract and write track list
#

tracklist = interpret + ' - ' + album + '\n\n'
trackparms = []

i = 1
for line in lines:
    if 'seekTo' in line:

        cline = re.sub('<([^>]*)>', '', line)
        print '\n' + cline
        tracklist += cline + '\n'

        starttime = re.search(r'(\d+:\d+)', cline).group(0)
        cline = re.sub(r'(\d+:\d+)', '', cline)
        title = re.search(
            r'[^(0%d)|^%d|^-|^.|^\s]+([A-z|0-9|\.]+\s)*' % (i, i),
                          cline).group(0).strip()

        ctitle = re.sub(r'\d+[\.\s|\s|-]+', '', title)
        print 'Title: ' + ctitle

        newtitle = raw_input('Skip or type in correct title: ')
        if newtitle != '':
            ctitle = newtitle

        print 'Starttime: ' + starttime
        newtime = raw_input('Skip or type in correct starttime "mm:ss": ')
        if newtime != '':

            starttime = newtime
        minutes = re.sub(r':\d+', '', starttime)
        seconds = re.sub(r'\d+:', '', starttime)

        trackparms.append([ctitle, minutes, seconds])
        i += 1

tracklist_file = open(albumdir + '/tracklist.txt', 'w')
tracklist_file.write(tracklist)
tracklist_file.close()
print trackparms

#
#  Download the album and convert it to mp3
#

urlq = '"' + url + '"'
os.system('youtube-dl --extract-audio --audio-format mp3 --audio-quality 0 '

          + urlq + ' -o "' + albumdir + '/albumraw.tmp"')
#
#  Split the album into different tracks
#

for i in range(1, len(trackparms) + 1):
    track = trackparms[i - 1][0]

    starttime = str(trackparms[i - 1][1]) + '.' + str(trackparms[i - 1][2])
    outpath = '"' + interpret + ' - (' + str(i) + ') ' + track + '"'
    if i < len(trackparms):

        stoptime = str(trackparms[i][1]) + '.' + str(trackparms[i][2]) + ' '
        os.system('mp3splt "' + albumdir + '/albumraw.mp3"' + ' ' +
                  starttime + ' ' + stoptime + '-o ' + outpath +

                  ' -g [@a="' + interpret + '",@b="' + album + '",' +
                  '@t="' + track + '",@n="' + str(i) + '"]')
    else:

        os.system('mp3splt "' + albumdir + '/albumraw.mp3"' + ' ' +
                  starttime + ' ' + '9999.00' + ' -o ' + outpath +
                  ' -g [@a="' + interpret + '",@b="' + album + '",' +

                  '@t="' + track + '",@n="' + str(i) + '"]')
if raw_input('Remove raw album? [Y/n]: ') in ['', 'Y', 'y']:
    os.system('rm "' + albumdir + '/albumraw.mp3"')
