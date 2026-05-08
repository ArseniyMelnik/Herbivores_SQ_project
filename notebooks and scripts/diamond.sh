#!/bin/bash

PROJECT_DIR="/home/herbivores"
ANNOT_DIR="$PROJECT_DIR/bakta_annotations"
OUT_DIR="$PROJECT_DIR/diamond_after_bakta"
QUERY_FAA="/data/sq_enzymes.faa"

mkdir -p "$OUT_DIR"

# collect all faa files from all subfolders into one compressed file, add the genome number to the protein headers
find "$ANNOT_DIR" -name "*.faa" -type f -exec sh -c '
    genome=$(basename "$1" .faa)
    sed "s/^>/>${genome}_/" "$1"
' _ {} \; | gzip > "$OUT_DIR/all_proteins.faa.gz"

cd "$OUT_DIR"

gunzip -c all_proteins.faa.gz | diamond makedb --in - -d diamond_db --threads 8

diamond blastp \
  -d diamond_db.dmnd \
  -q "$QUERY_FAA" \
  -o sq_hits.tsv \
  --ultra-sensitive \
  --outfmt 6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore \
  --evalue 1e-3 \
  --id 20 \
  --query-cover 30 \
  --subject-cover 30 \
  --max-target-seqs 10000 \
  --threads 8


# select unique matches
sort -k2,2 -k12,12nr sq_hits.tsv | awk '!seen[$2]++' > unique_sq_best_hits.tsv

