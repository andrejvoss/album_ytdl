#!/bin/bash
url="$(xclip -o)"
gnome-terminal -e "python /home/miriam/Code/album_ytdl/ytdl.py "$url
