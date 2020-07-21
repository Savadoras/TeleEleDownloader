import urllib.request
import re
import time
from datetime import datetime
import os
import sys


def get_epoch_time(time_string):
    ts = time.time()
    utc_offset = -(datetime.fromtimestamp(ts) -
                   datetime.utcfromtimestamp(ts)).total_seconds()

    utc_time = datetime.strptime(time_string, "%d-%m-%Y %H:%M")
    return int((utc_time - datetime(1970, 1, 1)).total_seconds() + utc_offset)


def get_channel_list(list_url):
    channels = {}
    file = str(urllib.request.urlopen(list_url).read())
    lines = file.split("#EXTINF:0")
    lines.pop(0)

    for line in lines:
        key = re.search(r"tvg-name=\"(.*?)\"", line).group(1)
        value = re.search(r"https://my\.teleelevidenie\.com/play.*?m3u8", line).group()
        channels[key] = value

    return channels


if len(sys.argv) < 7:
    print("usage: <client_id> <playlist_id> <date dd-mm> <time HH:MM:SS> <channel> <duration HH:MM:SS> <output>")
    exit(0)

client_id = sys.argv[1]
playlist_id = sys.argv[2]
datetime_string = sys.argv[3] + "-" + str(datetime.now().year) + " " + sys.argv[4]
channel = sys.argv[5]
duration = sys.argv[6]
output = sys.argv[7]

link = f'https://my.teleelevidenie.com/play/hls/custom/{client_id}/{playlist_id}'
channels = get_channel_list(link)
epoch_time = get_epoch_time(datetime_string)
if channel not in channels:
    print("Channel not found! Available channels:")
    for key in channels:
        print(key)
    exit(1)

stream_url = channels.get(channel)
stream_url += f"?utc{epoch_time}"

cmd = f'ffmpeg -hide_banner -loglevel warning -y -i {stream_url} -c copy -t {duration} {output}'
os.system(cmd)
