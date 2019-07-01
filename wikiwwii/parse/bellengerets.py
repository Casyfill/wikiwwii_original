WORDS = ["Germany", "Italy", "Estonian conscripts"]  # known ones on the wrong side


def _swap_ensure_sides(
    raw_df,
    col="Bellegerents.allies",
    swap_cols=["Belligerents.{}", "Casualties and losses.{}"],
    words=WORDS,
):
    """NOTE: overly specific - need to abstract from column names"""
    df = raw_df.copy()
    swap_axis = [el.format("axis") for el in swap_cols]
    swap_allies = [el.format("allies") for el in swap_cols]

    for word in words:
        mask = df[col].fillna("").str.contains(word)

        if mask.any():
            axis_party = df.loc[mask, swap_allies].copy()
            df.loc[mask, swap_allies] = df.loc[mask, swap_axis].values
            df.loc[mask, swap_axis] = axis_party.values

    return df
