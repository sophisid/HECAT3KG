import xml.etree.ElementTree as ET
import pandas as pd
import math

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

    # Directly replace values instead of creating new nodes
    if 'FLAG_2MASS' in record and record['FLAG_2MASS'] is not None:
        record['FLAG_2MASS'] = flag_2mass_map.get(record['FLAG_2MASS'], record['FLAG_2MASS'])
    
    if 'CLASS_SP' in record and record['CLASS_SP'] is not None:
        record['CLASS_SP'] = class_sp_map.get(record['CLASS_SP'], record['CLASS_SP'])
    
    if 'FLAG_METAL' in record and record['FLAG_METAL'] is not None:
        record['FLAG_METAL'] = flag_metal_map.get(record['FLAG_METAL'], record['FLAG_METAL'])
    
    for q_field, s_field in [('Q12', 'S12'), ('Q25', 'S25'), ('Q60', 'S60'), ('Q100', 'S100')]:
        if q_field in record and record[q_field] is not None:
            if s_field in record and record[s_field] not in [None, "", "-"]:
                q_label = q_label_map.get(record[q_field], record[q_field])
                if q_label != "not in IRAS":
                    record[q_field] = q_label
                else:
                    del record[q_field]  # Remove it if it's "not in IRAS"

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

def group_errors(record):
    """Groups error columns under an <errors> tag, pairing each value with its corresponding error column."""
    errors = []

    for key, value in record.items():
        if key.startswith("E_"):
            main_key = key[2:]  # main column name
            if main_key in record:
                errors.append((main_key, key, record[main_key], value))

    return errors if errors else None

def csv_to_xml(csv_file, xml_file):
    df = pd.read_csv(csv_file)
    root = ET.Element("root")
    
    for _, row in df.iterrows():
        row_element = ET.SubElement(root, "row")
        for col_name, value in row.items():
            if pd.notna(value):  # Remove empty tags
                field = ET.SubElement(row_element, col_name)
                field.text = str(value)
    
    prettify_xml(root)
    tree = ET.ElementTree(root)
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)
    print(f"Converted CSV to XML: {xml_file}")


def parse_xml(xml_file):
    records = []
    
    for event, elem in ET.iterparse(xml_file, events=("start", "end")):
        if event == "end" and elem.tag == "row":
            record = {child.tag: child.text for child in elem if child.text and child.text.strip() != "-"}
            
            # Αντιστοίχιση flags και υπολογισμοί
            map_flag_values(record)

            # Μετατροπή αριθμητικών δεδομένων
            for key in ['RA', 'DEC', 'V', 'E_V', 'D', 'E_D']:
                if key in record and record[key] is not None:
                    try:
                        record[key] = float(record[key])
                    except ValueError:
                        record[key] = None
            
            records.append(record)
            
            # **Καθαρισμός μνήμης**: Αφαιρούμε το επεξεργασμένο στοιχείο για αποφυγή MemoryError
            elem.clear()
    
    return records

def export_to_xml(records, output_file):
    root = ET.Element("root")

    for idx, record in enumerate(records, start=1):
        row_element = ET.SubElement(root, "row")

        row_number_element = ET.SubElement(row_element, "ROW_NUMBER")
        row_number_element.text = f"galaxy_{idx}"

        # ids
        identifier_fields = {'PGC', 'OBJNAME', 'ID_NED', 'ID_NEDD', 'ID_IRAS', 'ID_2MASS', 'SDSS_PHOTID', 'SDSS_SPECID'}
        error_fields = {col for col in record.keys() if col.startswith("E_")}
        ci_fields = {"D_LO68", "D_HI68", "D_LO95", "D_HI95"}
        
        identifiers_present = {key: value for key, value in record.items() if key in identifier_fields and value is not None}
        if identifiers_present:
            id_element = ET.SubElement(row_element, "identifiers")
            for key, value in identifiers_present.items():
                field = ET.SubElement(id_element, key)
                field.text = str(value)

        # errors
        errors_present = {}
        for error_key in error_fields:
            main_key = error_key[2:]  # Το κύριο πεδίο χωρίς το "E_"
            if main_key in record and record[main_key] is not None:
                errors_present[main_key] = (record[main_key], record[error_key])

        if errors_present:
            errors_element = ET.SubElement(row_element, "errors")
            for main_key, (main_value, error_value) in errors_present.items():
                error_entry = ET.SubElement(errors_element, "error")
                column_element = ET.SubElement(error_entry, "column")
                ET.SubElement(column_element, main_key).text = str(main_value)

                error_column_element = ET.SubElement(error_entry, "error_column")
                ET.SubElement(error_column_element, "E_" + main_key).text = str(error_value)

        # confidence intervals
        ci_present = {key: value for key, value in record.items() if key in ci_fields and value is not None}
        if ci_present and "D" in record:
            ci_element = ET.SubElement(row_element, "confidence_intervals")
            ci_error_element = ET.SubElement(ci_element, "CI_error")

            column_element = ET.SubElement(ci_error_element, "column")
            ET.SubElement(column_element, "D").text = str(record["D"])

            lower_bound_element = ET.SubElement(ci_error_element, "lower_bound")
            if "D_LO68" in ci_present:
                ET.SubElement(lower_bound_element, "D_LO68").text = str(record["D_LO68"])
            if "D_LO95" in ci_present:
                ET.SubElement(lower_bound_element, "D_LO95").text = str(record["D_LO95"])

            upper_bound_element = ET.SubElement(ci_error_element, "upper_bound")
            if "D_HI68" in ci_present:
                ET.SubElement(upper_bound_element, "D_HI68").text = str(record["D_HI68"])
            if "D_HI95" in ci_present:
                ET.SubElement(upper_bound_element, "D_HI95").text = str(record["D_HI95"])

        # general columns
        gen_fields = set(record.keys()) - identifier_fields - error_fields - ci_fields
        gen_present = {key: value for key, value in record.items() if key in gen_fields and value is not None}

        if gen_present:
            gen_element = ET.SubElement(row_element, "gen")
            for key, value in gen_present.items():
                field = ET.SubElement(gen_element, key)
                field.text = str(value)

    prettify_xml(root)
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"Processed XML saved to {output_file}")

# Usage
csv_path = "HECATE_columns.csv"  # Replace with actual CSV path
intermediate_xml = "HECATE_columns-inter.xml"
output_xml = "HECATE_columns.xml"

# Convert CSV to XML
csv_to_xml(csv_path, intermediate_xml)

# Process the converted XML
data = parse_xml(intermediate_xml)
export_to_xml(data, output_xml)