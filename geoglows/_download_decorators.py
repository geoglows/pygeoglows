import warnings
from io import StringIO

import numpy as np
import pandas as pd
import requests
import s3fs
import xarray as xr

from ._constants import (
    ODP_FORECAST_S3_BUCKET_URI,
    ODP_S3_BUCKET_REGION,
    DEFAULT_REST_ENDPOINT,
    DEFAULT_REST_ENDPOINT_VERSION,
    get_uri,
)
from .analyze import (
    simple_forecast as calc_simple_forecast,
    forecast_stats as calc_forecast_stats,
)

__all__ = [
    '_forecast',
    '_retrospective',
]


def _forecast(function):
    def from_aws(*args, **kwargs):
        product_name = function.__name__.replace("_", "").lower()
        if product_name == 'forecastrecords':
            warnings.warn('forecast_records are not available from the AWS Open Data Program.')
            return from_rest(*args, **kwargs)

        river_id = args[0] if len(args) > 0 else kwargs.get('river_id', None)
        if river_id is None and product_name != 'dates':
            raise ValueError('River ID must be provided to retrieve forecast data.')

        return_format = kwargs.get('format', 'df')
        assert return_format in ('df', 'xarray'), f'Unsupported return format requested: {return_format}'

        if kwargs.get('skip_log', False):
            requests.post(f'{DEFAULT_REST_ENDPOINT}{DEFAULT_REST_ENDPOINT_VERSION}/log',
                          json={'river_id': river_id, 'product': product_name, 'format': return_format},
                          timeout=1, )  # short timeout- don't need the response, post only needs to be received

        date = kwargs.get('date', False)
        if not date:
            print('Date not specified. Must be searched on s3. Specify the date for fastest results.')
            s3 = s3fs.S3FileSystem(anon=True, client_kwargs=dict(region_name=ODP_S3_BUCKET_REGION))
            zarr_vars = ['rivid', 'Qout', 'time', 'ensemble']
            dates = [s3.glob(ODP_FORECAST_S3_BUCKET_URI + '/' + f'*.zarr/{var}') for var in zarr_vars]
            dates = [set([d.split('/')[1].replace('.zarr', '') for d in date]) for date in dates]
            dates = sorted(set.intersection(*dates), reverse=True)
            if product_name == 'dates':
                return pd.DataFrame(dict(dates=dates))
            date = dates[0]
        if len(date) == 8:
            date = f'{date}00.zarr'
        elif len(date) == 10:
            date = f'{date}.zarr'
        else:
            raise ValueError('Date must be YYYYMMDD or YYYYMMDDHH format. Use dates() to view available data.')

        attrs = {
            'source': 'geoglows',
            'forecast_date': date[:8],
            'retrieval_date': pd.Timestamp.now().strftime('%Y%m%d'),
            'units': 'cubic meters per second',
        }

        file_uri = f'{ODP_FORECAST_S3_BUCKET_URI}/{date}'
        with xr.open_zarr(file_uri, zarr_format=2, storage_options={'anon': True}).sel(rivid=river_id) as ds:
            if return_format == 'xarray' and product_name == 'forecastensembles':
                ds = ds.rename({'time': 'datetime', 'rivid': 'river_id'})
                ds.attrs = attrs
                return ds
            df = ds.to_dataframe().round(2).reset_index()
            df['time'] = pd.to_datetime(df['time'], utc=True)

            # rename columns to match the REST API
            if isinstance(river_id, int) or isinstance(river_id, np.int64):
                df = df.pivot(index='time', columns='ensemble', values='Qout')
            else:
                df = df.pivot(index=['time', 'rivid'], columns='ensemble', values='Qout')
                df.index.names = ['time', 'river_id']
            df = df[sorted(df.columns)]
            df.columns = [f'ensemble_{str(x).zfill(2)}' for x in df.columns]

            if product_name == 'forecast':
                df = calc_simple_forecast(df)
            elif product_name == 'forecaststats':
                df = calc_forecast_stats(df)

            if return_format == 'df':
                return df
            ds = df.to_xarray()
            ds.attrs = attrs
            return ds

    def from_rest(*args, **kwargs):
        # update the default values set by the function unless the user has already specified them
        for key, value in function.__kwdefaults__.items() if function.__kwdefaults__ else []:
            if key not in kwargs:
                kwargs[key] = value

        return_format = kwargs.get('format', 'csv')
        assert return_format in ('csv', 'json', 'url'), f'Unsupported format requested: {return_format}'

        # parse out the information necessary to build a request url
        endpoint = kwargs.get('endpoint', DEFAULT_REST_ENDPOINT)
        endpoint = endpoint[:-1] if endpoint[-1] == '/' else endpoint
        endpoint = endpoint + '/api' if not endpoint.endswith('/api') else endpoint
        endpoint = f'https://{endpoint}' if not endpoint.startswith(('https://', 'http://')) else endpoint

        version = kwargs.get('version', DEFAULT_REST_ENDPOINT_VERSION)
        assert version in ('v2',), ValueError(f'Unrecognized model version parameter: {version}')

        product_name = function.__name__.replace("_", "").lower()

        river_id = args[0] if len(args) > 0 else kwargs.get('river_id', None)
        if river_id is None and product_name != 'dates':
            raise ValueError('River ID must be provided to retrieve forecast data.')
        if not isinstance(river_id, (int, np.int64,)):
            raise ValueError('Multiple river_ids are not available via REST API. Provide a single 9 digit integer.')
        if river_id and version == 'v2':
            assert 1_000_000_000 > river_id >= 110_000_000, ValueError('River ID must be a 9 digit integer')

        # request parameter validation before submitting
        for key in ('endpoint', 'version', 'river_id'):
            if key in kwargs:
                del kwargs[key]
        for key, value in kwargs.items():
            if value is None:
                del kwargs[key]
        for date in ('date', 'start_date', 'end_date'):
            if date in kwargs:
                assert len(str(kwargs[date])) == 8 or len(
                    str(kwargs[date])) == 10, f'Invalid date format: {kwargs[date]}'
        if 'format' in kwargs and kwargs['format'] != 'json':
            del kwargs['format']
        kwargs['source'] = kwargs.get('source', 'pygeoglows')  # allow using default for specific apps which override
        params = '&'.join([f'{key}={value}' for key, value in kwargs.items()])

        # piece together the request url
        request_url = f'{endpoint}/{version}/{product_name}'  # build the base url
        request_url = f'{request_url}/{river_id}' if river_id else request_url  # add the river_id if it exists
        request_url = f'{request_url}?{params}'  # add the query parameters

        if return_format == 'url':
            return request_url.replace(f'source={kwargs["source"]}', '')

        response = requests.get(request_url)

        if response.status_code != 200:
            raise RuntimeError('Received an error from the REST API: ' + response.text)

        if return_format == 'csv':
            df = pd.read_csv(StringIO(response.text))
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                if df.index.tz is None:
                    df.index = df.index.tz_localize('UTC')
            return df
        elif return_format == 'json':
            return response.json()
        else:
            raise ValueError(f'Unsupported return format requested: {return_format}')

    def main(*args, **kwargs):
        source = kwargs.get('data_source', 'aws')
        assert source in ('rest', 'aws'), ValueError(f'Unrecognized data source requested: {source}')
        if source == 'rest':
            return from_rest(*args, **kwargs)
        return from_aws(*args, **kwargs)

    main.__doc__ = function.__doc__  # necessary for code documentation auto generators
    main.__name__ = function.__name__
    return main


def _retrospective(function):
    def main(*args, **kwargs):
        products = ('retro_hourly', 'retro_daily', 'retro_monthly', 'retro_yearly', 'fdc', 'return_periods')
        river_id = args[0] if len(args) > 0 else kwargs.get('river_id', None)
        return_format = kwargs.get('format', 'df')
        resolution = kwargs.get('resolution', 'hourly')
        distribution = kwargs.get('distribution', 'logpearson3')  # only used for return_periods
        fdc_type = kwargs.get('fdc_type', 'monthly')  # only used for fdc

        product_name = function.__name__.lower()

        if product_name == 'retrospective':
            product_name = f"retro_{resolution}"
            assert product_name in products, ValueError('Unrecognized retrospective simulation resolution')
        assert return_format in ('df', 'xarray'), f'Unsupported return format requested: {return_format}'

        if kwargs.get('skip_log', False):
            requests.post(f'{DEFAULT_REST_ENDPOINT}{DEFAULT_REST_ENDPOINT_VERSION}/log',
                          timeout=1,  # short timeout. don't need the response, post just needs to be received
                          json={'river_id': river_id, 'product': product_name, 'format': return_format})

        uri = get_uri(product_name)
        storage_options = {'anon': True} if uri.startswith('s3://geoglows-v2') else None
        storage_options = kwargs.get('storage_options', storage_options)

        with xr.open_zarr(uri, zarr_format=2, storage_options=storage_options) as ds:
            if return_format == 'xarray':
                return ds
            if river_id is None:
                raise ValueError('River ID must be provided to retrieve retrospective data.')
            try:
                ds = ds.sel(river_id=river_id)
            except Exception:
                raise ValueError(f'River ID(s) not found in the retrospective dataset: {river_id}')
            if product_name in ('retro_hourly', 'retro_daily', 'retro_monthly', 'retro_yearly'):
                df = (
                    ds
                    .to_dataframe()
                    .reset_index()
                    .pivot(columns='river_id', values='Q', index='time')
                )
                df.index = df.index.tz_localize('UTC')
                return df
            if product_name == 'fdc':
                assert resolution in ('daily', 'hourly'), f'Unsupported resolution requested: {resolution}'
                assert fdc_type in ('total', 'monthly'), f'Unsupported fdc_type: {fdc_type}'
                var_name = f'{resolution}{f"_{fdc_type}" if fdc_type == "monthly" else ""}'
                index = ['month', 'p_exceed'] if fdc_type == 'monthly' else ['p_exceed']
                return (
                    ds
                    [var_name]
                    .to_dataframe()
                    .reset_index()
                    .pivot(columns='river_id', values=var_name, index=index)
                )
            if product_name == 'return_periods':
                distributions = ('gumbel', 'logpearson3')
                assert distribution in distributions, f'Unrecognized return period estimation method given: {distribution}'
                return (
                    ds
                    [distribution]
                    .to_dataframe()
                    .reset_index()
                    .pivot(columns='river_id', index='return_period', values=distribution)
                )
            raise ValueError(f'Unsupported product requested: {product_name}')

    main.__doc__ = function.__doc__  # necessary for code documentation auto generators
    main.__name__ = function.__name__
    return main
