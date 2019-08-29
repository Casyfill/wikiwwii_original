import pandas as pd

idx = pd.IndexSlice

assumptions = {
    "killed": [0, 2_000_000],
    "wounded": [0, 1_000_000],
    "tanks": [0, 5_000],
    "airplane": [0, 3_000],
    "guns": [0, 30_000],
    ("start", "end"): [pd.to_datetime(el) for el in ("1939-01-01", "1945-12-31")],
}


#%%
def _check_assumptions(data, assumptions):
    for k, (min_, max_) in assumptions.items():
        df = data.loc[:, idx[:, k]]
        for i in range(df.shape[1]):
            assert df.iloc[:, i].between(min_, max_).all(), (
                df.iloc[:, i].name,
                df.iloc[:, i].describe(),
            )
