#!/bin/bash


export accession=ERR1136736
export coreNum=12
export mem_mb=64000
export mem_gb=64
export pfam=PF00009
export interval=5000

# The wrapper version of metaspades won't utilize all threads 
# unless this variable is set:
export OMP_NUM_THREADS=$coreNum

echo "Num threads == $OMP_NUM_THREADS"

snakemake -p -j $coreNum --resources mem_mb=$mem_mb -s /home/bmerrill/user_data/Projects/github_projects/MetaGenomeContext/Snakefile_MGC --config accession=$accession all_cpu=$coreNum mem_gb=$mem_gb skip_ec='--only-assembler' pfam=$pfam interval=$interval --configfile /home/bmerrill/user_data/Projects/github_projects/MetaGenomeContext/config.yaml #-n --debug-dag

