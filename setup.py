from setuptools import setup

setup(
    name='flask-io',
    version='1.3.2',
    packages=['flask_io'],
    url='https://github.com/viniciuschiele/flask-io',
    license='Apache 2.0',
    author='Vinicius Chiele',
    author_email='vinicius.chiele@gmail.com',
    description='Flask IO is a library for Python 3+ which make easier to parse request arguments and serialize responses.',
    keywords=['flask', 'rest', 'parse', 'encode', 'decode', 'request', 'json'],
    install_requires=['flask>=0.10.1', 'python-dateutil>=2.4.2', 'marshmallow==2.0.0rc2'],
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
