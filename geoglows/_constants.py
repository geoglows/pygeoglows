import os

ODP_FORECAST_S3_BUCKET_URI = 's3://geoglows-v2-forecasts'
ODP_S3_BUCKET_REGION = 'us-west-2'
DEFAULT_REST_ENDPOINT = 'https://geoglows.ecmwf.int/api/'
DEFAULT_REST_ENDPOINT_VERSION = 'v2'  # 'v1, v2, latest'

default_uri = {
    # forecasts
    # retrospective
    'retrospective': 's3://rfs-v2/retrospective/hourly.zarr',
    'daily_averages': 's3://rfs-v2/retrospective/daily.zarr',
    'monthly_averages': 's3://rfs-v2/retrospective/monthly-timeseries.zarr',
    'annual_averages': 's3://rfs-v2/retrospective/yearly-timeseries.zarr',
    'fdc': 's3://rfs-v2/retrospective/fdc.zarr',
    'return_periods': 's3://rfs-v2/retrospective/return-periods.zarr',
    # transformers
    'sfdc': 's3://rfs-v2/transformers/sfdc.zarr',
    'hydroweb': 's3://rfs-v2/transformers/hydroweb.zarr',
    # tables
    'transformer_table': 's3://rfs-v2/transformers/transformer_table.parquet',
    'metadata_table': 's3://geoglows-v2/transformers/metadata-tables.parquet',
}

env_keys = {
    # forecasts
    # retrospective
    'retrospective': 'PYGEOGLOWS_RETROSPECTIVE_URI',
    'daily_averages': 'PYGEOGLOWS_DAILY_AVERAGES_URI',
    'monthly_averages': 'PYGEOGLOWS_MONTHLY_AVERAGES_URI',
    'annual_averages': 'PYGEOGLOWS_ANNUAL_AVERAGES_URI',
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
    return os.getenv(env_keys[product_name], default_uri[product_name])


def set_uri(product_name, uri):
    os.environ[env_keys[product_name]] = uri
    return
