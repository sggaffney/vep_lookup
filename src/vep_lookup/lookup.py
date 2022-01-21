import json
import os

import click
import requests
import pandas as pd
from rich.console import Console


SERVER_38 = "https://rest.ensembl.org"
SERVER_37 = "http://grch37.rest.ensembl.org"
ENDPOINT = "vep/human/hgvs"


def get_var_tables(chrom, pos, ref, alt, genome=37):
    """Get info tables for specified variant."""
    if genome not in {37, 38}:
        raise ValueError("genome argument must be 37 or 38.")
    server = SERVER_37 if genome == 37 else SERVER_38
    # query examples: "9:g.22125504G>C", 'ENSP00000401091.1:p.Tyr124Cys'
    query = f"{chrom}:g.{pos}{ref}>{alt}"
    r = requests.get(
        f"{server}/{ENDPOINT}/{query}",
        params={"content-type": "application/json", "canonical": "1"},
    )
    if 'error' in r.json():
        raise Exception(r.json()['error'])

    j = r.json()[0]
    other_keys = set(j.keys()).difference(
        ["transcript_consequences", "colocated_variants"]
    )
    meta = pd.Series({i: j[i] for i in sorted(other_keys)})
    consequences = pd.DataFrame(j["transcript_consequences"])
    consequences["canonical"] = consequences["canonical"].fillna(0).astype(int)
    # rows appear to be sorted by descending sift and/or polyphen score
    first_cols = [
        "gene_symbol",
        "transcript_id",
        "canonical",
        "consequence_terms",
        "impact",
    ]
    # 'polyphen_prediction', 'sift_score', 'polyphen_score'
    other_cols = sorted([i for i in consequences.columns if i not in first_cols])
    consequences = consequences[first_cols + other_cols]

    consequences['consequence_terms'] = consequences['consequence_terms'].map(
        lambda v: ';'.join(v))
    if 'flags' in consequences.columns:
        consequences['flags'] = consequences['flags'].map(
            lambda v: ';'.join(v) if type(v) is list else '.' if pd.isna(v) else v)

    meta = meta.to_frame().T

    colocated = pd.DataFrame()
    if "colocated_variants" in j:
        colocated = pd.DataFrame(j["colocated_variants"])
    return {
        "meta": meta,
        "consequences": consequences,
        "colocated": colocated,
    }


def print_tables(table_dict, width=None):
    if not width:
        width = os.get_terminal_size().columns

    meta = table_dict['meta']
    consequences = table_dict['consequences']
    colocated = table_dict['colocated']
    show_meta_cols = ['assembly_name', 'seq_region_name', 'start', 'end',
                      'allele_string', 'strand', 'most_severe_consequence']
    show_meta = meta[show_meta_cols]  # .rename(columns={'seq_region_name': 'chrom'})

    s = show_meta.iloc[0]
    console = Console(width=width)
    console.print('SUMMARY', style='red bold underline')
    console.print(s.to_string(header=False) + '\n')

    console.print("COLOCATED VARIANTS", style="red bold underline")
    for ind, coloc in colocated.iterrows():
        if 'frequencies' in colocated.columns:
            freq = coloc.pop('frequencies')
        else:
            freq = None

        console.print(coloc.to_string(header=False) + '\n')
        if pd.notnull(freq):
            console.print('\nFREQUENCIES')
            console.print(pd.DataFrame(freq).T.to_string(line_width=width) + '\n')
    if not len(colocated):
        console.print('No colocated variants found.\n')

    console.print('CONSEQUENCES', style='red bold underline')
    skip_conseq_cols = ['gene_symbol_source', 'hgnc_id']
    cq = consequences.copy()
    int_cols = list(cq.convert_dtypes().dtypes.eq('Int64').loc[lambda v: v].index)
    for col in int_cols:
        cq[col] = cq[col].map(lambda v: int(v) if pd.notna(v) else '.')
    for na_col in ['amino_acids', 'polyphen_prediction', 'sift_prediction',
                   'codons', 'polyphen_score']:
        if na_col in cq.columns:
            cq[na_col] = cq[na_col].fillna('.')
    console.print(cq.drop(columns=skip_conseq_cols).to_string(line_width=width))
