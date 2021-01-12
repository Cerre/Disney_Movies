from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from collections import defaultdict
import regex as re
import datetime


def get_all_urls(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    div = soup.find('div', class_= 'mw-parser-output')
    tables = div.find_all('table', class_= 'wikitable sortable')#, class_ = 'wikitable sortable jquery-tablesorter')
    for table in tables:
        boxes = table.find_all('a', title = True)
        for box in boxes:
            print(box['title'])

        # rows = table.find_all('tr')
        # for row in rows:
        #     obj = row.find('i', recursive=True)
        #     print(obj.title)



def request_from_webiste(url):
    r = requests.get(url);
    soup = BeautifulSoup(r.text, 'html.parser');
    soup.prettify();
    return soup

def gather_data(soup):
    infobox = soup.find_all('table',class_='infobox vevent')
    info_dict = defaultdict()
    for table in infobox:
        rows = table.find_all('tr')
        for row in rows:
            attributes = row.find_all('th', recursive=True)
            information = row.find_all('td')
            for attribute, info in zip(attributes,information):
                key = attribute.text
                value = list(filter(lambda x: x!='',info.text.split('\n')))
                info_dict[key] = value
    for key, values in info_dict.items():
        print(key, values)
    return info_dict


def cleanup_values(info_dict):
    info_dict = remove_brackets(info_dict)


    return info_dict

def remove_brackets(info_dict):
    for key,  value in info_dict.items():
        info_dict[key] = list(map(lambda x: re.sub("[\[].*?[\]]", "", x), value))

    return info_dict


def fix_dates(info_dict):
    info_dict['Release date'] = list(map(lambda x: re.findall('\(([^)]+)', x), info_dict['Release date']))

    info_dict['Box office'] = list(map(lambda x: x.replace('\xa0',u' '), info_dict['Box office']))
    info_dict['Box office'] = list(map(lambda x: x.replace('$',u''), info_dict['Box office']))

    info_dict['Budget'] = list(map(lambda x: x.replace('\xa0',u' '), info_dict['Budget']))
    info_dict['Budget'] = list(map(lambda x: x.replace('$',u''), info_dict['Budget']))

    return info_dict



def main():
    base_url = 'https://en.wikipedia.org/wiki/List_of_Walt_Disney_Pictures_films'
    get_all_urls(base_url)


    





    # url = 'https://en.wikipedia.org/wiki/Toy_Story_3'
    # soup = request_from_webiste(url)
    # info_dict_raw = gather_data(soup)
    # info_dict = cleanup_values(info_dict_raw)
    # info_dict = fix_dates(info_dict)
    
    
    
    # for key, values in info_dict.items():
    #     print(key, values)

main()