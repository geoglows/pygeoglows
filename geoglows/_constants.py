import os

METADATA_TABLE_PATH = os.getenv(
    'PYGEOGLOWS_METADATA_TABLE_PATH',
    os.path.join(os.path.dirname(__file__), 'data', 'metadata-tables.parquet')
)
