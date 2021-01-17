from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from collections import defaultdict
import regex as re
import datetime
import pickle
import json

def get_all_urls(base_url, url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    movies = soup.select('.wikitable.sortable i')
    links = defaultdict()
    for movie in movies:
        try:
            title = movie.a['title']
            href = movie.a['href']
            links[title] = base_url + href
        except:
            continue
    return links


def request_from_webiste(url):
    # import pdb
    # pdb.set_trace()
    r = requests.get(url);
    soup = BeautifulSoup(r.text, 'html.parser');
    soup.prettify();
    return soup

def gather_data_from_box(soup):
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
    info_dict = cleanup_values(info_dict)
    return info_dict


def cleanup_values(info_dict):
    info_dict = remove_brackets(info_dict)
    info_dict = fix_dates(info_dict)
    return info_dict

def remove_brackets(info_dict):
    for key,  value in info_dict.items():
        info_dict[key] = list(map(lambda x: re.sub("[\[].*?[\]]", "", x), value))
    return info_dict


def fix_dates(info_dict):
    if 'Release date' in info_dict.keys():
        info_dict['Release date'] = list(map(lambda x: re.findall('\(([^)]+)', x), info_dict['Release date']))
        # info_dict['Release date'] = list(map(lambda x: x.replace('\xa0',u' '), info_dict['Release date']))
    if 'Box office' in info_dict.keys():
        info_dict['Box office'] = list(map(lambda x: x.replace('\xa0',u' '), info_dict['Box office']))
        info_dict['Box office'] = list(map(lambda x: x.replace('$',u''), info_dict['Box office']))
    if 'Budget' in info_dict.keys():
        info_dict['Budget'] = list(map(lambda x: x.replace('\xa0',u' '), info_dict['Budget']))
        info_dict['Budget'] = list(map(lambda x: x.replace('$',u''), info_dict['Budget']))

    return info_dict


def build_db(links):
    db = defaultdict()
    i = 1
    N = len(links)
    for key, value in links.items():
        soup = request_from_webiste(value)
        box = gather_data_from_box(soup)
        db[key] = box
        print(str(i) + ' / ' + str(N))
        i += 1
    return db



def create_db(base_url, list_url):
    links = get_all_urls(base_url,list_url)
    movie_db = build_db(links)
    filehandler = open('movie_db', 'wb') 
    pickle.dump(movie_db, filehandler)
    filehandler.close()
    print("Created database and pickled into movie_db")

def load_db():
    infile = open("movie_db",'rb')
    db = pickle.load(infile)
    infile.close()
    return db

def write_to_json(db):
    with open('movie_db.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

def load_from_json(db):
    db = load_data("movie_db.json")

def main():
    list_url = 'https://en.wikipedia.org/wiki/List_of_Walt_Disney_Pictures_films'
    base_url = 'https://en.wikipedia.org'
    # db = create_db(base_url, list_url)
    db = load_db()
    write_to_json(db)

    






    # url = 'https://en.wikipedia.org/wiki/Toy_Story_3'
    # soup = request_from_webiste(url)
    # info_dict_raw = gather_data(soup)
    # info_dict = cleanup_values(info_dict_raw)
    # info_dict = fix_dates(info_dict)
    
    
    
    # for key, values in info_dict.items():
    #     print(key, values)

main()