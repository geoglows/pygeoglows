from setuptools import setup, find_packages

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name='geoglows',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['geoglows'],
    package_data={'': ['*.ipynb', '*.html']},
    include_package_data=True,
    python_requires='>=3',
)
