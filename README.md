# vep_lookup

Look up VEP variant annotation via CLI.

```text
Usage: lookup_vep [OPTIONS] CHROM POS REF ALT

  VEP lookup for CHROM:POS REF>ALT.

Options:
  -b, --genome [37|38]  Genome version
  --help                Show this message and exit.
```

```shell
# Example: Look up 5:7520801 G>A
lookup_vep -b38 5 7520801 G A
```

## Installation

```shell
# Option 1: Remote pip install directly from GitHub
pip install git+https://github.com/sggaffney/vep_lookup.git

# Option 2: Run from lookup_vep code directory
python setup.py develop
```

## Note

This project has been set up using PyScaffold 4.0.2. For details and usage
information on PyScaffold see https://pyscaffold.org/.
