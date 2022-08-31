#!/usr/bin/env python

import os
import pathlib
import numpy as np
import pandas as pd
import pyranges as pr
from pyfaidx import Fasta
from collections import defaultdict


def import_gff(gff):
    gr = pr.readers.read_gff3(gff, full=True, as_df=False)
    return gr

def tsv_to_dict(tsv):
    pfam_dict = defaultdict(set)
    with open(tsv) as h:
        line = h.readline()
        line = h.readline()
        while line != "":
            line = line.strip().split('\t')
            pfam_dict[line[0]].add(line[4])
            line = h.readline()
    for key in pfam_dict:
        pfam_dict[key] = ','.join(list(pfam_dict[key]))

    pfam_df = pd.DataFrame(list(pfam_dict.items()),columns = ['ID','pfams'])
    
    return pfam_dict, pfam_df

# def join_pfams(gr, pfam_dict):
#     pfam_df = pd.DataFrame(list(pfam_dict.items()),columns = ['ID','pfams'])
#     gr_j = pr.PyRanges(pd.merge(gr.df, pfam_df, how="left"))
#     return gr_j

def add_to_ends(df, **kwargs):
    df.loc[:, "End"] = kwargs["slack"] + df.End
    df.loc[:, "Start"] = df.Start - kwargs["slack"]
    return df

def gen_intervals_df(gr_j, pfam_dict):
    s = gr_j[gr_j.ID.isin(pfam_dict.keys())]
    s_add = s.apply(add_to_ends, slack=10000).merge()
    return s_add

def gen_intervals_output(gr, s_add, outdir, interval, genes, pfam_df):
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    int_num = 1
    for i, j in s_add.df.iterrows():
        chrm = str(j[['Chromosome']][0])
        start = int(j[['Start']][0])
        end = int(j[['End']][0])
        print("chrm: {0}, start: {1}, end: {2}".format(chrm, start, end))
        out_path = os.path.join(outdir,"interval_{0}.gff".format(int_num))
        df_out = gr[chrm, start:end]
        df_out_j = pd.merge(df_out.df, pfam_df, how="left")
        with open(out_path.replace('gff','faa'),'w') as faa_out:
            for gene in list(df_out.ID):
                faa_out.write(">{0}\n".format(genes[gene][:].name))
                faa_out.write("{0}\n".format(genes[gene][:].seq))
        df_out.to_gff3(out_path)
        int_num += 1
        
if __name__ == "__main__":
    import argparse
    import pathlib
    usage = """%(prog)s identifies genes matching an hmm model (e.g. PFAM) 
               and returns that protein with associated genomic context (e.g. 
               all genes within # basepairs of a protein with a PFAM hit).  
               Required input includes: 
               - gff and faa file generated using Prodigal on a metagenome assembly 
               - hmmsearch domtblout file parsed to be tab-separated 
               - output directory (generates one subsetted gff and faa per interval) 
               - interval size (in base pairs)"""

    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("-g", "--gff", dest="gff",
                        help="path to gff file generated using Prodigal on a \
                        metagenome assembly", type=str, required=True)
    parser.add_argument("-a", "--faa", dest="faa",
                        help="path to faa file generated using Prodigal on a \
                        metagenome assembly", type=str, required=True)
    parser.add_argument("-t", "--tsv", dest="tsv",
                        help="path to hmmsearch domtblout file parsed to be \
                        tab-separated", type=str, required=True)
    parser.add_argument("-o", "--outdir", help="Output directory for interval files",
                        type=str, required=True)
    parser.add_argument("-i", "--interval", dest="interval",
                         help="The # of basepairs upstream and downstream of a \
                         protein that has a hit in the provided tsv. \
                         For example, -i 5000 will provide 10000 bp of genomic \
                         context for a given protein, with 5000 before and after.\
                         default: 5000", type=int, default=5000)

    args = parser.parse_args()

    print("Import gff as pyranges")
    gr = import_gff(args.gff)

    print("Import tsv")
    pfam_dict, pfam_df = tsv_to_dict(args.tsv)

    # print("Joining pfam functions to pyranges")
    # gr_j = join_pfams(gr, pfam_dict)

    print("Generating interval ranges dataframe")
    s_add = gen_intervals_df(gr, pfam_dict)

    print("Import faa file for rapid subsetting")
    genes = Fasta(args.faa)

    print("Generating gff and faa files for each interval")
    gen_intervals_output(gr, s_add, args.outdir, args.interval, genes, pfam_df)

    print("Done!")
