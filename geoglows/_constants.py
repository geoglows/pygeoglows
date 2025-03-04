import os

ODP_FORECAST_S3_BUCKET_URI = 's3://geoglows-v2-forecasts'
ODP_S3_BUCKET_REGION = 'us-west-2'
DEFAULT_REST_ENDPOINT = 'https://geoglows.ecmwf.int/api/'
DEFAULT_REST_ENDPOINT_VERSION = 'v2'  # 'v1, v2, latest'

default_uri = {
    # forecasts

    # retrospective
    'retro_hourly': 's3://rfs-v2/retrospective/hourly.zarr',
    'retro_daily': 's3://rfs-v2/retrospective/daily.zarr',
    'retro_monthly': 's3://rfs-v2/retrospective/monthly-timeseries.zarr',
    'retro_yearly': 's3://rfs-v2/retrospective/yearly-timeseries.zarr',
    'fdc': 's3://rfs-v2/retrospective/fdc.zarr',
    'return_periods': 's3://rfs-v2/retrospective/return-periods.zarr',
    # transformers
    'sfdc': 's3://rfs-v2/transformers/sfdc.zarr',
    'hydroweb': 's3://rfs-v2/transformers/hydroweb.zarr',
    # tables
    'transformer_table': 's3://rfs-v2/transformers/transformer_table.parquet',
    'metadata_table': 'https://rfs-v2.s3-us-west-2.amazonaws.com/tables/model-metadata-table.parquet',
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
