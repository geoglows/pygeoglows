import pandas as pd
import plotly.graph_objects as go

from .format_tools import return_period_plot_colors

__all__ = [
    '_rperiod_scatters'
]


def _rperiod_scatters(startdate: str,
                      enddate: str,
                      rperiods: pd.DataFrame,
                      y_max: float,
                      max_plotted_flow: float = 0,
                      visible: bool = None):
    colors = return_period_plot_colors()
    x_vals = (startdate, enddate, enddate, startdate)

    r2 = int(rperiods[2].values[0])
    r5 = int(rperiods[5].values[0])
    r10 = int(rperiods[10].values[0])
    r25 = int(rperiods[25].values[0])
    r50 = int(rperiods[50].values[0])
    r100 = int(rperiods[100].values[0])
    rmax = int(max(2 * r100 - r25, y_max))

    visible = True if max_plotted_flow > r2 else 'legendonly'

    def template(name, y, color, fill='toself'):
        return go.Scatter(
            name=name,
            x=x_vals,
            y=y,
            legendgroup='returnperiods',
            fill=fill,
            visible=visible,
            line=dict(color=color, width=0))

    return [
        template('Return Periods', (r2, r2, rmax, rmax), 'rgba(0,0,0,0)', fill='none'),
        template(f'2 Year: {r2}', (r2, r2, r5, r5), colors['2 Year']),
        template(f'5 Year: {r5}', (r5, r5, r10, r10), colors['5 Year']),
        template(f'10 Year: {r10}', (r10, r10, r25, r25), colors['10 Year']),
        template(f'25 Year: {r25}', (r25, r25, r50, r50), colors['25 Year']),
        template(f'50 Year: {r50}', (r50, r50, r100, r100), colors['50 Year']),
        template(f'100 Year: {r100}', (r100, r100, rmax, rmax), colors['100 Year']),
    ]
