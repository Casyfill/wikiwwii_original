import pytest
from pathlib import Path
data_folder = Path(__file__).parent / 'data' / 'pages'


def test_parse_page():
    from wikiwwii.collect.battles import _parse_page
    from bs4 import BeautifulSoup

    path = data_folder / 'Action at Mechili, 24 January 1941 - Wikipedia.html'
    with path.open('r') as f:
        dom = BeautifulSoup(f.read(), 'html.parser')
    
    answer = {'Date': '24 January 1941',
              'Location': 'Mechili, Libya32°11′00″N 22°16′00″E\ufeff / \ufeff32.18333°N 22.26667°E\ufeff / 32.18333; 22.26667Coordinates: 32°11′00″N 22°16′00″E\ufeff / \ufeff32.18333°N 22.26667°E\ufeff / 32.18333; 22.26667',
              'Result': 'British victory',
              'Belligerents': {'allies': 'United Kingdom', 'axis': 'Italy'},
              'Commanders and leaders': {'allies': "Richard O'Connor   Michael O'Moore Creagh",
              'axis': 'Rodolfo Graziani   Giuseppe Tellera  Valentino Babini'},
              'Strength': {'allies': '145 tanks',
              'axis': '5,000 men 129 tanks 25 tankettes 6 armoured cars 84 guns'},
              'Casualties and losses': {'allies': '4 killed 3 captured 7 tanks destroyed',
              'axis': '9 tanks destroyed'}
    }

    result = _parse_page(dom)
    assert result == answer
    