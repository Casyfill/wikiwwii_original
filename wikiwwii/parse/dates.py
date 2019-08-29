import pandas as pd

MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    " August",
    "September",
    "October",
    "November",
    "December",
)
MONTH_PATTERN = r"(" + "|".join(MONTHS) + ")"
YEAR_PATTERN = r"(19\d\d)"


def extract_dates(dateCol):
    year_extracted = dateCol.str.extractall(YEAR_PATTERN).unstack()

    # where only one year, fillna
    year_extracted.iloc[:, 1] = year_extracted.iloc[:, 1].fillna(
        year_extracted.iloc[:, 0]
    )

    month_extracted = dateCol.str.extractall(MONTH_PATTERN).unstack()

    for i in range(2, month_extracted.shape[1] + 1):
        month_extracted.iloc[:, -1].fillna(month_extracted.iloc[:, -i], inplace=True)

    month_extracted = month_extracted.iloc[:, [0, -1]]

    cols = "start", "end"
    year_extracted.columns = month_extracted.columns = cols
    I = dateCol.index

    return pd.DataFrame(
        {
            col: pd.to_datetime(
                month_extracted.loc[I, col] + " " + year_extracted.loc[I, col]
            )
            for col in cols
        }
    )
