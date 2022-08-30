# MetaGenomeContext
This pipeline can be used to assemble metagenomes and extract contigs containing a protein with a specific function, as well as surrounding genes.

## Setup
To run on a local machine, set up the following conda environment:
```
conda create -n mgc -c conda-forge -c bioconda -c nodefaults sra-tools pigz pbzip2 snakemake-wrapper-utils snakemake-minimal bbmap spades python==3.9 fasta-splitter prodigal
```