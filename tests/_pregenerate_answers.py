from pathlib import Path
from bs4 import BeautifulSoup
import json
file_dir = Path(__file__).parent / 'data' / 'pages'

def _load_dom(path):
    with path.open('r') as f:
        return BeautifulSoup(f.read(), 'html.parser')


def generate_answers():
    from wikiwwii.collect.battles import _parse_page
    paths = file_dir.glob('*.html')

    result = {p.name: _parse_page(_load_dom(p)) for p in paths}

    with (file_dir / 'answers.json').open('w') as f:
        json.dump(result, f)

if __name__ == '__main__':
    generate_answers()