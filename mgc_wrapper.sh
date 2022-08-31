#!/bin/bash -x

set -euo pipefail

START_TIME=$SECONDS

LOCAL=$(pwd)

# The next two lines are necessary because there are two different /mnt locations
# Without this odd copy step, Snakemake fails (other things do too).
cp -pr * $LOCAL/
cd $LOCAL

export PATH="/opt/conda/bin:${PATH}"

# Optional variables
coreNum=${coreNum:-8}
snakefile=${snakefile:-scripts/Snakefile_MGC}
config=${config:-scripts/config.yaml}
mem_mb=${mem_mb:-32000}
mem_gb=$(( $mem_mb / 1024 ))
interval=${interval:-5000}

# Required variables
#   accession
#   pfam
DATA_DEST=${DATA_DEST%/}

snakemake -p -j $coreNum --resources mem_mb=$mem_mb -s $snakefile \
  --config accession=$accession all_cpu=$coreNum mem_gb=$mem_gb \
      skip_ec='--only-assembler' pfam=$pfam interval=$interval outdir=outdir/ \
      scripts=scripts --configfile $config -n --debug-dag

cp LATEST outdir/$accession/00_LOGS/VERSION__metagenomecontext

echo "Syncing data back to S3 ..."
aws s3 sync outdir/ ${DATA_DEST}/

echo "File transfer complete. Pipeline has finished."
