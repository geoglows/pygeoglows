import json
import os

import jinja2
import pandas as pd

__all__ = [
    'probabilities_table',
    'return_periods_table',
]


def probabilities_table(ensem: pd.DataFrame, rperiods: pd.DataFrame) -> str:
    """
    Processes the results of forecast_ensembles and return_periods and shows the probabilities of exceeding the
    return period flow on each day.

    Args:
        ensem: the csv response from forecast_ensembles
        rperiods: the csv response from return_periods

    Return:
         string containing html to build a table with a row of dates and for exceeding each return period threshold
    """
    ens = ensem.drop(columns=['ensemble_52_cms']).dropna()
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

    # style column background based the the column name and the opacity of the color based on the value
    colors = {
        'Date': 'rgba(0, 0, 0, 0)',
        '2 Year': 'rgba(0, 0, 255, {0})',
        '5 Year': 'rgba(0, 255, 0, {0})',
        '10 Year': 'rgba(255, 255, 0, {0})',
        '25 Year': 'rgba(255, 165, 0, {0})',
        '50 Year': 'rgba(255, 0, 0, {0})',
        '100 Year': 'rgba(128, 0, 128, {0})',
    }

    def _apply_column_wise_colors(x):
        return [f'background-color: {colors[x.name].format(round(val * 0.0065, 2))}' for col, val in x.items()]

    # fill the dataframe with random values between 0 and 100 for testing purposes
    import numpy as np
    percent_series = pd.DataFrame(np.random.randint(0, 100, size=percent_series.shape), columns=percent_series.columns)

    percent_series = percent_series.style.apply(_apply_column_wise_colors, axis=0, subset=percent_series.columns[1:])

    # rows = ''.join([f"<tr>{''.join([f'<td>{x}</td>' for x in row])}</tr>" for row in percent_series.values.tolist()])
    # headers = "".join([f'<th>{x}</th>' for x in percent_series.columns])
    # rows = []
    # for row_idx, row in enumerate(percent_series.values.tolist()):
    #     cells = []
    #     for col_idx, cell in enumerate(row):
    #         cells.append(f'<td class="cell cell-{col_idx} row row-{row_idx}">{cell}</td>')
    #     rows.append(f'<tr>{"".join(cells)}</tr>')
    # rows = "".join(rows)
    #
    # return f"""
    # <div class="forecast-probabilities-table">Percent of Ensembles that Exceed Return Periods</div>
    # <table id="probabilities_table" align="center"><tbody>{headers}{rows}</tbody></table>
    # """
    # return percent_series.to_html(index=False)
    string = percent_series.to_html(index=False)
    # replace the id tags with a style tag containing the styles applied to that id
    # use a regular expression to find the id="*" and class="*"> and replace with style="*"
    import re
    all_id_tags = re.findall(r'id=".*?"', string)
    for idname in all_id_tags:
        # find the contents of the multiline string that goes #idname { * } and replace the id tag with style="*"
        css_string = re.search(rf'{idname} {{.*?}}', _apply_column_wise_colors.__doc__, re.DOTALL).group()
        string = string.replace(idname, f'style="{idname[4:-1]}"')


def return_periods_table(rperiods: pd.DataFrame) -> str:
    """
    Processes the dataframe response from the return_periods function and uses jinja2 to render an html string for a
    table showing each of the return periods

    Args:
        rperiods: the dataframe from the return periods function

    Returns:
        string of html
    """

    # find the correct template to render
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates', 'return_periods_table.html'))
    # work on a copy of the dataframe so you dont ruin the original
    tmp = rperiods
    reach_id = str(tmp.index[0])
    js = json.loads(tmp.to_json())
    rp = {}
    for i in js:
        if i.startswith('return_period'):
            year = i.split('_')[-1]
            rp[f'{year} Year'] = js[i][reach_id]
        elif i == 'max_flow':
            rp['Max Simulated Flow'] = js[i][reach_id]

    rp = {key: round(value, 2) for key, value in sorted(rp.items(), key=lambda item: item[1])}

    with open(path) as template:
        return jinja2.Template(template.read()).render(reach_id=reach_id, rp=rp, colors=_plot_colors())
