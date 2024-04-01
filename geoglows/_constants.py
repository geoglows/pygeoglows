import os

METADATA_TABLE_LOCAL_PATH = os.path.join(os.path.dirname(__file__), 'data', 'metadata-tables.parquet')
s3_metadata_tables = [
    'http://geoglows-v2.s3-us-west-2.amazonaws.com/tables/v2-model-table.parquet',
    'http://geoglows-v2.s3-us-west-2.amazonaws.com/tables/v2-countries-table.parquet',
]
