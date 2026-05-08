#!/bin/bash

bakta_db download --output /beegfs/lvsea/bakta_db/ --type light

for genome in /beegfs/lvsea/mags_download/*.fna.gz; do
    sample_name=$(basename "$genome" .fna.gz)
output_dir="${sample_name}_annot"

if [ -f "$output_dir/${sample_name}.gff3" ]; then
        echo "Skipping $sample_name - already processed" >&2
        continue
fi


bakta \
    --db /beegfs/lvsea/bakta_db/db-light \
    --output "$output_dir" \
    --prefix "${sample_name}" \
    --threads 8 \
    --meta \
    --min-contig-length 200 \
    --keep-contig-headers \
    --verbose \
    "$genome" 

    sleep 2
done

