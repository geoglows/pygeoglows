================
Developing Notes
================

Packaging for PyPi
~~~~~~~~~~~~~~~~~~
Sign up for an account on pypi.org

.. code-block:: bash

	pip install twine
	python setup.py sdist
	twine upload dist/name_of_dist.tar.gz

Packaging for Conda/Anaconda Cloud
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sign up for an account on anaconda.org

.. code-block:: bash

	conda install anaconda-client conda-build
	conda build .
	anaconda upload /path/to/distribution -u user_or_group_name -l label

Developing documentation
~~~~~~~~~~~~~~~~~~~~~~~~
Use Sphinx

.. code-block:: bash

	conda install sphinx sphinx_rtd_theme
	make html