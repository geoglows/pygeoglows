geoglows
========
.. image:: https://anaconda.org/geoglows/geoglows/badges/platforms.svg
        :target: https://anaconda.org/geoglows/geoglows
.. image:: https://img.shields.io/pypi/v/geoglows
        :target: https://pypi.org/project/geoglows
.. image:: https://anaconda.org/geoglows/geoglows/badges/latest_release_date.svg
        :target: https://anaconda.org/geoglows/geoglows

The geoglows python package is intended to promote access to data, API's, and code developed for the `GEOGloWS ECMWF Streamflow Model <https://geoglows.ecmwf.int>`_.
Read more about GEOGloWS at `<https://geoglows.org>`_

Demos
=====
These links will be maintained to reference the most updated versions of the tutorials.
The tutorials are GitHub Gists which you can copy and launch in a Google Collaboratory setting directly from the GitHub.

- Retrieve & plot GEOGloWS model data: `<https://gist.github.com/rileyhales/873896e426a5bd1c4e68120b286bc029>`_
- Finding Stream ID #'s programatically: `<https://gist.github.com/rileyhales/ad92d1fce3aa36ef5873f2f7c2632d31>`_
- Bias Evaluation and Calibration at a point: `<https://gist.github.com/rileyhales/d5290e12b5858d59960d0898fbd0ed69>`_
- Generate/Download High Res Plot Images: `<https://gist.github.com/rileyhales/9b5bbb0c5f307eb14b9f1ced39d641e4>`_

About GEOGloWS ECMWF Streamflow
===============================
GEOGloWS ECMWF Streamflow Project: This project provides access to the results of a hydrologic model that is run each
day. The model is based on a group of unique weather forecasts, known as an ensemble, from ECMWF. Each unique
precipitation forecast, known as an ensemble member, produces a unique streamflow forecast. There are 52 members of the
ensemble that drives the model each day. The ERA-5 historical precipitation dataset to also used to produce a
hindcasted streamflow on each river. `Read more here <https://geoglows.ecmwf.int>`_.

.. toctree::
    :caption: Table of Contents
    :name: mastertoc
    :maxdepth: 1

    api-documentation
    dev-notes
    license
