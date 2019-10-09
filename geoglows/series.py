try:
    import pandas
    from plotly.offline import plot as offplot
    from plotly.graph_objs import Scatter, Scattergl, Layout, Figure
    import plotly.graph_objs as go
    import datetime
    import flask
    import os
except ImportError as error:
    raise error


def forecasted(forecast, returnperiods, reach_id, outformat='json'):
    if not isinstance(forecast, pandas.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')

    r2 = returnperiods.iloc[3][0]
    r10 = returnperiods.iloc[2][0]
    r20 = returnperiods.iloc[1][0]
    dates = forecast['datetime'].tolist()
    startdate = dates[0]
    enddate = dates[-1]

    if outformat in ['json', 'JSON', 'dict', 'dictionary']:
        hires = forecast[['datetime', 'high_res (m3/s)']].dropna(axis=0)
        tmp = forecast[['datetime', 'mean (m3/s)']].dropna(axis=0)
        return {
            'reach_id': reach_id,
            'x_ensembles': tmp['datetime'].tolist(),
            'x_hires': hires['datetime'].tolist(),
            'ymax': max(forecast['max (m3/s)']),
            'min': list(forecast['min (m3/s)'].dropna(axis=0)),
            'mean': list(forecast['mean (m3/s)'].dropna(axis=0)),
            'max': list(forecast['max (m3/s)'].dropna(axis=0)),
            'stdlow': list(forecast['std_dev_range_lower (m3/s)'].dropna(axis=0)),
            'stdup': list(forecast['std_dev_range_upper (m3/s)'].dropna(axis=0)),
            'hires': list(forecast['high_res (m3/s)'].dropna(axis=0)),
        }

    elif outformat in ['html', 'HTML']:
        tmp = forecast[['datetime', 'mean (m3/s)']].dropna(axis=0)
        meanplot = Scatter(
            name='Mean',
            x=list(tmp['datetime']),
            y=list(tmp['mean (m3/s)']),
            line=dict(color='blue'),
        )
        tmp = forecast[['datetime', 'max (m3/s)']].dropna(axis=0)
        rangemax = max(forecast['max (m3/s)'])
        maxplot = Scatter(
            name='Max',
            x=list(tmp['datetime']),
            y=list(tmp['max (m3/s)']),
            fill='tonexty',
            mode='lines',
            line=dict(color='rgb(152, 251, 152)', width=0)
        )
        tmp = forecast[['datetime', 'min (m3/s)']].dropna(axis=0)
        minplot = Scatter(
            name='Min',
            x=list(tmp['datetime']),
            y=list(tmp['min (m3/s)']),
            fill=None,
            mode='lines',
            line=dict(color='rgb(152, 251, 152)')
        )
        tmp = forecast[['datetime', 'std_dev_range_lower (m3/s)']].dropna(axis=0)
        stdlow = Scatter(
            name='Std. Dev. Lower',
            x=list(tmp['datetime']),
            y=list(tmp['std_dev_range_lower (m3/s)']),
            fill='tonexty',
            mode='lines',
            line=dict(color='rgb(152, 251, 152)', width=0)
        )
        tmp = forecast[['datetime', 'std_dev_range_upper (m3/s)']].dropna(axis=0)
        stdup = Scatter(
            name='Std. Dev. Upper',
            x=list(tmp['datetime']),
            y=list(tmp['std_dev_range_upper (m3/s)']),
            fill='tonexty',
            mode='lines',
            line={'width': 0, 'color': 'rgb(34, 139, 34)'}
        )
        tmp = forecast[['datetime', 'high_res (m3/s)']].dropna(axis=0)
        hires = Scatter(
            name='Higher Resolution',
            x=list(tmp['datetime']),
            y=list(tmp['high_res (m3/s)']),
            line={'color': 'black'}
        )
        layout = Layout(
            title='Forecasted Streamflow<br>Stream ID: ' + reach_id,
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


def historical(hist, returnperiods, outformat='json'):
    if not isinstance(hist, pandas.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')

    r2 = returnperiods.iloc[3][0]
    r10 = returnperiods.iloc[2][0]
    r20 = returnperiods.iloc[1][0]
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


def probabilities_table(forecast, ensembles, returnperiods):
    dates = forecast['datetime'].tolist()
    startdate = dates[0]
    enddate = dates[-1]
    start_datetime = datetime.datetime.strptime(startdate, "%Y-%m-%d %H:00:00")
    span = datetime.datetime.strptime(enddate, "%Y-%m-%d %H:00:00") - start_datetime
    uniqueday = [start_datetime + datetime.timedelta(days=i) for i in range(span.days + 2)]
    # get the return periods for the stream reach
    r2 = returnperiods.iloc[3][0]
    r10 = returnperiods.iloc[2][0]
    r20 = returnperiods.iloc[1][0]

    # Build the ensemble stat table- iterate over each day and then over each ensemble.
    returntable = {'days': [], 'r2': [], 'r10': [], 'r20': []}
    for i in range(len(uniqueday) - 1):  # (-1) omit the extra day used for reference only
        tmp = ensembles.loc[uniqueday[i]:uniqueday[i + 1]]
        returntable['days'].append(uniqueday[i].strftime('%b %d'))
        num2 = 0
        num10 = 0
        num20 = 0
        for column in tmp:
            if any(i > r20 for i in tmp[column].to_numpy()):
                num2 += 1
                num10 += 1
                num20 += 1
            elif any(i > r10 for i in tmp[column].to_numpy()):
                num10 += 1
                num2 += 1
            elif any(i > r2 for i in tmp[column].to_numpy()):
                num2 += 1
        returntable['r2'].append(round(num2 * 100 / 52))
        returntable['r10'].append(round(num10 * 100 / 52))
        returntable['r20'].append(round(num20 * 100 / 52))

    return flask.render_template(os.path.join(os.pardir, 'templates', 'return_period_table.html'), returntable)


def hydroviewer(forecast, ensembles, returnperiods, reach_id):
    return forecasted(forecast, returnperiods, reach_id) + probabilities_table(forecast, ensembles, returnperiods)
