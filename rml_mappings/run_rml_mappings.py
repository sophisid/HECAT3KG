import os
import subprocess

csv_dir = "./split_csvs"
rml_file = "updated_parsec_mapping.ttl"
output_dir = "./output_rdf"
temp_rml = "temp_mapping.ttl"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

with open(rml_file, "r") as f:
    rml_template = f.read()

for csv_file in os.listdir(csv_dir):
    if csv_file.endswith(".csv"):
        csv_path = f"{csv_dir}/{csv_file}"
        with open(temp_rml, "w") as f:
            f.write(rml_template.replace('rml:source "CURRENT_CSV"', f'rml:source "{csv_path}"'))
        
        output_file = f"{output_dir}/{csv_file.replace('.csv', '.ttl')}"
        
        result = subprocess.run(
            ["java", "-jar", "../../rmlmapper-7.3.3-r374-all.jar", "-m", temp_rml, "-o", output_file],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print(f"Processed {csv_file} -> {output_file}")
        else:
            print(f"Error processing {csv_file}: {result.stderr}")
        
        os.remove(temp_rml)