import pandas as pd
import json
from .geocode import nominatim_geocode

def extract_latlon(locColumn):
    '''extracts latlon from the location'''
    latlon_pattern = r'/ ([\d|\.]+); ([\d|\.]+)'
    latlon = locColumn.str.extract(latlon_pattern)
    for col in  range(2):
        latlon.iloc[:, col] = latlon.iloc[:, col].astype(float)

    return latlon

LOC_REPLACEMENTS = {
            'Ukrainian SSR, Soviet Union': 'Ukraine',
            'Russian SFSR, Soviet Union': 'Russia',
            'Russian SFSR': 'Russia',
            'Belorussian SSR': 'Belorus',
            'Soviet Union': '',
            'USSR': '',
            ', Poland (now Ukraine)': 'Ukraine',
            'east prussia (now kaliningrad oblast)': 'Kaliningrad Oblast, Russia',
            ', czechoslovakia': ', czech republic',
            'königsberg, germany (now: kaliningrad, russia)': 'Kaliningrad Oblast, Russia',
            'lwów, lwów voivodeship, poland': 'Lvov, Ukraine',
            'leningrad region, ; narva, estonia': 'Narva, Estonia',
            'Kingdom of Hungary': 'Hungary',
            'odessa region, ukraine': 'Odessa, Ukraine'
        }


def geocode_location(locColumn, replacements=LOC_REPLACEMENTS, errata=None):
    '''attempts to geocode locations.
    don't forget to use mask not to waste 
    geocoding on those located already'''


    location = locColumn.str.lower().str.replace('near ', '')

    if replacements is not None:
        for k, v in replacements.items():
            location = location.str.replace(k.lower(), v.lower(), regex=False)
    if errata is not None:
        for k, v in errata.items():
            location = location.replace(k.lower(), v.lower(), regex=False)

    def _vectorized_geocode(x):
        result = nominatim_geocode(x)
        if len(result) == 0:
            return dict()
        return {k:result[0][k] for k in ('lat', 'lon', 'importance', 'display_name')}


    return location.str.replace('\n', ' ').progress_apply(vectorized_geocode)


#%%
response.iloc[0]


#%%
battles.loc[geo_mask, 'Location'].iloc[0]


#%%
geo_df = pd.DataFrame(response.tolist(), index = response.index)
geo_df.rename(columns={'lat': 'Lattitude', 'lon': ' Longitude'}, inplace=True)


#%%
rmask = geo_df['importance'].isnull()  # still no location


#%%
f'{rmask.sum() / len(battles):.1%}'


#%%
location[geo_mask].loc[rmask]

#%% [markdown]
# ## Time

#%%
# pd.to_datetime('September 1939')


#%%
battles.loc[94, 'Date']


#%%
d = ('January', 'February', 'March', 'April', 'May', 
     'June', "July",' August', 'September', 'October', 'November', 'December')

month_pattern = r'(' + "|".join(d) + ')'


#%%
year_pattern = r'(19\d\d)'


#%%
year_extracted = battles['Date'].str.extractall(year_pattern).unstack()


#%%
# len(d.iloc[:, -1].notnull())
year_extracted[year_extracted.iloc[:, -1].notnull()]


#%%
# d[d.iloc[:, -1].notnull()]


#%%
battles.loc[94, 'Date']


#%%
year_extracted = year_extracted.iloc[:, :2]


#%%
year_extracted.head(10)


#%%
year_extracted.iloc[:, 1] = year_extracted.iloc[:, 1].fillna(year_extracted.iloc[:, 0])


#%%
month_extracted = battles['Date'].str.extractall(month_pattern).unstack()


#%%
for i in range(2, month_extracted.shape[1]+1):
    month_extracted.iloc[:, -1].fillna(month_extracted.iloc[:, -i], inplace=True)


#%%
month_extracted = month_extracted.iloc[:, [0, -1]]


#%%
year_extracted.columns = month_extracted.columns = ['start', 'end']
I = battles.index
cols = 'start', 'end'

for col in cols:
    battles[col] = pd.to_datetime(month_extracted.loc[I, col] + ' ' + year_extracted.loc[I, col])

#%% [markdown]
# # Sides Swap

#%%
words = ['Germany', 'Italy', 'Estonian conscripts']


#%%
for word in words:
    mask = battles['Belligerents.allies'].fillna('').str.contains(word)
    axis_party = battles.loc[mask, ['Belligerents.allies', 'Casualties and losses.allies']].copy()
    battles.loc[mask, ['Belligerents.allies', 'Casualties and losses.allies']] = battles.loc[mask, ['Belligerents.axis', 'Casualties and losses.axis']].values
    battles.loc[mask, ['Belligerents.axis', 'Casualties and losses.axis']] = axis_party.values

#%% [markdown]
# ## Casualties

#%%
battles['Casualties and losses.allies'].iloc[0]


#%%
digit_pattern = '([\d|\,|\.]+)(?:\[\d+\])?\+?\s*(?:{words})'

keywords = { 'killed': ['men', 'dead', 'killed', 'casualties', 'kia'], 
             'wounded': ['wounded', 'sick', 'injured'], 
             'captured': ['captured', 'prisoners'],
             'tanks': ['tank', 'panzer'],
             'airplane': ['airplane', 'aircraft'],
             'guns': ['artillery', 'gun', 'self propelled guns', 'field-guns', 'anti-tank guns'],
             'ships': ['warships', 'boats', 'destroyer', 'minelayer'],
             'submarines': ['submarines']
}

only_digits = '([\d|\,|\.]+)\Z'


#%%
# column[column.fillna('').str.match(only_digits)].str.extract(only_digits)


#%%
def _shy_convert_numeric(v):
    if pd.isnull(v) or v in (',', '.'):
        return pd.np.nan
    
    return int(v.replace(',', '').replace('.', ''))
    


#%%
results = {
'allies' : pd.DataFrame(index=battles.index, columns=keywords.keys()),  # empty dataframes with the same index
'axis' : pd.DataFrame(index=battles.index, columns=keywords.keys())
}

for name, edf in results.items():
    column = battles[f'Casualties and losses.{name}']
    for tp, keys in keywords.items():
        pattern = digit_pattern.format(words="|".join(keys))
        print(pattern)
        extracted = column.str.lower().str.extractall(pattern).unstack()
        values = extracted.applymap(_shy_convert_numeric)
#         if tp == 'killed':
#             mask values.iloc[:, 0].notnull()
        edf[tp] = values.min(1)
    results[name] = edf.fillna(0).astype(int)
    

    b = column.fillna('').str.extract(only_digits).applymap(_shy_convert_numeric).iloc[:, 0]
    mask = b.notnull()
    results[name].loc[mask, 'killed'] = b[mask]


#%%
pattern = '([\d|\,]+)(?:\[\d+\])?\+?\s*(?:men|dead|killed|casualties|kia)'
battles[f'Casualties and losses.axis'].str.extractall(pattern).unstack().head(5)


#%%
battles['Casualties and losses.axis'][battles.name == 'Battle of Stalingrad'].iloc[0]


#%%
# battles[battles.name == 'Battle of Stalingrad']


#%%
results['axis'][battles.name == 'Battle of Stalingrad']


#%%
battles.loc[[27], 'Casualties and losses.axis'].iloc[0] #.str.extractall('([\d|\,]+)\s[tank]')


#%%
results['axis'].loc[27]


#%%
results['axis'][battles.name == 'Battle for Velikiye Luki (1943)']


#%%
battles.loc[battles.name=='Battle for Velikiye Luki (1943)', 'Casualties and losses.axis'].iloc[0]


#%%


#%% [markdown]
# # Combine

#%%
results['old_metrics'] = battles
new_dataset = pd.concat(results, axis=1)

#%% [markdown]
# # Quality Assurance

#%%
idx = pd.IndexSlice


#%%
assumptions = {
    'killed': [0, 2_000_000],
    'wounded': [0, 1_000_000],
    'tanks': [0, 5_000],
    'airplane': [0, 3_000],
    'guns': [0, 30_000],
    ('start', 'end'): [pd.to_datetime(el) for el in ('1939-01-01', '1945-12-31')]
}


#%%
def _check_assumptions(data, assumptions):
    for k, (min_, max_) in assumptions.items():
        df = data.loc[:, idx[:, k]]
        for i in range(df.shape[1]):
            assert df.iloc[:, i].between(min_, max_).all(), (df.iloc[:, i].name, df.iloc[:, i].describe())


#%%
d = new_dataset.loc[new_dataset.loc[:, idx['allies', 'tanks']] > 1_000 , idx['old_metrics', ['name', 'url']]] 
d


#%%
d.iloc[0, 1]


#%%
_check_assumptions(new_dataset, assumptions)


#%%
new_dataset.loc[~new_dataset.loc[:, idx['old_metrics', 'start']].between(*[pd.to_datetime(el) for el in ('1939-01-01', '1945-12-31')]), idx['old_metrics', ['start']]]


#%%
new_dataset.loc[new_dataset.loc[:, idx['old_metrics', 'start']].isnull(), idx['old_metrics', ['name','url']]]


#%%
new_dataset.loc[135, idx['old_metrics', 'start']] = pd.to_datetime('1944-08-09')
new_dataset.loc[135, idx['old_metrics', 'end']] = pd.to_datetime('1944-08-16') # August 9–16, 1944


#%%
_check_assumptions(new_dataset, assumptions)

#%% [markdown]
# # Store

#%%
new_dataset.to_csv('./data/EF_battles.csv', index=None)


#%%



