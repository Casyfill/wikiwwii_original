import pandas as pd

DIGIT_PATTERN = "([\d|\,|\.]+)(?:\[\d+\])?\+?\s*(?:{words})"
ONLY_DIGITS = "([\d|\,|\.]+)\Z"
KEYWORDS = {
    "killed": ["men", "dead", "killed", "casualties", "kia"],
    "wounded": ["wounded", "sick", "injured"],
    "captured": ["captured", "prisoners"],
    "tanks": ["tank", "panzer"],
    "airplane": ["airplane", "aircraft"],
    "guns": ["artillery", "gun", "self propelled guns", "field-guns", "anti-tank guns"],
    "ships": ["warships", "boats", "destroyer", "minelayer"],
    "submarines": ["submarines"],
}


def _shy_convert_numeric(v):
    if pd.isnull(v) or v in (",", "."):
        return pd.np.nan

    return int(v.replace(",", "").replace(".", ""))


def _parse_casualties(column, keywords=KEYWORDS):
    df = pd.DataFrame(index=column.index, columns=KEYWORDS.keys())

    for tp, keys in keywords.items():
        pattern = DIGIT_PATTERN.format(words="|".join(keys))
        extracted = column.str.lower().str.extractall(pattern).unstack()
        df[tp] = extracted.applymap(_shy_convert_numeric).min(1)

    df = df.fillna(0).astype(int)

    # only digits
    b = (
        column.fillna("")
        .str.extract(ONLY_DIGITS)
        .applymap(_shy_convert_numeric)
        .iloc[:, 0]
    )
    mask = b.notnull()
    df.loc[mask, "killed"] = b[mask]
    return df
