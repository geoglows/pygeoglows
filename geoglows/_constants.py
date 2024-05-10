import os

ODP_CORE_S3_BUCKET_URI = 's3://geoglows-v2'
ODP_FORECAST_S3_BUCKET_URI = 's3://geoglows-v2-forecasts'
ODP_RETROSPECTIVE_S3_BUCKET_URI = 's3://geoglows-v2-retrospective'
ODP_S3_BUCKET_REGION = 'us-west-2'

METADATA_TABLE_PATH = os.getenv(
    'PYGEOGLOWS_METADATA_TABLE_PATH',
    os.path.join(os.path.dirname(__file__), 'data', 'metadata-tables.parquet')
)


def get_metadata_table_path() -> str:
    return METADATA_TABLE_PATH


def set_metadata_table_path(path: str) -> str:
    global METADATA_TABLE_PATH
    METADATA_TABLE_PATH = path
    return METADATA_TABLE_PATH
