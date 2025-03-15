import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom

def prettify_xml(element):
    rough_string = ET.tostring(element, encoding="utf-8")
    parsed = minidom.parseString(rough_string)
    return parsed.toprettyxml(indent="  ")

def csv_to_xml(csv_file, xml_file):
    root = ET.Element("root")
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row_number, row in enumerate(reader, start=1):  # Enumerate to get row number
            item = ET.SubElement(root, "row")
            # Add the row number element
            row_number_elem = ET.SubElement(item, "ROW_NUMBER")
            row_number_elem.text = str(row_number)
            # Add the rest of the CSV fields
            for key, value in row.items():
                child = ET.SubElement(item, key)
                child.text = value
    
    # Pretty-print the XML
    pretty_xml = prettify_xml(root)
    with open(xml_file, "w", encoding="utf-8") as file:
        file.write(pretty_xml)

csv_to_xml("HECATE_columns.csv", "HECATE_columns.xml")
