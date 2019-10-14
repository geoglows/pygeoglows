==============
geoglows.gldas
==============

The gldas module contains functions that will request a timeseries from the GLDAS historical dataset using the GLDAS
Data Tool Tethys application hosted by Brigham Young University. For more detailed documentation, see
[https://gldas-data-tool.readthedocs.io/en/latest/]

help
----
The help function requires an API token and returns a dictionary full of helpful information for making requests. If
you do not provide an apikey, a sample token is provided for you.

.. code-block:: python

    import geoglows
    data = geoglows.gldas.help(apikey='Token my_alphanumeric_token')

point_timeseries
----------------
Returns a dictionary of timeseries data that can be plotted with Plotly Express. Requires the variable name,
measurement level, and the latitude and longitude of the point.

+-----------------+--------------------------------------------------------+--------------------------+
| Parameter       | Description                                            | Examples                 |
+=================+========================================================+==========================+
| time            | A year or decade                                       | 1990's, 2012             |
+-----------------+--------------------------------------------------------+--------------------------+
| variable        | The short name of a GLDAS variables                    | 'Tair_f_inst'            |
+-----------------+--------------------------------------------------------+--------------------------+
| lat             | The latitude of the point                              | 40                       |
+-----------------+--------------------------------------------------------+--------------------------+
| lon             | The longitude of the point                             | -110                     |
+-----------------+--------------------------------------------------------+--------------------------+
| apikey          | An API token used to make the request                  | 'alpha_numeric_string'   |
+-----------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.gldas.point_timeseries("2010's", 'Tair_f_inst', 40, -110, apikey='Token my_alphanumeric_token')

box_timeseries
--------------
Returns a dictionary of timeseries data that can be plotted with Plotly Express. Requires the variable name,
measurement level, and the minimum and maximum latitudes and longitudes of the bounding box.

+-----------------+--------------------------------------------------------+--------------------------+
| Parameter       | Description                                            | Examples                 |
+=================+========================================================+==========================+
| time            | A year or decade                                       | 1990's, 2012             |
+-----------------+--------------------------------------------------------+--------------------------+
| variable        | The short name of a GLDAS variables                    | 'Tair_f_inst'            |
+-----------------+--------------------------------------------------------+--------------------------+
| minlat          | The minimum latitude of the bounding box               | 30                       |
+-----------------+--------------------------------------------------------+--------------------------+
| maxlat          | The maximum latitude of the bounding box               | 40                       |
+-----------------+--------------------------------------------------------+--------------------------+
| minlon          | The minimum longitude of the bounding box              | -115                     |
+-----------------+--------------------------------------------------------+--------------------------+
| maxlon          | The maximum longitude of the bounding box              | -105                     |
+-----------------+--------------------------------------------------------+--------------------------+
| apikey          | An API token used to make the request                  | 'alpha_numeric_string'   |
+-----------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.gldas.box_timeseries(1990, 'Tair_f_inst', 30, 40, -115, -105, apikey='Token my_alphanumeric_token')

region_timeseries
-----------------
Returns a dictionary of timeseries data that can be plotted with Plotly Express. Requires the variable name,
measurement level, and the minimum and maximum latitudes and longitudes of the bounding box.

+-----------------+--------------------------------------------------------+--------------------------+
| Parameter       | Description                                            | Examples                 |
+=================+========================================================+==========================+
| time            | A year or decade                                       | 1990's, 2012             |
+-----------------+--------------------------------------------------------+--------------------------+
| variable        | The short name of a GLDAS variables                    | 'Tair_f_inst'            |
+-----------------+--------------------------------------------------------+--------------------------+
| region          | A UN world region or country name                      | Italy                    |
+-----------------+--------------------------------------------------------+--------------------------+
| apikey          | An API token used to make the request                  | 'alpha_numeric_string'   |
+-----------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.gldas.box_timeseries(2005, 'Tair_f_inst', 'Italy', apikey='Token my_alphanumeric_token')
