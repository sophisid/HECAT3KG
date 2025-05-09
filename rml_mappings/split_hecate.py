import pandas as pd
import os
import sys
import argparse
import subprocess

def split_csv_and_apply_rml_java(csv_file, mapping_file, output_dir, java_mapper_path, chunk_size=100):
    """
    Splits a CSV file into chunks of 100 lines and applies RML mappings using a Java mapper.
    
    Args:
        csv_file (str): Path to the input CSV file
        mapping_file (str): Path to the RML mapping file
        output_dir (str): Directory to store output RDF files
        java_mapper_path (str): Path to the Java RMLMapper jar file
        chunk_size (int): Number of rows per chunk (default 100)
    """
    # Check if Java is installed
    try:
        subprocess.run(["java", "-version"], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        print("Error: Java is not installed or not accessible. Please install Java and ensure it's in your PATH.")
        sys.exit(1)

    # Check if java_mapper_path exists
    if not os.path.exists(java_mapper_path):
        print(f"Error: Java RMLMapper jar file not found at {java_mapper_path}")
        sys.exit(1)

    # Check if mapping file exists
    if not os.path.exists(mapping_file):
        print(f"Error: Mapping file not found at {mapping_file}")
        sys.exit(1)

    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found at {csv_file}")
        sys.exit(1)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"Processing CSV file: {csv_file}")
    csv_basename = os.path.splitext(os.path.basename(csv_file))[0]
    
    # Read CSV in chunks with error handling for encoding
    try:
        chunk_iterator = pd.read_csv(csv_file, chunksize=chunk_size, encoding='utf-8')
    except UnicodeDecodeError:
        print(f"Encoding error with {csv_file}. Trying with 'latin1' encoding.")
        chunk_iterator = pd.read_csv(csv_file, chunksize=chunk_size, encoding='latin1')
    except Exception as e:
        print(f"Error reading CSV file {csv_file}: {str(e)}")
        sys.exit(1)
    
    for i, chunk in enumerate(chunk_iterator):
        # Save chunk to temporary CSV
        temp_csv = os.path.join(output_dir, f"{csv_basename}_chunk_{i}.csv")
        chunk.to_csv(temp_csv, index=False, encoding='utf-8')
        
        # Load RML mapping with error handling for encoding
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping_content = f.read()
        except UnicodeDecodeError:
            print(f"Encoding error with mapping file {mapping_file}. Trying with 'latin1' encoding.")
            with open(mapping_file, 'r', encoding='latin1') as f:
                mapping_content = f.read()
        except Exception as e:
            print(f"Error reading mapping file {mapping_file}: {str(e)}")
            continue
        
        # Update RML mapping to point to temporary CSV
        mapping_content = mapping_content.replace(
            'rr:source "HECATE_v1.1.csv"',
            f'rr:source "{temp_csv}"'
        )
        
        # Save temporary mapping file
        temp_mapping = os.path.join(output_dir, f"{csv_basename}_mapping_{i}.ttl")
        with open(temp_mapping, 'w', encoding='utf-8') as f:
            f.write(mapping_content)
        
        # Execute Java RMLMapper
        try:
            output_file = os.path.join(output_dir, f"{csv_basename}_output_chunk_{i}.rdf")
            command = [
                "java", "-jar", java_mapper_path,
                "-m", temp_mapping,
                "-o", output_file
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print(f"Processed chunk {i} of {csv_basename}, output saved to {output_file}")
            print("RMLMapper output:", result.stdout)
            
        except subprocess.CalledProcessError as e:
            print(f"Error processing chunk {i} of {csv_basename}: {str(e)}")
            print("RMLMapper error output:", e.stderr)
        except Exception as e:
            print(f"Unexpected error processing chunk {i} of {csv_basename}: {str(e)}")
        
        # Clean up temporary files
        if os.path.exists(temp_csv):
            os.remove(temp_csv)
        if os.path.exists(temp_mapping):
            os.remove(temp_mapping)

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Split a CSV file into 100-line chunks and apply RML mappings with Java")
    parser.add_argument('--csv-file', required=True, help="Path to the input CSV file")
    parser.add_argument('--mapping-file', required=True, help="Path to the RML mapping file")
    parser.add_argument('--output-dir', default="output", help="Directory for output files")
    parser.add_argument('--java-mapper', default="../../rmlmapper-7.3.3-r374-all.jar", help="Path to the Java RMLMapper jar file")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the function
    split_csv_and_apply_rml_java(args.csv_file, args.mapping_file, args.output_dir, args.java_mapper)