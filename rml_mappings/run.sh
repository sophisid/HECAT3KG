#!/bin/bash

CSV_FILE="../HECATE_v1.1.csv"
CHUNK_SIZE=100
MAPPING_TEMPLATE="./updated_parsec_mapping.ttl"
OUTPUT_DIR="outputs"
TEMP_DIR="temp_chunks"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$TEMP_DIR"

# Get header
HEADER=$(head -n 1 "$CSV_FILE")

# Count total lines (excluding header)
TOTAL_LINES=$(tail -n +2 "$CSV_FILE" | wc -l)
CHUNKS=$(( (TOTAL_LINES + CHUNK_SIZE - 1) / CHUNK_SIZE ))

for ((i=0; i<CHUNKS; i++)); do
    START_LINE=$((i * CHUNK_SIZE + 2))  # +2 to skip header
    END_LINE=$((START_LINE + CHUNK_SIZE - 1))
    CHUNK_FILE="$TEMP_DIR/chunk_$i.csv"

    # Write header and chunk lines
    echo "$HEADER" > "$CHUNK_FILE"
    sed -n "${START_LINE},${END_LINE}p" "$CSV_FILE" >> "$CHUNK_FILE"

    # Create mapping file for this chunk
    MAPPING_FILE="$TEMP_DIR/mapping_chunk_$i.rml.ttl"
    sed "s|{{CSV_PATH}}|$CHUNK_FILE|g" "$MAPPING_TEMPLATE" > "$MAPPING_FILE"

    echo "Running mapping for chunk $i..."
    java -jar ../../rmlmapper-7.3.3-r374-all.jar -m "$MAPPING_FILE" -o "$OUTPUT_DIR/output_$i.ttl" -s turtle
done

echo "✅ All chunks processed."
