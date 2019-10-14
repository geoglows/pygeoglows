============
geoglows.gfs
============

The gfs module contains functions that will request a timeseries from the most recent GFS forecast through the GFS Data
Tool Tethys application hosted by Brigham Young University. For more detailed documentation, see
[https://gfs.readthedocs.io/en/latest/]

help
----
The help function requires an API token and returns a dictionary full of helpful information for making requests. If
you do not provide an apikey, a sample token is provided for you.

.. code-block:: python

    import geoglows
    data = geoglows.gfs.help(apikey='Token my_alphanumeric_token')

variable_levels
---------------
Returns a dictionary containing the measurement levels associated with a specified GFS variable.

+-----------------+--------------------------------------------------------+--------------------------+
| Parameter       | Description                                            | Examples                 |
+=================+========================================================+==========================+
| variable        | The short name of a GFS variables                      | SUNSD                    |
+-----------------+--------------------------------------------------------+--------------------------+
| apikey          | An API token used to make the request                  | 'alpha_numeric_string'   |
+-----------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.gfs.variable_levels('SUNSD', apikey='Token my_alphanumeric_token')

point_timeseries
----------------
Returns a dictionary of timeseries data that can be plotted with Plotly Express. Requires the variable name,
measurement level, and the latitude and longitude of the point.

+-----------------+--------------------------------------------------------+--------------------------+
| Parameter       | Description                                            | Examples                 |
+=================+========================================================+==========================+
| variable        | The short name of a GFS variables                      | SUNSD                    |
+-----------------+--------------------------------------------------------+--------------------------+
| level           | The measurement level for the variable chosen          | surface                  |
+-----------------+--------------------------------------------------------+--------------------------+
| lat             | The latitude of the point                              | 40                       |
+-----------------+--------------------------------------------------------+--------------------------+
| lon             | The longitude of the point                             | -110                     |
+-----------------+--------------------------------------------------------+--------------------------+
| apikey          | An API token used to make the request                  | 'alpha_numeric_string'   |
+-----------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.gfs.point_timeseries('SUNSD', 'surface', 40, -110, apikey='Token my_alphanumeric_token')

box_timeseries
--------------
Returns a dictionary of timeseries data that can be plotted with Plotly Express. Requires the variable name,
measurement level, and the minimum and maximum latitudes and longitudes of the bounding box.

+-----------------+--------------------------------------------------------+--------------------------+
| Parameter       | Description                                            | Examples                 |
+=================+========================================================+==========================+
| variable        | The short name of a GFS variables                      | SUNSD                    |
+-----------------+--------------------------------------------------------+--------------------------+
| level           | The measurement level for the variable chosen          | surface                  |
+-----------------+--------------------------------------------------------+--------------------------+
| minlat          | The minimum latitude of the bounding box               | 40                       |
+-----------------+--------------------------------------------------------+--------------------------+
| maxlat          | The maximum latitude of the bounding box               | 40                       |
+-----------------+--------------------------------------------------------+--------------------------+
| minlon          | The minimum longitude of the bounding box              | 40                       |
+-----------------+--------------------------------------------------------+--------------------------+
| maxlon          | The maximum longitude of the bounding box              | 40                       |
+-----------------+--------------------------------------------------------+--------------------------+
| apikey          | An API token used to make the request                  | 'alpha_numeric_string'   |
+-----------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.gfs.box_timeseries('SUNSD', 'surface', 30, 40, -115, -105, apikey='Token my_alphanumeric_token')

region_timeseries
-----------------
Returns a dictionary of timeseries data that can be plotted with Plotly Express. Requires the variable name,
measurement level, and the minimum and maximum latitudes and longitudes of the bounding box.

+-----------------+--------------------------------------------------------+--------------------------+
| Parameter       | Description                                            | Examples                 |
+=================+========================================================+==========================+
| variable        | The short name of a GFS variables                      | SUNSD                    |
+-----------------+--------------------------------------------------------+--------------------------+
| level           | The measurement level for the variable chosen          | surface                  |
+-----------------+--------------------------------------------------------+--------------------------+
| region          | A UN world region or country name                      | Italy                    |
+-----------------+--------------------------------------------------------+--------------------------+
| apikey          | An API token used to make the request                  | 'alpha_numeric_string'   |
+-----------------+--------------------------------------------------------+--------------------------+

.. code-block:: python

    import geoglows
    data = geoglows.gfs.box_timeseries('SUNSD', 'surface', 30, 40, -115, -105, apikey='Token my_alphanumeric_token')
