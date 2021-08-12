import os
import pandas as pd


def stats():
    """
    Returns a pandas dataframe of forecast stats data which provides a good visualization
    """
    return pd.read_pickle(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'stats_example.pickle')))


def ens():
    """
    Returns a pandas dataframe of forecast ensembles data which provides a good visualization
    """
    return pd.read_pickle(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'ens_example.pickle')))


def hist():
    """
    Returns a pandas dataframe of historical simulation data which provides a good visualization
    """
    return pd.read_pickle(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'hist_example.pickle')))


def rec():
    """
    Returns a pandas dataframe of forecast records data which provides a good visualization
    """
    return pd.read_pickle(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'rec_example.pickle')))


def rper():
    """
    Returns a pandas dataframe of return periods data which provides a good visualization
    """
    return pd.read_pickle(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'rper_example.pickle')))
