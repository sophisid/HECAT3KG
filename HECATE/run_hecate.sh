#!/bin/bash

for i in {1..20474}
do
    input_file="../HECATE_columns_part${i}.xml"
    output_file="../HECATE_part${i}.trig"
    
    echo "Processing $input_file to $output_file..."
    
    java -Xms10g -Xmx14g -jar ../../x3ml/target/x3ml-engine-2.2.2-SNAPSHOT-exejar.jar \
        --input "$input_file" \
        --x3ml mappings_v2/columns.x3ml \
        --policy mappings_v2/generator-policies.xml \
        --output "$output_file" \
        --format application/trig \
        --reportProgress
    
    if [ $? -eq 0 ]; then
        echo "Successfully processed $input_file to $output_file"
    else
        echo "Error processing $input_file"
    fi
done