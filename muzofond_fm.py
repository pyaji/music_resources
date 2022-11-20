#!/usr/bin/env python
from requests import get
import sys
import re
import tqdm
from bs4 import BeautifulSoup
from mutagen.easyid3 import EasyID3

BASE_URL = 'https://muzofond.fm/'


def download_file(url: str, filename: str):
    r = get(url, allow_redirects=True)
    with open(filename, 'wb') as f:
        f.write(r.content)
    return filename


def item_to_data_to_download(item: BeautifulSoup):
    url = item.select_one('li.play').attrs['data-url']
    autor_name = item.select_one('.desc h3 .artist').get_text().strip()
    track_name = item.select_one('span.track').get_text().strip()
    return {
        'url': url,
        'artist': autor_name,
        'title': track_name
    }


def get_urls(url: str) -> list:
    resp = get(url)
    text = resp.text
    soup = BeautifulSoup(text, 'html.parser')
    data = [item_to_data_to_download(d)
            for d in soup.select('.mainSongs li.item')]
    return data


def set_attrs_to_file(filename: str, attrs: dict):
    f = EasyID3(filename)
    for attr, val in attrs.items():
        if attr != 'url':
            f[attr] = val
    f.save()


def start_download(url: str):
    urls = get_urls(url)
    for i, data in tqdm.tqdm(enumerate(urls)):
        _url = data['url']
        filename = f'track_{i}.mp3'
        download_file(_url, filename)
        set_attrs_to_file(filename, data)


def check_url(arg: str):
    return arg.startswith(BASE_URL)


if __name__ == '__main__':
    args = sys.argv
    if len(args) == 2 and check_url(args[1]):
        start_download(args[1])
