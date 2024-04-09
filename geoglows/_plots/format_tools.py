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
