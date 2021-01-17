from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from collections import defaultdict
import regex as re
import datetime
import pickle
import json
import pdb




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
    r = requests.get(url);
    soup = BeautifulSoup(r.text, 'html.parser');
    soup.prettify();
    return soup

def gather_data_from_box(soup):
    infobox = soup.find_all('table',class_='infobox vevent')
    info_dict = defaultdict()
    alternative_box = soup.find_all('t')
    
    for table in infobox:
        rows = table.find_all('tr')
        for row in rows:
            attributes = row.find_all('th', recursive = True)
            information = row.find_all('td')
                
            # pdb.set_trace()
            for attribute, info in zip(attributes,information):
                key = attribute.get_text(" ", strip=True)
                codetags = info.find_all('b')
                for codetag in codetags:
                    codetag.extract()
                
                value = list(filter(lambda x: x!='', info.text.split('\n')))
                info_dict[key] = value
    return info_dict


def cleanup_values(db):
    for key, value in db.items():
        db[key] = remove_brackets(db[key])
        db[key] = fix_dates(db[key])
        db[key] = convert_time(db[key])
    return db

def remove_brackets(info_dict):
    for key,  value in info_dict.items():
        info_dict[key] = list(map(lambda x: re.sub("[\[].*?[\]]", "", x), value))
    return info_dict


def convert_time(info_dict):

    if 'Running time' in info_dict.keys():
        info_dict['Running time'] = list(map(lambda x : int(re.search(r'\d+', x).group()), info_dict['Running time']))
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
    db = defaultdict(lambda: defaultdict(str))
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
    # filehandler = open('movie_db.pkl', 'wb') 
    # pickle.dump(movie_db, filehandler)
    # filehandler.close()
    # print("Created database and pickled into movie_db")
    return movie_db

def load_db():
    infile = open("movie_db",'rb')
    db = pickle.load(infile)
    infile.close()
    return db

def write_to_json(db, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

def load_from_json():
    with open('movie_db.json') as json_file:
        db = json.load(json_file)
    return db 

def main():
    list_url = 'https://en.wikipedia.org/wiki/List_of_Walt_Disney_Pictures_films'
    base_url = 'https://en.wikipedia.org'
    db = create_db(base_url, list_url)
    # write_to_json(db, "movie_db_clean.json")
    # single_soup = request_from_webiste('https://en.wikipedia.org/wiki/Bambi')
    # box = gather_data_from_box(single_soup)
    # write_to_json(box, 'single_box.json')
    
    
    # db = load_from_json()
    db_clean = cleanup_values(db)
    db_clean = write_to_json(db, "movie_db_clean.json")
    # print(type(db))
    






    # url = 'https://en.wikipedia.org/wiki/Toy_Story_3'
    # soup = request_from_webiste(url)
    # info_dict_raw = gather_data(soup)
    # info_dict = cleanup_values(info_dict_raw)
    # info_dict = fix_dates(info_dict)
    
    
    
    # for key, values in info_dict.items():
    #     print(key, values)

main()