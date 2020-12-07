#!/usr/bin/env python3
import os
import subprocess
import sys
from urllib.parse import urljoin

import requests

FFMPEG_BIN = '/usr/bin/ffmpeg'


def execv_cmd(cmd):
    parts = cmd.split(' ')
    file = parts[0]
    os.execv(file, parts)


def get_event_stream_options(*, url, key):
    options_url = urljoin(url, '/events/stream-options')
    req = requests.get(options_url, params=dict(key=key))
    return req.json()


def exec_ffmpeg_youtube(*, key, yt_server, yt_key):
    source = 'rtmp://localhost:1935/live/{key}'.format(key=key)
    yt_url = '{yt_server}/{yt_key}'.format(yt_server=yt_server, yt_key=yt_key)
    cmd = '{ffmpeg_bin} ' \
        '-i {source} ' \
        '-c:v libx264 -b:v 20000k -preset veryfast ' \
        '-c:a copy ' \
        '-f flv ' \
        '{yt_url}'.format(ffmpeg_bin=FFMPEG_BIN, source=source, yt_url=yt_url)
    print("Exec:", cmd)
    execv_cmd(cmd)


def main(*, url, key):
    stream_opts = get_event_stream_options(url=url, key=key)

    # FIXME: For now, support only YouTube
    yt_opts = next(s for s in stream_opts['services'] if s['kind'] == 'YT')
    exec_ffmpeg_youtube(key=key,
                        yt_server=yt_opts['server'],
                        yt_key=yt_opts['key'])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Muxy push script for nginx-rtmp',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--url',
                        required=True,
                        default='http://muxy:8000/',
                        help='Muxy API URL')
    parser.add_argument('--key', required=True, help='Muxy stream key')

    args = parser.parse_args()

    main(url=args.url, key=args.key)
