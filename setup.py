# encoding: utf-8
from setuptools import setup


version = "1.0.0.dev1"


def readme():
    """Import README for use as long_description."""
    with open('README.rst') as f:
        return f.read()


setup(
    name="statscraper",
    version=version,
    description="""\
A base class for building web scrapers for statistical data.\
""",
    long_description=readme(),
    url="https://github.com/jplusplus/statscraper",
    author="Leo Wallentin and Jens Finnäs, J++ Stockholm; Robin Lindeborg",
    author_email='stockholm@jplusplus.org',
    license='MIT',
    packages=['statscraper'],
    zip_safe=False,
    install_requires=[
        "pandas",
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True,
    download_url="https://github.com/jplusplus/skrejperpark/archive/%s.tar.gz"
                 % version,
)
