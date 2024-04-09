import pandas as pd

__all__ = [
    'flood_probabilities',
    'return_periods',
]


def flood_probabilities(ensem: pd.DataFrame, rperiods: pd.DataFrame) -> str:
    """
    Processes the results of forecast_ensembles and return_periods and shows the probabilities of exceeding the
    return period flow on each day.

    Args:
        ensem: the csv response from forecast_ensembles
        rperiods: the csv response from return_periods

    Return:
         string containing html to build a table with a row of dates and for exceeding each return period threshold
    """
    ens = ensem.drop(columns=['ensemble_52']).dropna()
    ens = ens.groupby(ens.index.date).max()
    ens.index = pd.to_datetime(ens.index).strftime('%Y-%m-%d')
    # for each return period, get the percentage of columns with a value greater than the return period on each day
    percent_series = {rp: (ens > rperiods[rp].values[0]).mean(axis=1).values.tolist() for rp in rperiods}
    percent_series = pd.DataFrame(percent_series, index=ens.index)
    percent_series.index.name = 'Date'
    percent_series.columns = [f'{c} Year' for c in percent_series.columns]
    percent_series = percent_series * 100
    percent_series = percent_series.round(1)
    percent_series = percent_series.reset_index()

    colors = {
        '2 Year': 'rgba(254, 240, 1, {0})',
        '5 Year': 'rgba(253, 154, 1, {0})',
        '10 Year': 'rgba(255, 56, 5, {0})',
        '20 Year': 'rgba(128, 0, 246, {0})',
        '25 Year': 'rgba(255, 0, 0, {0})',
        '50 Year': 'rgba(128, 0, 106, {0})',
        '100 Year': 'rgba(128, 0, 246, {0})',
    }

    headers = "".join([f'<th>{x}</th>' for x in percent_series.columns])
    rows = []
    for row_idx, row in enumerate(percent_series.values.tolist()):
        cells = []
        for col_idx, cell in enumerate(row):
            if col_idx == 0:
                cells.append(f'<td>{cell}</td>')
                continue
            column_name = percent_series.columns[col_idx]
            stylestring = f'background-color: {colors[column_name].format(round(cell * 0.005, 2))}'
            cells.append(f'<td style="{stylestring}">{cell}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    rows = "".join(rows)

    return f'<table id="probabilities_table" align="center"><tbody><tr>{headers}</tr>{rows}</tbody></table>'


def return_periods(rperiods: pd.DataFrame) -> str:
    """
    Makes an html string of a table of return periods and river id numbers

    Args:
        rperiods: the dataframe from the return periods function

    Returns:
        string of html
    """
    colors = {
        '2 Year': 'rgba(254, 240, 1, .4)',
        '5 Year': 'rgba(253, 154, 1, .4)',
        '10 Year': 'rgba(255, 56, 5, .4)',
        '20 Year': 'rgba(128, 0, 246, .4)',
        '25 Year': 'rgba(255, 0, 0, .4)',
        '50 Year': 'rgba(128, 0, 106, .4)',
        '100 Year': 'rgba(128, 0, 246, .4)',
    }
    rperiods = rperiods.astype(float).round(2).astype(str)
    rperiods.columns = [f'{c} Year' for c in rperiods.columns]
    rperiods.index = rperiods.index.astype(int).astype(str)
    rperiods = rperiods.reset_index()

    headers = "".join([f'<th>{x}</th>' for x in rperiods.columns])
    rows = []
    for row in rperiods.values.tolist():
        cells = []
        for col_idx, cell in enumerate(row):
            if col_idx == 0:
                cells.append(f'<td>{cell}</td>')
                continue
            column_name = rperiods.columns[col_idx]
            stylestring = f'background-color: {colors[column_name]}'
            cells.append(f'<td style="{stylestring}">{cell}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    rows = "".join(rows)

    return f'<table id="return_periods_table" align="center"><tbody><tr>{headers}</tr>{rows}</tbody></table>'
