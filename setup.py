from setuptools import setup

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name='geoglows',
    packages=['geoglows'],
    version='0.10.1',
    description='Package for accessing data and APIs developed for the GEOGloWS initiative',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Riley Hales',
    url='https://geoglows.org',
    project_urls=dict(Documentation='https://geoglows.readthedocs.io', Source='https://github.com/rileyhales/geoglows'),
    license='BSD 3-Clause',
    license_family='BSD',
    package_data={'': ['*.ipynb', '*.html']},
    include_package_data=True,
    python_requires='>=3',
    install_requires=['requests', 'plotly', 'jinja2', 'pandas', 'shapely', 'scipy']
)
