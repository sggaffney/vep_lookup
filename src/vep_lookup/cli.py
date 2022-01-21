import logging

import click
import rich

from vep_lookup import __version__, lookup

__author__ = "Stephen Gaffney"
__copyright__ = "Stephen Gaffney"
__license__ = "GPL-3.0-or-later"

_logger = logging.getLogger(__name__)


@click.command()
@click.argument("chrom")
@click.argument("pos", type=int)
@click.argument("ref")
@click.argument("alt")
@click.option(
    "-b",
    "--genome",
    type=click.Choice(["37", "38"]),
    default="37",
    help="Genome version",
)
def lookup_cli(chrom, pos, ref, alt, genome):
    """VEP lookup for CHROM:POS REF>ALT."""
    console = rich.console.Console()
    console.print(f":mag: vep_lookup ({__version__})\n")
    console.print(f"USING BUILD {genome}\n")
    try:
        table_dict = lookup.get_var_tables(
            chrom=chrom, pos=pos, ref=ref, alt=alt, genome=int(genome)
        )
        lookup.print_tables(table_dict)
    except lookup.InputException as e:
        raise click.UsageError(str(e))


if __name__ == "__main__":
    lookup_cli()
