#!/bin/bash

BASEDIR=$(dirname "$0")
echo "$BASEDIR"
url="$(xclip -o)"
python $BASEDIR/ytdl.py $url
gnome-terminal -e "python $BASEDIR/album_ytdl.py "$url
