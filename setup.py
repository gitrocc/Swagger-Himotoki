# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

__author__ = 'Ryosuke Nakashiro'

setup(
    name='swagger_himotoki', 
    version='0.0.1', 
    description='Simple script to generate Himotoki code in Swift 3.0 by Swagger yaml.', 
    author='Ryosuke Nakashiro', 
    #author_email='', 
    url='https://github.com/gitrocc/Swagger-Himotoki', 
    classifiers=[ 
        'License :: OSI Approved :: MIT License',
    ],
    packages=find_packages(), 
    include_package_data=False, 
    keywords=['Swagger', 'Himotoki', 'Swift'], 
    license='MIT License', 
    install_requires=[ 
        'click', 
        'PyYAML', 
        'jinja2', 
    ],
    entry_points="""
        [console_scripts]
        swagger_himotoki = swagger_himotoki:main
    """,
)