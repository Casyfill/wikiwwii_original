import pytest
import json
from pathlib import Path
data_folder = Path(__file__).parent / 'data' / 'pages'

with (data_folder / 'answers.json').open('r') as f:
    answers = json.load(f)

def _load_dom(path):
    from bs4 import BeautifulSoup

    with path.open('r') as f:
        return BeautifulSoup(f.read(), 'html.parser')


@pytest.mark.parametrize("name, answer", answers.items())
def test_parse_page(name, answer):
    from wikiwwii.collect.battles import _parse_page

    dom = _load_dom(data_folder / name)
    result = _parse_page(dom)

    assert result == answer
    