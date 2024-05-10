geoglows
========
.. image:: https://anaconda.org/conda-forge/geoglows/badges/platforms.svg
        :target: https://anaconda.org/geoglows/geoglows
.. image:: https://img.shields.io/pypi/v/geoglows
        :target: https://pypi.org/project/geoglows
.. image:: https://anaconda.org/conda-forge/geoglows/badges/latest_release_date.svg
        :target: https://anaconda.org/geoglows/geoglows

The geoglows Python package enables access to data, API's, and code developed for the `GEOGLOWS Hydrology Model <https://geoglows.ecmwf.int>`_.
Read more about GEOGLOWS at `<https://geoglows.org>`_

For demos, tutorials, and other training materials for GEOGLOWS and the geoglows Python packge, please visit `<https://data.geoglows.org>`_.

Supplemental Data
=================
Some functions in this package will help you browse the metadata for the model to identify river locations, names, and
other information. It is available online at `<http://geoglows-v2.s3-website-us-west-2.amazonaws.com/tables/package-metadata-table.parquet>`_.
If you do not already have a copy downloaded, the code will fetch it for you and cache a copy in the same directory that
the source code of the package is installed in.

It is more efficient to save this file yourself and reuse it so that you do not have to download it every time your python
environment is recreated, the package version is updated, and so on. You may do this in several ways.

1. You can set the environment variable `PYGEOGLOWS_METADATA_TABLE_PATH` **before** importing the package.
2. Call the `geoglows.set_metadata_table_path` function to set the path the path at any time **after** importing.
3. Pass the path to the table to functions that use it.

About the GEOGLOWS Hydrology Model
==================================
The GEOGLOWS Hydrology Model is run each day at midnight (UTC +00). The model is based on the ECMWF ENS and HRES ensemble
of meteorology and land surface model forecasts. There are 51 members of the ensemble that drives the model each day.
The ERA5 reanalysis dataset is also used to produce a retrospective simulation on each river. The model provides river in
units m^3/s over the preceeding interval (1, 3, or 24 hours depending on the dataset). `Read more here <https://data.geoglows.org>`_.

.. toctree::
    :caption: Table of Contents
    :name: mastertoc
    :maxdepth: 1

    api-documentation
    license
