"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = delete_me.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This skeleton file can be safely removed if not needed!

References:
    - https://setuptools.readthedocs.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import logging

import click
import rich

from vep_lookup import __version__, lookup

__author__ = "Stephen Gaffney"
__copyright__ = "Stephen Gaffney"
__license__ = "GPL-3.0-or-later"

_logger = logging.getLogger(__name__)


@click.command()
@click.argument('chrom')
@click.argument('pos', type=int)
@click.argument('ref')
@click.argument('alt')
@click.option('-b', '--genome', type=click.Choice(['37', '38']), default='37',
              help='Genome version')
def lookup_cli(chrom, pos, ref, alt, genome):
    """VEP lookup for CHROM:POS REF>ALT."""
    console = rich.console.Console()
    console.print(f":mag: vep_lookup ({__version__})\n")
    console.print(f"USING BUILD {genome}\n")
    table_dict = lookup.get_var_tables(chrom=chrom, pos=pos, ref=ref, alt=alt,
                                       genome=int(genome))
    lookup.print_tables(table_dict)


if __name__ == '__main__':
    lookup_cli()
