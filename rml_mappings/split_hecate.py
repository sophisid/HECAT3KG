import pandas as pd
import os

input_file = "../HECATE_v1.1.csv"
output_dir = "./split_csvs"
chunk_size = 1000

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for i, chunk in enumerate(pd.read_csv(input_file, chunksize=chunk_size)):
    output_file = f"{output_dir}/HECATE_v1.1_part_{i+1}.csv"
    chunk.to_csv(output_file, index=False)
    print(f"Created {output_file}")