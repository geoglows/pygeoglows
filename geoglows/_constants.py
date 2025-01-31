import os

ODP_S3_BUCKET_REGION = 'us-west-2'
ODP_RFS_V2_S3_BUCKET_URI = 's3://rfs-v2'
ODP_FORECAST_S3_BUCKET_URI = 's3://geoglows-v2-forecasts'

METADATA_TABLE_PATH_ENV_KEY = 'PYGEOGLOWS_METADATA_TABLE_PATH'
DEFAULT_TABLE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'metadata-tables.parquet')


def get_metadata_table_path() -> str:
    return os.getenv('PYGEOGLOWS_METADATA_TABLE_PATH', DEFAULT_TABLE_PATH)


def set_metadata_table_path(path: str) -> str:
    METADATA_TABLE_PATH = os.path.abspath(path)
    os.environ[METADATA_TABLE_PATH_ENV_KEY] = METADATA_TABLE_PATH
    return METADATA_TABLE_PATH
