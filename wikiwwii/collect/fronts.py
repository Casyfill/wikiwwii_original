
import requests as rq
from bs4 import BeautifulSoup
import json

BASE_URL = 'https://en.wikipedia.org/wiki/List_of_World_War_II_battles'


def _get_dom(url):
    response = rq.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'html.parser')


def collect_fronts(base_url=BASE_URL):
    '''collect links and names on all subjects in the table, 
    hierarchically
    '''
    soup = _get_dom(base_url)
    content = soup.find('div', id='mw-content-text').find('div', 'mw-parser-output')
    fronts = [el for el in content.find_all('h2', recursive=False)[:-1]]

    theaters = {}
    for front in fronts:
        theaters[front.text[:-6]] = dictify(front.find_next_siblings("div", "div-col columns column-width")[0].ul)
    
    return theaters


def dictify(ul, level=0):
    '''recursive table parsing'''
    result = dict()
    
    for li in ul.find_all("li", recursive=False):
        text = li.stripped_strings
        key = next(text)
        
        try:
            time = next(text).replace(':', '').strip()
        except StopIteration:
            time = None

        ul, link = li.find("ul"), li.find('a')
        if link:
            link = 'https://en.wikipedia.org' + link.get('href')
            
        nextlevel = level + 1

        r ={'url': link,
            'time':time,
            'level': nextlevel} 
        
        if ul:
            r['children'] = dictify(ul, level=nextlevel+1)

        result[key] = r
    return result


