import os

DEFAULT_REST_ENDPOINT = 'https://geoglows.ecmwf.int/api/'
DEFAULT_REST_ENDPOINT_VERSION = 'v2'  # 'v1, v2, latest'

ODP_CORE_S3_BUCKET_URI = 's3://geoglows-v2'
ODP_FORECAST_S3_BUCKET_URI = 's3://geoglows-v2-forecasts'
ODP_S3_BUCKET_REGION = 'us-west-2'

METADATA_TABLE_ENV_KEY = 'PYGEOGLOWS_METADATA_TABLE_PATH'
TRANSFORMER_TABLE_ENV_KEY = 'PYGEOGLOWS_TRANSFORMER_TABLE_URI'
SFDC_ZARR_ENV_KEY = 'PYGEOGLOWS_SFDC_ZARR_URI'


def get_sfdc_zarr_uri() -> str:
    return os.getenv(SFDC_ZARR_ENV_KEY, 's3://rfs-v2/transformers/sfdc.zarr')


def set_sfdc_zarr_uri(uri: str) -> None:
    os.environ[SFDC_ZARR_ENV_KEY] = uri
    return


def get_transformer_table_uri() -> str:
    return os.getenv(TRANSFORMER_TABLE_ENV_KEY, 's3://rfs-v2/transformers/transformer_table.parquet')


def set_transformer_table_uri(uri: str) -> None:
    os.environ[TRANSFORMER_TABLE_ENV_KEY] = uri
    return


def get_metadata_table_path() -> str:
    return os.getenv(METADATA_TABLE_ENV_KEY, os.path.join(os.path.dirname(__file__), 'data', 'metadata-tables.parquet'))


def set_metadata_table_path(path: str) -> None:
    os.environ[METADATA_TABLE_ENV_KEY] = path
    return
