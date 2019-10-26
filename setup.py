from setuptools import setup, find_packages

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3',
)
