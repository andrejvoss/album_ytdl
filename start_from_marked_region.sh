#!/bin/bash

BASEDIR=$(dirname "$0")
url="$(xclip -o)"
gnome-terminal -e "python $BASEDIR/album_ytdl.py "$url
