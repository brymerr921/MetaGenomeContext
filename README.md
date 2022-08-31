# MetaGenomeContext
This pipeline can be used to assemble metagenomes and extract contigs containing a protein with a specific function, as well as surrounding genes.

## Running on a local machine

### Setup
To run on a local machine, set up the following conda environment:
```
conda create -n mgc -c conda-forge -c bioconda -c nodefaults \
     sra-tools pigz pbzip2 snakemake-wrapper-utils snakemake-minimal \
     bbmap spades python==3.9 fasta-splitter prodigal hmmer pyfaidx \
     pandas pyranges
```

Next, clone this github repo somewhere on your machine using the following command:  
```
git clone https://github.com/brymerr921/MetaGenomeContext.git
```

### Execution
From here, we can set a few bash variables specifying our input parameters and then run the program.  
```
# Specify which SRR or ERR run you'd like to download -- must be paired-end reads!
export accession=ERR1136736

# Specify how many CPUs you have available
export coreNum=12

# Specify how much RAM you have available (in megabytes and gigabytes)
export mem_mb=64000
export mem_gb=64

# Specify which PFAM you'd like to analyze
export pfam=PF00009

# Specify the interval you'd like to use for genomic context 
# up/downstream of a target gene
export interval=5000

# Specify the path to the output directory
export outdir=outdir

# Specify the path to this repo
export repo_path=/home/bmerrill/user_data/Projects/github_projects/MetaGenomeContext

# Activate your conda environment
conda activate mgc 

# Run the workflow
snakemake -p -j $coreNum --resources mem_mb=$mem_mb \
  -s ${repo_path%/}/scripts/Snakefile_MGC --config accession=$accession \
  all_cpu=$coreNum mem_gb=$mem_gb skip_ec='--only-assembler' \
  pfam=$pfam interval=$interval outdir=${outdir%/}/ \
  scripts=${repo_path%/}/scripts \
  --configfile ${repo_path%/}/scripts/config.yaml #-n --debug-dag
```
You can remove the comment from the `snakemake` command to do a dry run (`-n`) and provide extra context why something isn't working (`--debug-dag`).  
  
  
## Running on AWS
To run on AWS, assuming `awscli` and `aegea` are installed, we just need to generate a submit command. Here's an example one:  
```
echo "Submitting ERR1136736 and PF00009 ..." 2>&1 | tee -a AEGEA.log
aegea batch submit --queue sonn --retry-attempts 3 \
  --image bmerrill9/metagenomecontext:latest --storage /mnt=500 \
  --vcpus 16 --memory 64000 \
  --command="export coreNum=16; export mem_mb=64000; \
      export accession=ERR1136736; export pfam=PF00009; \
      export interval=10000; \
      export DATA_DEST=s3://sonn-current/users/bmerrill/220831_mgc_testing/round1; \
      ./mgc_wrapper.sh" 2>&1 >> AEGEA.log
```
This will place exported files in the path specified by `DATA_DEST`.  
You can see the expected output below.  
  
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

## Caveats
There are several caveats/considerations regarding this workflow.  
  1. Though only currently designed to take in a single `pfam`, some code is in place to provide more than one.  
  2. Designing a useful output required some concessions to be made. One of these is that proteins containing target pfam domains might lie within `interval` base pairs of each other. One option would be to generate a `.faa` and `.gff` file for each protein and its genomic neighbors regardless of proximity. However, in favor of a simpler output, when two proteins lie within `interval` base pairs of each other, the intervals are merged, and only one is reported.  
  3. This pipeline utilizes Snakemake within a Docker image that contains all dependencies. Files are generated within the Docker image, and in this case, copied to aws s3 before the container and ec2 instance are shut down. Another way to run this would be to containerize each Snakemake rule and point at cloud storage paths, rather than local storage paths. Using Snakemake in this way would improve portability.  
  4. To facilitate computing these intervals I used the `pyranges` and `pandas` packages. However, these steps as currently implemented are *very* slow, especially for large assemblies, and would greatly benefit from parallelization or more efficient use of these packages. One solution within Snakemake might be to run the `identify_intervals` rule on the split files, rather than running it after the `combine_files` rule.  
  5. Output size could also be reduced by only outputting intervals with at least *n* genes. Right now, single-gene contigs containing a pfam domain of interest are output.  
  6. A single, aggregated table would also be useful. This could be generated by aggregating all of the `interval_*.gff` files.  
  7. Many output files could be gzipped to reduce size.  
