import pytest
import pandas as pd

@pytest.fixture()
def case():
    return {
        'col': pd.Series([
            '10,000',
            '37,000 dead, 7,000 POW (Soviet est)',
            '29 aircraft destroyed (ground)',
            '20 men, 4 tanks, 20 guns',
            ''
        ]),

        'answer': pd.DataFrame({
            'killed':[10_000, 37_000, 0, 20, 0],
            'airplane': [0, 0, 29, 0, 0],
            'guns': [0, 0, 0, 20, 0],
            'tanks': [0, 0, 0, 4, 0]
        })
    }

def test_parse_casualties(case):
    from wikiwwii.parse.casualties import _parse_casualties

    parsed = _parse_casualties(case['col'])

    for col in case['answer'].columns:
        mask = parsed[col] == case['answer'][col]
        comp = pd.DataFrame({'col': case['col'],
                             'result': parsed[col]})

        assert mask.all(), (col, comp[~mask].to_string())
