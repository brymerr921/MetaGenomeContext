# MetaGenomeContext
This pipeline can be used to assemble metagenomes and extract contigs containing a protein with a specific function, as well as surrounding genes.

## Running on a local machine

### Setup
To run on a local machine, set up the following conda environment:
```
conda create -n mgc -c conda-forge -c bioconda -c nodefaults sra-tools pigz pbzip2 snakemake-wrapper-utils snakemake-minimal bbmap spades python==3.9 fasta-splitter prodigal hmmer pyfaidx pandas pyranges
```

Next, clone this github repo somewhere on your machine using the following command:  
```
git clone https://github.com/brymerr921/MetaGenomeContext.git
```

### Execution
From here, we can set a few bash variables specifying our input parameters and then run the program.  
```
# Specify which SRR or ERR run you'd like to download -- must be paired-end reads
export accession=ERR1136736

# Specify how many CPUs you have available
export coreNum=12

# Specify how much RAM you have available (in megabytes and gigabytes)
export mem_mb=64000
export mem_gb=64

# Specify which PFAM you'd like to analyze
export pfam=PF00009

# Specify the interval you'd like to use for genomic context up/downstream of a target gene
export interval=5000

# Specify the path to the output directory
export outdir=outdir

# Specify the path to this repo
export repo_path=/home/bmerrill/user_data/Projects/github_projects/MetaGenomeContext

# Activate your conda environment
conda activate mgc 

# Run the workflow
snakemake -p -j $coreNum --resources mem_mb=$mem_mb -s ${repo_path%/}/scripts/Snakefile_MGC --config accession=$accession all_cpu=$coreNum mem_gb=$mem_gb skip_ec='--only-assembler' pfam=$pfam interval=$interval outdir=${outdir%/}/ scripts=${repo_path%/}/scripts --configfile ${repo_path%/}/scripts/config.yaml #-n --debug-dag
```

## Running on AWS


## Expected outputs
Your `outdir` directory should contain the following folders upon successful completion of the workflow.
```
.
└── ERR1136736
    ├── 00_LOGS
    ├── 02_TRIMMED
    ├── 03_ASSEMBLY
    ├── 04_ANNOTATION
    ├── 05_INTERVALS
    ├── hmms
    └── split
```

Contents of `00_LOGS`:  
This contains stdout/stderr from a few of the Snakemake rules.  
```
00_LOGS/
├── 01__get_fastq.ERR1136736.log
├── 02__adapter_and_quality_trim.ERR1136736.log
├── 03__metaspades.ERR1136736.log
├── 04__split_files.ERR1136736.log
└── ERR1136736.done
```

`01_FASTQC` is not generated yet, but this directory will eventually hold FASTQC outputs on reads before/after trimming.  

Contents of `02_TRIMMED`:  
Forward and reverse reads folloiwng processing by `bbduk.sh` as part of the workflow.  
```
02_TRIMMED/
├── QC_ERR1136736_R1.fastq.gz
└── QC_ERR1136736_R2.fastq.gz
```

Contents of `03_ASSEMBLY`:  
Here you'll find the default metaSPAdes outputs, as well as these `METASPADES_` files, where contig/scaffold names have been prefixed with `ERR1136736__`.
```
03_ASSEMBLY/
├── ...
├── K21
├── K33
├── K55
├── METASPADES_ERR1136736.contigs.fasta
├── METASPADES_ERR1136736.scaffolds.fasta
├── ...
```

Contents of `04_ANNOTATION`:  
Here you'll find the Prodigal-generated `.faa` and `gff` files containing proteins and gene calls from the entire metagenome assembly. You'll also find a `.txt` and `.tsv` file from the raw and parsed `hmmsearch` output.  
```
04_ANNOTATION/
├── METASPADES_ERR1136736.scaffolds.faa
├── METASPADES_ERR1136736.scaffolds.faa.fai
├── METASPADES_ERR1136736.scaffolds.gff
├── METASPADES_ERR1136736.scaffolds.PF00009.tsv
└── METASPADES_ERR1136736.scaffolds.PF00009.txt
```

Contents of `05_INTERVALS`:  
Here you'll find one `.faa` and one `.gff` for each interval identified. An interval consists of one or more proteins with a PFAM domain of interest, as well as genes that fall within +/- *n* base pairs on either side of the protein(s) of interest.  
```
├── interval_1.faa
├── interval_1.gff
├── interval_2.faa
├── interval_2.gff
├── ...
```

