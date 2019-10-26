try:
    import pandas
    import requests
    import json
    import datetime
    import jinja2
    import os
    import multiprocessing
    from plotly.offline import plot as offplot
    from plotly.graph_objs import Scatter, Scattergl, Layout, Figure
    import plotly.graph_objs as go
    from io import StringIO
except ImportError as error:
    raise error

AZURE_ENDPOINT = 'http://global-streamflow-prediction.eastus.azurecontainer.io/api/'


# FUNCTIONS THAT CALL THE GLOBAL STREAMFLOW PREDICTION API
def forecast_stats(reach_id, apikey, return_format='csv'):
    params = {
        'reach_id': reach_id,
        'return_format': return_format
    }
    headers = {'Ocp-Apim-Subscription-Key': apikey}

    data = requests.get(AZURE_ENDPOINT + 'ForecastStats', headers=headers, params=params).text

    if return_format == 'csv':
        return pandas.read_csv(StringIO(data))
    elif return_format == 'json':
        return json.loads(data)
    elif return_format == 'waterml':
        return data


def forecast_ensembles(reach_id, apikey, return_format='csv'):
    params = {
        'reach_id': reach_id,
        'return_format': return_format
    }
    headers = {'Ocp-Apim-Subscription-Key': apikey}

    data = requests.get(AZURE_ENDPOINT + 'ForecastEnsembles', headers=headers, params=params).text

    if return_format == 'csv':
        tmp = pandas.read_csv(StringIO(data), index_col='datetime')
        tmp.index = pandas.to_datetime(tmp.index)
        return tmp
    elif return_format == 'json':
        return json.loads(data)
    elif return_format == 'waterml':
        return data


def historic_simulation(reach_id, apikey, return_format='csv'):
    params = {
        'reach_id': reach_id,
        'return_format': return_format
    }
    headers = {'Ocp-Apim-Subscription-Key': apikey}

    data = requests.get(AZURE_ENDPOINT + 'HistoricSimulation', headers=headers, params=params).text

    if return_format == 'csv':
        return pandas.read_csv(StringIO(data))
    elif return_format == 'json':
        return json.loads(data)
    elif return_format == 'waterml':
        return data


def seasonal_average(reach_id, apikey, return_format='csv'):
    params = {
        'reach_id': reach_id,
        'return_format': return_format
    }
    headers = {'Ocp-Apim-Subscription-Key': apikey}

    data = requests.get(AZURE_ENDPOINT + 'SeasonalAverage', headers=headers, params=params).text

    if return_format == 'csv':
        return pandas.read_csv(StringIO(data))
    elif return_format == 'json':
        return json.loads(data)
    elif return_format == 'waterml':
        return data


def return_periods(reach_id, apikey, return_format='csv'):
    params = {
        'reach_id': reach_id,
        'return_format': return_format
    }
    headers = {'Ocp-Apim-Subscription-Key': apikey}

    data = requests.get(AZURE_ENDPOINT + 'ReturnPeriods', headers=headers, params=params).text

    if return_format == 'csv':
        return pandas.read_csv(StringIO(data), index_col='return period')
    elif return_format == 'json':
        return json.loads(data)
    elif return_format == 'waterml':
        return data


def available_regions(apikey):
    headers = {'Ocp-Apim-Subscription-Key': apikey}
    return json.loads(requests.get(AZURE_ENDPOINT + 'AvailableRegions', headers=headers).text)


def available_dates(apikey):
    headers = {'Ocp-Apim-Subscription-Key': apikey}
    return json.loads(requests.get(AZURE_ENDPOINT + 'ReturnPeriods', headers=headers).text)


# FUNCTIONS THAT PROCESS THE RESULTS OF THE API INTO A PLOTLY PLOT OR DICTIONARY
def forecast_plot(stats, rperiods, reach_id, outformat='json'):
    if not isinstance(stats, pandas.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')
    if outformat not in ['json', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json or html')

    r2 = rperiods.iloc[3][0]
    r10 = rperiods.iloc[2][0]
    r20 = rperiods.iloc[1][0]
    dates = stats['datetime'].tolist()
    startdate = dates[0]
    enddate = dates[-1]

    hires = stats[['datetime', 'high_res (m3/s)']].dropna(axis=0)
    ens = stats[['datetime', 'mean (m3/s)']].dropna(axis=0)
    plot_data = {
        'reach_id': reach_id,
        'x_ensembles': ens['datetime'].tolist(),
        'x_hires': hires['datetime'].tolist(),
        'ymax': max(stats['max (m3/s)']),
        'min': list(stats['min (m3/s)'].dropna(axis=0)),
        'mean': list(stats['mean (m3/s)'].dropna(axis=0)),
        'max': list(stats['max (m3/s)'].dropna(axis=0)),
        'stdlow': list(stats['std_dev_range_lower (m3/s)'].dropna(axis=0)),
        'stdup': list(stats['std_dev_range_upper (m3/s)'].dropna(axis=0)),
        'hires': list(stats['high_res (m3/s)'].dropna(axis=0)),
    }

    if outformat == 'json':
        return plot_data

    meanplot = Scatter(
        name='Mean',
        x=plot_data['x_ensembles'],
        y=plot_data['mean'],
        line=dict(color='blue'),
    )
    maxplot = Scatter(
        name='Max',
        x=plot_data['x_ensembles'],
        y=plot_data['max'],
        fill='tonexty',
        mode='lines',
        line=dict(color='rgb(152, 251, 152)', width=0)
    )
    minplot = Scatter(
        name='Min',
        x=plot_data['x_ensembles'],
        y=plot_data['min'],
        fill=None,
        mode='lines',
        line=dict(color='rgb(152, 251, 152)')
    )
    stdlowplot = Scatter(
        name='Std. Dev. Lower',
        x=plot_data['x_ensembles'],
        y=plot_data['stdlow'],
        fill='tonexty',
        mode='lines',
        line=dict(color='rgb(152, 251, 152)', width=0)
    )
    stdupplot = Scatter(
        name='Std. Dev. Upper',
        x=plot_data['x_ensembles'],
        y=plot_data['stdup'],
        fill='tonexty',
        mode='lines',
        line={'width': 0, 'color': 'rgb(34, 139, 34)'}
    )
    hires = Scatter(
        name='Higher Resolution',
        x=plot_data['x_hires'],
        y=plot_data['hires'],
        line={'color': 'black'}
    )
    layout = Layout(
        title='Forecasted Streamflow<br>Stream ID: ' + str(reach_id),
        xaxis={'title': 'Date'},
        yaxis={
            'title': 'Streamflow (m<sup>3</sup>/s)',
            'range': [0, 1.2 * plot_data['ymax']]
        },
        shapes=[
            go.layout.Shape(
                type='rect',
                x0=startdate,
                x1=enddate,
                y0=r2,
                y1=r10,
                line={'width': 0},
                opacity=.4,
                fillcolor='yellow'
            ),
            go.layout.Shape(
                type='rect',
                x0=startdate,
                x1=enddate,
                y0=r10,
                y1=r20,
                line={'width': 0},
                opacity=.4,
                fillcolor='red'
            ),
            go.layout.Shape(
                type='rect',
                x0=startdate,
                x1=enddate,
                y0=r20,
                y1=1.2 * plot_data['ymax'],
                line={'width': 0},
                opacity=.4,
                fillcolor='purple'
            ),
        ]
    )
    if outformat == 'plotly':
        return Figure([minplot, meanplot, maxplot, stdlowplot, stdupplot, hires], layout=layout)
    if outformat == 'plotly_html':
        return offplot(
            Figure([minplot, meanplot, maxplot, stdlowplot, stdupplot, hires], layout=layout),
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )


def historical_plot(hist, rperiods, outformat='plotly'):
    if not isinstance(hist, pandas.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')
    if outformat not in ['json', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json or plotly or plotly_html')

    r2 = rperiods.iloc[3][0]
    r10 = rperiods.iloc[2][0]
    r20 = rperiods.iloc[1][0]
    dates = hist['datetime'].tolist()
    startdate = dates[0]
    enddate = dates[-1]

    if outformat == 'json':
        # todo make the json output
        return

    layout = Layout(
        title='Historic Streamflow Simulation',
        xaxis={
            'title': 'Date',
            'hoverformat': '%b %d %Y',
            'tickformat': '%Y'
        },
        yaxis={
            'title': 'Streamflow (m<sup>3</sup>/s)',
            'range': [0, 1.2 * max(hist['streamflow (m3/s)'])]
        },
        shapes=[
            go.layout.Shape(
                type='rect',
                x0=startdate,
                x1=enddate,
                y0=r2,
                y1=r10,
                line={'width': 0},
                opacity=.4,
                fillcolor='yellow'
            ),
            go.layout.Shape(
                type='rect',
                x0=startdate,
                x1=enddate,
                y0=r10,
                y1=r20,
                line={'width': 0},
                opacity=.4,
                fillcolor='red'
            ),
            go.layout.Shape(
                type='rect',
                x0=startdate,
                x1=enddate,
                y0=r20,
                y1=1.2 * 1.2 * max(hist['streamflow (m3/s)']),
                line={'width': 0},
                opacity=.4,
                fillcolor='purple'
            ),
        ]
    )
    figure = Figure([Scattergl(x=dates, y=hist['streamflow (m3/s)'].tolist())], layout=layout)
    if outformat == 'plotly':
        return figure
    if outformat == 'plotly_html':
        return offplot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    return


def daily_avg_plot(daily, outformat='plotly'):
    if not isinstance(daily, pandas.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')
    if outformat not in ['json', 'plotly', 'plotly_html']:
        raise ValueError('invalid outformat specified. pick json or plotly or plotly_html')

    if outformat == 'json':
        # todo make the json output
        return

    daily['day'] = pandas.to_datetime(daily['day'] + 1, format='%j')
    layout = Layout(
        title='Daily Average Streamflow (Historic Simulation)',
        xaxis={
            'title': 'Date',
            'hoverformat': '%b %d (%j)',
            'tickformat': '%b'
        },
        yaxis={
            'title': 'Streamflow (m<sup>3</sup>/s)',
            'range': [0, 1.2 * max(daily['streamflow_avg (m3/s)'])]
        },
    )
    figure = Figure([Scatter(x=daily['day'].tolist(), y=daily['streamflow_avg (m3/s)'].tolist())], layout=layout)
    if outformat == 'plotly':
        return figure
    if outformat == 'plotly_html':
        return offplot(
            figure,
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )
    return


def probabilities_table(stats, ensembles, rperiods):
    dates = stats['datetime'].tolist()
    startdate = dates[0]
    enddate = dates[-1]
    start_datetime = datetime.datetime.strptime(startdate, "%Y-%m-%d %H:00:00")
    span = datetime.datetime.strptime(enddate, "%Y-%m-%d %H:00:00") - start_datetime
    uniqueday = [start_datetime + datetime.timedelta(days=i) for i in range(span.days + 2)]
    # get the return periods for the stream reach
    rp2 = rperiods.iloc[3][0]
    rp10 = rperiods.iloc[2][0]
    rp20 = rperiods.iloc[1][0]

    # fill the lists of things used as context in rendering the template
    days = []
    r2 = []
    r10 = []
    r20 = []
    for i in range(len(uniqueday) - 1):  # (-1) omit the extra day used for reference only
        tmp = ensembles.loc[uniqueday[i]:uniqueday[i + 1]]
        days.append(uniqueday[i].strftime('%b %d'))
        num2 = 0
        num10 = 0
        num20 = 0
        for column in tmp:
            if any(i > rp20 for i in tmp[column].to_numpy()):
                num2 += 1
                num10 += 1
                num20 += 1
            elif any(i > rp10 for i in tmp[column].to_numpy()):
                num10 += 1
                num2 += 1
            elif any(i > rp2 for i in tmp[column].to_numpy()):
                num2 += 1
        r2.append(round(num2 * 100 / 52))
        r10.append(round(num10 * 100 / 52))
        r20.append(round(num20 * 100 / 52))

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates', 'probabilities_table.html'))
    with open(path) as template:
        return jinja2.Template(template.read()).render(days=days, r2=r2, r10=r10, r20=r20)


# CUSTOM FUNCTIONS FOR IMPLEMENTATION IN A HYDROVIEWER
def hydroviewer_forecast(reach_id, apikey):
    # make all the API calls asynchronously with a pool
    with multiprocessing.Pool(3) as pl:
        stats = pl.apply_async(forecast_stats, (reach_id, apikey))
        ensembles = pl.apply_async(forecast_ensembles, (reach_id, apikey))
        rperiods = pl.apply_async(return_periods, (reach_id, apikey))
        pl.close()
        pl.join()
        stats = stats.get()
        ensembles = ensembles.get()
        rperiods = rperiods.get()
    fp = forecast_plot(stats, rperiods, reach_id, outformat='plotly_html')
    pt = probabilities_table(stats, ensembles, rperiods)
    return fp + pt
