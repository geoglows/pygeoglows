from setuptools import setup, find_packages

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="geoglows",
    version="0.0.1",
    author="Riley Hales",
    license='BSD 3-Clause',
    description="Package for accessing data and APIs developed for the GEOGloWS initiative",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rileyhales/geoglows",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires='>=3.7',
)
