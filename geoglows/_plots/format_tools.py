import datetime

import pytz
from plotly.offline import plot as offline_plot


def build_title(main_title, plot_titles: list):
    if plot_titles is not None:
        main_title += '<br>'.join(plot_titles)
    return main_title


def return_period_plot_colors():
    return {
        '2 Year': 'rgba(254, 240, 1, .4)',
        '5 Year': 'rgba(253, 154, 1, .4)',
        '10 Year': 'rgba(255, 56, 5, .4)',
        '20 Year': 'rgba(128, 0, 246, .4)',
        '25 Year': 'rgba(255, 0, 0, .4)',
        '50 Year': 'rgba(128, 0, 106, .4)',
        '100 Year': 'rgba(128, 0, 246, .4)',
    }


def plotly_figure_to_html_plot(figure, include_plotlyjs: bool = False, ) -> str:
    return offline_plot(
        figure,
        config={'autosizable': True, 'responsive': True},
        output_type='div',
        include_plotlyjs=include_plotlyjs
    )


def timezone_label(timezone: str = None):
    timezone = str(timezone) if timezone is not None else 'UTC'
    # get the number of hours the timezone is offset from UTC
    now = datetime.datetime.now(pytz.timezone(timezone))
    utc_offset = now.utcoffset().total_seconds() / 3600
    # convert float number of hours to HH:MM format
    utc_offset = f'{int(utc_offset):+03d}:{int((utc_offset % 1) * 60):02d}'
    return f'Datetime ({timezone} {utc_offset})'
