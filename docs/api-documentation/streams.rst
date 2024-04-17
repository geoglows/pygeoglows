================
geoglows.streams
================

The functions in this module lookup metadata for rivers using a table of metadata about the GEOGLOWS model. This needs
to be downloaded or it can be retrieved and cached by the metadata table function in the data module.

If you download the table in advance, you can specify it with the PYGEOGLOWS_METADATA_TABLE_PATH environment variable
which will be checked at runtime. If it is not set, you need to restart the runtime or use the download function to
retrieve it.

.. automodule:: geoglows.streams
    :members:
        river_to_vpu, latlon_to_river, river_to_latlon
