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

# Get URL from 1. either from command argument
if len(sys.argv) > 1:
    url = sys.argv[1]
if len(sys.argv) > 2:
    musicdir = sys.argv[2]

# or 2. from clipboard
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
# get title section
videotitlesec = re.search('watch-title"\s.+>', html).group(0)
videotitle = re.search('title=".+">', videotitlesec).group(0)[7:-2]
# get title
videotitle = re.sub(
    '\s?\*?\(?([Nn]ew\s)?[Ff]ull\s?[Aa]lbum\*?\)?\s?', '', videotitle, re.IGNORECASE)
titlesplits = re.split('\s?[-|\xe2\x80\x8e\xe2\x80\x93]\s?', videotitle)
if len(titlesplits) > 1:
    interpret, album = titlesplits[0], titlesplits[1]
else:
    interpret = 'N/A'
    album = 'N/A'
print '\n' + 'Interpreter: ' + interpret

# if wrong, correct interpreter and album
newinterp = raw_input('Skip or type in correct INTERPRETER: ')
if newinterp != '':
    interpret = newinterp
print '\n' + 'Album: ' + album
newalbum = raw_input('Skip or type in correct ALBUM name: ')
if newalbum != '':
    album = newalbum

# make dirs
if not os.path.isdir(musicdir + interpret):
    os.mkdir(musicdir + interpret)
albumdir = musicdir + interpret + '/' + album
if not os.path.isdir(albumdir):
    os.mkdir(albumdir)

#  Extract and write track list
description = re.search('eow-description.+</div>', html).group(0)
lines = re.split('<br />', description)
tracklist = interpret + ' - ' + album + '\n\n'
trackparms = []
i = 1
for line in lines:
    if 'seekTo' in line:
        linesearch = re.search('>?([^<>]+)<[^<>]+>([^<>]+)(?:<[^<>]+>([^<>]+))?<?', line)
        if (linesearch.group(3) is None) or (linesearch.group(3) == ')'):
            cline = linesearch.group(1)
            time = linesearch.group(2)
        else: # meaning if the timestamp is somewhere in the middle
            cline = linesearch.group(2)
            time = linesearch.group(3)
        timesearch = re.search(r'(?:(\d+):)?(\d+):(\d+)', time)
        if timesearch is None: # if time and track name are interchanged...
            time, cline = cline, time            
            timesearch = re.search(r'(?:(\d+):)?(\d+):(\d+)', time)
        # add hours to minutes for correct timeformat for mp3splt       
        hours_ = timesearch.group(1)
        if hours_ is not None:          
            minutes = str(int(timesearch.group(2)) + 60*int(hours_))
        else:
            minutes = timesearch.group(2)
        seconds = timesearch.group(3)
        ctitle = re.search(r"[^%d|^(?:0%d)](\w(?:(\w\-\w|[\w\.'&])*\s?)+)" % (i, i),   
                          cline).group(1).strip()
        print '\nTrack Description: ' + cline        
        print 'Estimated Title  : ' + ctitle
        newtitle = raw_input('Skip or type in correct title: ')
        if newtitle != '':
            ctitle = newtitle
        print 'Time Stamp         : ' + time
        print 'Estimated Starttime: ' + minutes + ':' + seconds
        newtime = raw_input('Skip or type in correct starttime "mm:ss": ')
        if newtime != '':
            minutes = re.sub(r':\d+', '', newtime)
            seconds = re.sub(r'\d+:', '', newtime)
        trackparms.append([ctitle, minutes, seconds])
        tracklist += ctitle + ' ' + minutes + ':' + seconds + '\n'
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