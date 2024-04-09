*****************
API Documentation
*****************

There are 3 modules in the geoglows package.

.. toctree::
   :maxdepth: 3

   api-documentation/data
   api-documentation/bias
   api-documentation/plots
   api-documentation/analyze


FAQ
~~~

How do I save streamflow data to csv?
-------------------------------------
By default, the results of most of the `geoglows.data` functions return a pandas DataFrame. You can save those to
a csv, json, pickle, or other file. For example, save to csv with the dataframe's ``.to_csv()`` method.

.. code-block:: python

   # get some data from the geoglows streamflow model
   data = geoglows.streamflow.forecast_stats(12341234)
   # save it to a csv
   data.to_csv('/path/to/save/the/csv/file.csv')