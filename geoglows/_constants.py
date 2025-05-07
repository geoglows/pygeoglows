import os

ODP_FORECAST_S3_BUCKET_URI = 's3://geoglows-v2-forecasts'
ODP_S3_BUCKET_REGION = 'us-west-2'
BUCKET_BASE_URI = f's3://geoglows-v2'
DEFAULT_REST_ENDPOINT = 'https://geoglows.ecmwf.int/api/'
DEFAULT_REST_ENDPOINT_VERSION = 'v2'  # 'v1, v2, latest'

default_uri = {
    # forecasts

    # retrospective
    'retro_hourly': f'{BUCKET_BASE_URI}/retrospective/hourly.zarr',
    'retro_daily': f'{BUCKET_BASE_URI}/retrospective/daily.zarr',
    'retro_monthly': f'{BUCKET_BASE_URI}/retrospective/monthly-timeseries.zarr',
    'retro_yearly': f'{BUCKET_BASE_URI}/retrospective/yearly-timeseries.zarr',
    'fdc': f'{BUCKET_BASE_URI}/retrospective/fdc.zarr',
    'return_periods': f'{BUCKET_BASE_URI}/retrospective/return-periods.zarr',
    # transformers
    'sfdc': f'{BUCKET_BASE_URI}/transformers/sfdc.zarr',
    'hydroweb': f'{BUCKET_BASE_URI}/transformers/hydroweb.zarr',
    # tables
    'transformer_table': 'http://geoglows-v2.s3-us-west-2.amazonaws.com/transformers/transformer_table.parquet',
    'metadata_table': 'https://geoglows-v2.s3-us-west-2.amazonaws.com/tables/v2-model-table.parquet',
}

env_keys = {
    # forecasts

    # retrospective
    'retro_hourly': 'PYGEOGLOWS_RETRO_HOURLY_URI',
    'retro_daily': 'PYGEOGLOWS_RETRO_DAILY_URI',
    'retro_monthly': 'PYGEOGLOWS_RETRO_MONTHLY_URI',
    'retro_yearly': 'PYGEOGLOWS_RETRO_YEARLY_URI',
    'fdc': 'PYGEOGLOWS_FDC_URI',
    'return_periods': 'PYGEOGLOWS_RETURN_PERIODS_URI',
    # transformers
    'sfdc': 'PYGEOGLOWS_SFDC_URI',
    'hydroweb': 'PYGEOGLOWS_HYDROWEB_URI',
    # tables
    'transformer_table': 'PYGEOGLOWS_TRANSFORMER_TABLE_URI',
    'metadata_table': 'PYGEOGLOWS_METADATA_TABLE_PATH',
}


def get_uri(product_name):
    try:
        return os.getenv(env_keys[product_name], default_uri[product_name])
    except KeyError:
        raise KeyError(f'Product name {product_name} not found in default_uri or env_keys')


def set_uri(product_name, uri):
    if product_name not in env_keys:
        raise KeyError(f'Product name {product_name} not found in env_keys')
    os.environ[env_keys[product_name]] = uri
    return
