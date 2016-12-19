from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='splunkinv',
    version='1.0',
    description='Dynamic ansible inventory from Splunk search',
    long_description=long_description,
    author='Lars Haugan',
    author_email='lars@larshaugan.net',
    packages=['splunkinv'],
    install_requires=['requests'],
    scripts=['splunkinv.py']
)
