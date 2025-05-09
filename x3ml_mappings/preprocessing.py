import xml.etree.ElementTree as ET
import pandas as pd
import math
import argparse
from xml.etree.ElementTree import Element, tostring
import xml.sax.saxutils as saxutils

def prettify_xml(element, indent="  "):
    """Formats the XML output to be more readable."""
    queue = [(0, element)]
    while queue:
        level, elem = queue.pop(0)
        children = list(elem)
        if children:
            elem.text = "\n" + (indent * (level + 1))
        if queue:
            elem.tail = "\n" + (indent * queue[0][0])
        else:
            elem.tail = "\n"
        for child in reversed(children):
            queue.insert(0, (level + 1, child))

def map_flag_values(record):
    """Maps flag values directly onto their respective fields in the record."""
    flag_2mass_map = {"0": "none", "1": "LGA", "2": "XSC", "3": "PSC"}
    class_sp_map = {"0": "star-forming", "1": "Seyfert", "2": "LINER", "3": "composite", "-1": "unknown"}
    flag_metal_map = {"-1": "missing", "0": "reliable", "1": "O3N2 ratio >2 (outside PP04 range)", "2": "low signal-to-noise ratio (<3 for weakest line)"}
    q_label_map = {"0": "not in IRAS", "1": "upper limit", "2": "moderate", "3": "high", "4": "flux from IRAS-RBGS"}
    dmethod_map = {
        "N": "using NED-D distance measurements", "Z": "regression",
        "Zv": "regression for Virgo Cluster members",
        "C": "distance from NED-D measurements but uncertainty from regression",
        "Cv": "distance from NED-D measurements but uncertainty from Virgo Cluster regressor"
    }
    edist_map = {"0": "measurement does not contain uncertainties", "1": "measurement contains uncertainties"}
    rflag_map = {"1": "Reliable", "2": "R2 set same as R1 (circular isophote treatment)"}
    rsource_map = {
        "H": "HyperLEDA", "S": "SDSS", "2": "2MASS", "6": "2dFGS", "W": "WINGS", "Y": "SkyMapper",
        "A": "Amiga-CIG", "K": "UNGC", "V": "VIII/77", "1": "KKH2001", "7": "KKH2007", "N": "NED"
    }

    if 'FLAG_2MASS' in record and record['FLAG_2MASS'] is not None:
        record['FLAG_2MASS'] = flag_2mass_map.get(record['FLAG_2MASS'], record['FLAG_2MASS'])
    
    if 'CLASS_SP' in record and record['CLASS_SP'] is not None:
        record['CLASS_SP'] = class_sp_map.get(record['CLASS_SP'], record['CLASS_SP'])
    
    if 'FLAG_METAL' in record and record['FLAG_METAL'] is not None:
        record['FLAG_METAL'] = flag_metal_map.get(record['FLAG_METAL'], record['FLAG_METAL'])
    
    for q_field, s_field in [('Q12', 'S12'), ('Q25', 'S25'), ('Q60', 'S60'), ('Q100', 'S100')]:
        if q_field in record and record[q_field] is not None:
            q_label = q_label_map.get(str(record[q_field]), record[q_field])
            if q_label == "not in IRAS" and (s_field not in record or record[s_field] in [None, "", "-"]):
                del record[q_field]  # Remove if "not in IRAS" and SXX is absent or null
            else:
                record[q_field] = q_label

    if 'DMETHOD' in record and record['DMETHOD'] is not None:
        record['DMETHOD'] = dmethod_map.get(record['DMETHOD'], record['DMETHOD'])
    
    if 'EDIST' in record and record['EDIST'] is not None:
        record['EDIST'] = edist_map.get(record['EDIST'], record['EDIST'])
    
    if 'RFLAG' in record and record['RFLAG'] is not None:
        record['RFLAG'] = rflag_map.get(record['RFLAG'], record['RFLAG'])

    if 'RSOURCE' in record and record['RSOURCE'] is not None:
        record['RSOURCE'] = rsource_map.get(record['RSOURCE'], record['RSOURCE'])

    if 'F_ASTROM' in record and record['F_ASTROM'] is not None:
        try:
            flag_value = int(record['F_ASTROM'])
            record['F_ASTROM'] = 2.78 * 10 ** (-4 + flag_value)
        except ValueError:
            record['F_ASTROM'] = None

def process_row_to_xml(row, idx):
    """Converts a single row to an XML element."""
    row_element = Element("row")

    row_number_element = ET.SubElement(row_element, "ROW_NUMBER")
    row_number_element.text = f"galaxy_{idx}"

    # Identifiers
    identifier_fields = {'PGC', 'OBJNAME', 'ID_NED', 'ID_NEDD', 'ID_IRAS', 'ID_2MASS', 'SDSS_PHOTID', 'SDSS_SPECID'}
    error_fields = {col for col in row.keys() if col.startswith("E_")}
    ci_fields = {"D_LO68", "D_HI68", "D_LO95", "D_HI95"}
    
    identifiers_present = {key: row[key] for key in identifier_fields if key in row and pd.notna(row[key])}
    if identifiers_present:
        id_element = ET.SubElement(row_element, "identifiers")
        for key, value in identifiers_present.items():
            field = ET.SubElement(id_element, key)
            field.text = str(value)

    # Degrees Grouping (excluding F_ASTROM)
    degrees_fields = {'RA', 'DEC'}
    degrees_present = {key: row[key] for key in degrees_fields if key in row and pd.notna(row[key])}
    if degrees_present:
        degrees_element = ET.SubElement(row_element, "degrees")
        for key, value in degrees_present.items():
            field = ET.SubElement(degrees_element, key)
            field.text = str(value)

    # Rotation Grouping (excluding RSOURCE, RFLAG)
    rotation_fields = {'R1', 'R2', 'PA'}
    rotation_present = {key: row[key] for key in rotation_fields if key in row and pd.notna(row[key])}
    if rotation_present:
        rotation_element = ET.SubElement(row_element, "rotation")
        for key, value in rotation_present.items():
            field = ET.SubElement(rotation_element, key)
            field.text = str(value)

    # Errors
    errors_present = {}
    for error_key in error_fields:
        main_key = error_key[2:]
        if main_key in row and pd.notna(row[main_key]):
            errors_present[main_key] = (row[main_key], row[error_key])

    if errors_present:
        errors_element = ET.SubElement(row_element, "errors")
        for main_key, (main_value, error_value) in errors_present.items():
            error_entry = ET.SubElement(errors_element, "error")
            column_element = ET.SubElement(error_entry, "column")
            ET.SubElement(column_element, main_key).text = str(main_value)
            error_column_element = ET.SubElement(error_entry, "error_column")
            ET.SubElement(error_column_element, "E_" + main_key).text = str(error_value)

    # Confidence Intervals with DMETHOD
    ci_present = {key: row[key] for key in ci_fields if key in row and pd.notna(row[key])}
    if ci_present and "D" in row and pd.notna(row["D"]):
        ci_element = ET.SubElement(row_element, "confidence_intervals")
        ci_error_element = ET.SubElement(ci_element, "CI_error")

        column_element = ET.SubElement(ci_error_element, "column")
        ET.SubElement(column_element, "D").text = str(row["D"])

        if "DMETHOD" in row and pd.notna(row["DMETHOD"]):
            dmethod_element = ET.SubElement(ci_error_element, "DMETHOD")
            dmethod_element.text = str(row["DMETHOD"])

        lower_bound_element = ET.SubElement(ci_error_element, "lower_bound")
        if "D_LO68" in ci_present:
            ET.SubElement(lower_bound_element, "D_LO68").text = str(row["D_LO68"])
        if "D_LO95" in ci_present:
            ET.SubElement(lower_bound_element, "D_LO95").text = str(row["D_LO95"])

        upper_bound_element = ET.SubElement(ci_error_element, "upper_bound")
        if "D_HI68" in ci_present:
            ET.SubElement(upper_bound_element, "D_HI68").text = str(row["D_HI68"])
        if "D_HI95" in ci_present:
            ET.SubElement(upper_bound_element, "D_HI95").text = str(row["D_HI95"])

    # Direct children of <row>: FLAG_2MASS, CLASS_SP, F_ASTROM, RSOURCE, RFLAG
    if "FLAG_2MASS" in row and pd.notna(row["FLAG_2MASS"]):
        flag_2mass_element = ET.SubElement(row_element, "FLAG_2MASS")
        flag_2mass_element.text = str(row["FLAG_2MASS"])

    if "CLASS_SP" in row and pd.notna(row["CLASS_SP"]):
        class_sp_element = ET.SubElement(row_element, "CLASS_SP")
        class_sp_element.text = str(row["CLASS_SP"])

    if "F_ASTROM" in row and pd.notna(row["F_ASTROM"]):
        fastrom_element = ET.SubElement(row_element, "F_ASTROM")
        fastrom_element.text = str(row["F_ASTROM"])

    if "RSOURCE" in row and pd.notna(row["RSOURCE"]):
        rsource_element = ET.SubElement(row_element, "RSOURCE")
        rsource_element.text = str(row["RSOURCE"])

    if "RFLAG" in row and pd.notna(row["RFLAG"]):
        rflag_element = ET.SubElement(row_element, "RFLAG")
        rflag_element.text = str(row["RFLAG"])

    # Metal Grouping: Only create if METAL exists and is non-empty
    if "METAL" in row and pd.notna(row["METAL"]) and str(row["METAL"]).strip() not in ["", "-"]:
        metal_element = ET.SubElement(row_element, "metal")
        value_element = ET.SubElement(metal_element, "value")
        value_element.text = str(row["METAL"])
        if "FLAG_METAL" in row and pd.notna(row["FLAG_METAL"]) and str(row["FLAG_METAL"]).strip() not in ["", "-"]:
            flag_metal_element = ET.SubElement(metal_element, "FLAG_METAL")
            flag_metal_element.text = str(row["FLAG_METAL"])

    # Flux Grouping: Always include <s> and <q>
    flux_pairs = [('Q12', 'S12'), ('Q25', 'S25'), ('Q60', 'S60'), ('Q100', 'S100')]
    for q_key, s_key in flux_pairs:
        flux_element = ET.SubElement(row_element, "flux")
        number = q_key[1:]  # Extract number (e.g., "12" from "Q12")
        number_element = ET.SubElement(flux_element, "number")
        number_element.text = number
        
        s_element = ET.SubElement(flux_element, "S")
        s_value = str(row[s_key]) if s_key in row and pd.notna(row[s_key]) else "N/A"
        s_element.text = s_value
        
        q_element = ET.SubElement(flux_element, "Q")
        q_value = str(row[q_key]) if q_key in row and pd.notna(row[q_key]) else "N/A"
        q_element.text = q_value

    # Dist Grouping
    dist_fields = {'EDIST', 'NDIST'}
    dist_present = {key: row[key] for key in dist_fields if key in row and pd.notna(row[key])}
    if dist_present:
        dist_element = ET.SubElement(row_element, "DIST")
        for key, value in dist_present.items():
            field = ET.SubElement(dist_element, key)
            field.text = str(value)

    # General columns: Manually specify fields to include in <gen>
    gen_fields = {
        'INCL', 'AG', 'AI', 'WFPOINT', 'WFTREAT', 'logL_K', 'logM_HEC', 'AGN_S17', 'AGN_HEC',
        'logL_TIR', 'logL_FIR', 'logL_60u', 'logL_12u', 'logL_22u', 'ML_RATIO',
        'logSFR_TIR', 'logSFR_FIR', 'logSFR_60u', 'logSFR_12u', 'logSFR_22u', 'logSFR_HEC',
        'FLAG_SFR_HEC', 'logSFR_GSW', 'logM_GSW', 'MIN_SNR'
    }
    gen_present = {key: row[key] for key in gen_fields if key in row and pd.notna(row[key])}

    if gen_present:
        gen_element = ET.SubElement(row_element, "gen")
        for key, value in gen_present.items():
            field = ET.SubElement(gen_element, key)
            field.text = str(value)

    return row_element

def process_csv_in_chunks(csv_path, chunk_size, base_output_xml):
    """
    Process the CSV in chunks and save each chunk to separate XML files using streaming.
    """
    chunk_number = 1
    for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
        print(f"Processing chunk {chunk_number} with {len(chunk)} rows...")
        
        # Define file name for this chunk
        output_xml = f"{base_output_xml}_part{chunk_number}.xml"
        
        # Process the chunk directly and write to XML in a streaming fashion
        with open(output_xml, 'wb') as f:
            # Write XML declaration and root opening tag
            f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(b'<root>\n')
            
            # Process each row in the chunk
            idx = (chunk_number - 1) * chunk_size + 1
            for _, row in chunk.iterrows():
                # Convert row to dictionary and apply transformations
                record = row.to_dict()
                map_flag_values(record)
                
                # Convert numeric data
                for key in ['RA', 'DEC', 'V', 'E_V', 'D', 'E_D']:
                    if key in record and pd.notna(record[key]):
                        try:
                            record[key] = float(record[key])
                        except ValueError:
                            record[key] = None
                
                # Convert the row to XML element
                row_element = process_row_to_xml(record, idx)
                
                # Write the row to the file with proper indentation
                row_str = tostring(row_element, encoding='utf-8').decode('utf-8')
                indented_row = '  ' + row_str.replace('\n', '\n  ') + '\n'
                f.write(indented_row.encode('utf-8'))
                
                idx += 1
            
            # Write root closing tag
            f.write(b'</root>\n')
        
        print(f"Processed XML saved to {output_xml}")
        chunk_number += 1

def main():
    # Ορισμός command-line arguments
    parser = argparse.ArgumentParser(description="Preprocess CSV to XML in chunks with streaming.")
    parser.add_argument('--csv', type=str, default="../HECATE_v1.1.csv", help="Path to the input CSV file")
    parser.add_argument('--chunk_size', type=int, default=50000, help="Number of rows per chunk (default: 50000)")
    parser.add_argument('--base_output_xml', type=str, default="../HECATE_columns", help="Base name for output XML files")

    args = parser.parse_args()

    # Paths and chunk size
    csv_path = args.csv
    chunk_size = args.chunk_size
    base_output_xml = args.base_output_xml

    # Process the CSV in chunks
    process_csv_in_chunks(csv_path, chunk_size, base_output_xml)

if __name__ == "__main__":
    main()