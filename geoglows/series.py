try:
    import pandas
    import datetime
    import jinja2
    import os
    import multiprocessing
    from plotly.offline import plot as offplot
    from plotly.graph_objs import Scatter, Scattergl, Layout, Figure
    import plotly.graph_objs as go
    from streamflow import forecast_stats, forecast_ensembles, historic_simulation, seasonal_average, return_periods
except ImportError as error:
    raise error


def forecasted(stats, rperiods, reach_id, outformat='html'):
    if not isinstance(stats, pandas.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')

    r2 = rperiods.iloc[3][0]
    r10 = rperiods.iloc[2][0]
    r20 = rperiods.iloc[1][0]
    dates = stats['datetime'].tolist()
    startdate = dates[0]
    enddate = dates[-1]

    if outformat in ['json', 'JSON', 'dict', 'dictionary']:
        hires = stats[['datetime', 'high_res (m3/s)']].dropna(axis=0)
        tmp = stats[['datetime', 'mean (m3/s)']].dropna(axis=0)
        return {
            'reach_id': reach_id,
            'x_ensembles': tmp['datetime'].tolist(),
            'x_hires': hires['datetime'].tolist(),
            'ymax': max(stats['max (m3/s)']),
            'min': list(stats['min (m3/s)'].dropna(axis=0)),
            'mean': list(stats['mean (m3/s)'].dropna(axis=0)),
            'max': list(stats['max (m3/s)'].dropna(axis=0)),
            'stdlow': list(stats['std_dev_range_lower (m3/s)'].dropna(axis=0)),
            'stdup': list(stats['std_dev_range_upper (m3/s)'].dropna(axis=0)),
            'hires': list(stats['high_res (m3/s)'].dropna(axis=0)),
        }

    elif outformat in ['html', 'HTML']:
        tmp = stats[['datetime', 'mean (m3/s)']].dropna(axis=0)
        meanplot = Scatter(
            name='Mean',
            x=list(tmp['datetime']),
            y=list(tmp['mean (m3/s)']),
            line=dict(color='blue'),
        )
        tmp = stats[['datetime', 'max (m3/s)']].dropna(axis=0)
        rangemax = max(stats['max (m3/s)'])
        maxplot = Scatter(
            name='Max',
            x=list(tmp['datetime']),
            y=list(tmp['max (m3/s)']),
            fill='tonexty',
            mode='lines',
            line=dict(color='rgb(152, 251, 152)', width=0)
        )
        tmp = stats[['datetime', 'min (m3/s)']].dropna(axis=0)
        minplot = Scatter(
            name='Min',
            x=list(tmp['datetime']),
            y=list(tmp['min (m3/s)']),
            fill=None,
            mode='lines',
            line=dict(color='rgb(152, 251, 152)')
        )
        tmp = stats[['datetime', 'std_dev_range_lower (m3/s)']].dropna(axis=0)
        stdlow = Scatter(
            name='Std. Dev. Lower',
            x=list(tmp['datetime']),
            y=list(tmp['std_dev_range_lower (m3/s)']),
            fill='tonexty',
            mode='lines',
            line=dict(color='rgb(152, 251, 152)', width=0)
        )
        tmp = stats[['datetime', 'std_dev_range_upper (m3/s)']].dropna(axis=0)
        stdup = Scatter(
            name='Std. Dev. Upper',
            x=list(tmp['datetime']),
            y=list(tmp['std_dev_range_upper (m3/s)']),
            fill='tonexty',
            mode='lines',
            line={'width': 0, 'color': 'rgb(34, 139, 34)'}
        )
        tmp = stats[['datetime', 'high_res (m3/s)']].dropna(axis=0)
        hires = Scatter(
            name='Higher Resolution',
            x=list(tmp['datetime']),
            y=list(tmp['high_res (m3/s)']),
            line={'color': 'black'}
        )
        layout = Layout(
            title='Forecasted Streamflow<br>Stream ID: ' + str(reach_id),
            xaxis={'title': 'Date'},
            yaxis={
                'title': 'Streamflow (m<sup>3</sup>/s)',
                'range': [0, 1.2 * rangemax]
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
                    y1=1.2 * rangemax,
                    line={'width': 0},
                    opacity=.4,
                    fillcolor='purple'
                ),
            ]
        )
        return offplot(
            Figure([minplot, meanplot, maxplot, stdlow, stdup, hires], layout=layout),
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )

    else:
        raise ValueError('invalid outformat specified. pick json or html')


def historical(hist, rperiods, outformat='json'):
    if not isinstance(hist, pandas.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')

    r2 = rperiods.iloc[3][0]
    r10 = rperiods.iloc[2][0]
    r20 = rperiods.iloc[1][0]
    dates = hist['datetime'].tolist()
    startdate = dates[0]
    enddate = dates[-1]

    if outformat in ['json', 'JSON', 'dict', 'dictionary']:
        return

    if outformat in ['html', 'HTML']:
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
        return offplot(
            Figure([Scattergl(x=dates, y=hist['streamflow (m3/s)'].tolist())], layout=layout),
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False)

    raise ValueError('invalid outformat specified. pick json or html')


def daily_avg(daily, outformat='html'):
    if not isinstance(daily, pandas.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')

    if outformat in ['json', 'JSON', 'dict', 'dictionary']:
        return

    if outformat in ['html', 'HTML']:
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
        return offplot(
            Figure([Scatter(x=daily['day'].tolist(), y=daily['streamflow_avg (m3/s)'].tolist())], layout=layout),
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False
        )

    raise ValueError('invalid outformat specified. pick json or html')


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

    with open(os.path.join(os.pardir, 'templates', 'probabilities_table.html')) as template:
        return jinja2.Template(template.read()).render(days=days, r2=r2, r10=r10, r20=r20)


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
    return forecasted(stats, rperiods, reach_id) + probabilities_table(stats, ensembles, rperiods)
