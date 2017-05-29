from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name="statscraper",
    version="0.0.1",
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
        "hashlib",
        "json",
        "pandas",
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
