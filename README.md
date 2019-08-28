[![Build Status](https://dev.azure.com/casyfill/casyfill/_apis/build/status/Casyfill.wikiwwii?branchName=master)](https://dev.azure.com/casyfill/casyfill/_build/latest?definitionId=1&branchName=master)

# Wikiwwii
scraper and processor for wikipedia WWII battles

## Installation
`pip install git+https://github.com/Casyfill/wikiwwii.git`


wikiwwii
├── README.md
├── pyproject.toml
├── tests
│ ├── __init__.py
│ └── test_wikiwwii.py
└── wikiwwii
  ├── __init__.py
  ├── collect
  │ ├── __init__.py
  │ ├── battles.py
  │ └── fronts.py
  └── parse
    ├── __init__.py
    ├── bellengerets.py
    ├── casualties.py
    ├── dates.py
    ├── geocode.py
    └── qa.py
