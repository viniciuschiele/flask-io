from setuptools import setup

setup(
    name='Flask-Binding',
    version='0.5.0',
    packages=['flask_binding'],
    url='https://github.com/viniciuschiele/flask-binding',
    license='Apache 2.0',
    author='Vinicius Chiele',
    author_email='vinicius.chiele@gmail.com',
    description='Adds support to turn arguments from the Flask request into method parameters.',
    keywords=['flask', 'rest', 'parse', 'request'],
    install_requires=['flask>=0.10.1', 'python-dateutil>=2.4.2'],
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
