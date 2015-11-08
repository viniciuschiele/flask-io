import flask_io

from setuptools import setup

setup(
    name='flask-io',
    version=flask_io.__version__,
    packages=['flask_io'],
    url='https://github.com/viniciuschiele/flask-io',
    license=flask_io.__license__,
    author=flask_io.__version__,
    author_email='vinicius.chiele@gmail.com',
    description='Flask-IO is a library for parsing Flask request arguments into parameters and for serialization of complex objects into Flask response.',
    keywords=['flask', 'rest', 'parse', 'encode', 'decode', 'request', 'json', 'marshmallow'],
    install_requires=['flask==0.10.1', 'python-dateutil>=2.4.2', 'marshmallow==2.2.0'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython'
    ]
)
