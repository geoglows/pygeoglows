from setuptools import setup, find_packages

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="geoglowstoolbox",
    version="0.0.1",
    author="Riley Hales",
    description="Tools for accessing data and API's developed for the GEOGloWS initiative",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rileyhales/geoglowstoolbox",
    packages=find_packages(),
    classifiers=[],
    python_requires='>=3.7',
)
