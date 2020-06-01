from setuptools import setup

with open("README.md", "r") as readme:
    long_description = readme.read()

with open('requirements.txt', 'r') as req:
    install_requires = req.read().splitlines()

setup(
    name='geoglows',
    packages=['geoglows'],
    version='0.18',
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
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Hydrology',
        'Topic :: Scientific/Engineering :: Visualization',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
    ],
    install_requires=install_requires
)
