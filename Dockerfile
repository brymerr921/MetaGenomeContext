# Base Image
FROM continuumio/miniconda3:4.9.2
USER root:root

# Data location
RUN mkdir -p /mnt
WORKDIR /mnt

# Install system-level programs
RUN apt-get --allow-releaseinfo-change update #&& apt-get install -qqy --no-install-suggests --no-install-recommends bc pigz parallel && apt-get clean && apt-get autoclean make gcc build-essential zlib1g-dev libbz2-dev

# Configuring conda channels
RUN conda config --add channels defaults && conda config --add channels bioconda && conda config --add channels conda-forge && conda install -y -c conda-forge mamba awscli boto3

# Install packages
RUN mamba install -c conda-forge -c bioconda -c nodefaults sra-tools pigz pbzip2 snakemake-wrapper-utils snakemake-minimal bbmap spades python==3.9 fasta-splitter prodigal hmmer pyfaidx pandas pyranges
# && conda clean -ay

# COPY . .
# RUN chmod +rx *


# Metadata
LABEL container.maintainer="Bryan Merrill <bmerrill@stanford.edu>" \
      container.base.image="continuumio/miniconda3:4.9.2" \
      container.version="0.0.1" \
      software.name="sra-tools, pigz, pbzip2, snakemake-wrapper-utils, snakemake-minimal, bbmap, spades, python==3.9, fasta-splitter, prodigal, hmmer, pyfaidx, pandas, pyranges"
