try:
    import pandas

    from plotly.offline import plot as offplot
    from plotly.graph_objs import Scatter, Scattergl, Layout, Figure
    import plotly.graph_objs as go

except ImportError as error:
    raise error

from .streamflow import *


def forecasted(forecast, reach_id, returnperiods, outformat='json'):
    if not isinstance(forecast, pandas.DataFrame):
        raise ValueError('Sorry, I only process pandas dataframes right now')

    r2 = returnperiods.iloc[3][0]
    r10 = returnperiods.iloc[2][0]
    r20 = returnperiods.iloc[1][0]
    dates = historical['datetime'].tolist()
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


def historical(historical, returnperiods, outformat='json'):
    r2 = returnperiods.iloc[3][0]
    r10 = returnperiods.iloc[2][0]
    r20 = returnperiods.iloc[1][0]
    dates = historical['datetime'].tolist()
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
                'range': [0, 1.2 * max(historical['streamflow (m3/s)'])]
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
                    y1=1.2 * 1.2 * max(historical['streamflow (m3/s)']),
                    line={'width': 0},
                    opacity=.4,
                    fillcolor='purple'
                ),
            ]
        )
        return offplot(
            Figure([Scattergl(x=dates, y=historical['streamflow (m3/s)'].tolist())], layout=layout),
            config={'autosizable': True, 'responsive': True},
            output_type='div',
            include_plotlyjs=False)


def daily_avg(daily,):
    return


def probabilities_table(forecast, returnperiods):
    return
