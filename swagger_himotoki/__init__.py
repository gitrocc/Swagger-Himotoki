# -*- coding: utf-8 -*-

import click
from swagger_himotoki import SwaggerHimotoki

__author__ = 'Ryosuke Nakashiro'

@click.command()
@click.argument('yml_file', type=click.File('r'))
@click.option('--prefix', help='Prefix for Class Name.')
def main(yml_file, prefix):
    SwaggerHimotoki.load_args(yml_file, prefix=prefix).export_himotoki()
