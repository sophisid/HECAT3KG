# **PARSEC-Mappings**

This repository contains mappings and configurations for transforming structured data into RDF using the [X3ML Engine](https://github.com/isl/x3ml). The mappings are specifically designed for the **PARSEC project**, supporting the generation of RDF data for celestial bodies and related entities.

---

## **Contents**
Here’s the folder structure you provided, formatted to reflect your repository structure and files:

```
HECATE-Mappings/
├── HECATE/
│   ├── HECATE_small.csv                # Input CSV file for celestial body data
│   ├── HECATE_small.trig               # Generated RDF output in TriG format
│   ├── HECATE_small.xml                # XML version of the input data
│   ├── csv_to_xml.py                   # Python script for converting CSV to XML
│   ├── mappings/
│   │   ├── generator-policies.xml      # Policy file for IRI & label generation
│   │   ├── mappings_celestial_body.x3ml # X3ML mapping file for celestial bodies
│   ├── run_hecate.sh                   # Shell script to automate the X3ML transformation process
├── parsec_version5_1.ttl               # Ontology file in Turtle format
```

---

## **Setup and Requirements**

### **Prerequisites**
- Java 11 or later
- Maven (to build the X3ML engine)
- X3ML Engine JAR file

### **Steps to Build the X3ML Engine**
1. Clone the X3ML engine repository:
   ```bash
   git clone https://github.com/isl/x3ml.git
   cd x3ml
   ```
2. Build the project using Maven:
   ```bash
   mvn clean install
   ```
3. After building, locate the executable JAR file in the `target/` directory (note the <version>):
   ```
   target/x3ml-engine-<version>-exejar.jar
   ```

---

## **Running the Transformations**

### **Command Example**
Run the X3ML engine with the following command:
```bash
java -jar ../x3ml/target/x3ml-engine-2.2.2-SNAPSHOT-exejar.jar \
--input HECATE_small.xml \
--x3ml mappings/mappings_celestial_body.x3ml \
--policy mappings/generator-policies.xml \
--output HECATE_small.rdf \
--format text/turtle \
--reportProgress
```

### **Options Explained**
- `--input`: Specifies the XML input file (e.g., `HECATE_small.xml`).
- `--x3ml`: Points to the mapping file (e.g., `mappings_celestial_body.x3ml`).
- `--policy`: Specifies the IRI generator policy file (e.g., `generator-policies.xml`).
- `--output`: Specifies the output RDF file (e.g., `HECATE_small.rdf`).
- `--format`: Defines the RDF output format (`text/turtle`, `application/trig`, etc.).
- `--reportProgress`: Outputs progress information to the console (optional).

---

## **Folder Structure**

```
HECATE-Mappings/
├── mappings/
│   ├── mappings_celestial_body.x3ml  # X3ML mapping for celestial bodies
├── generator-policies.xml            # Policy for IRI generation
├── HECATE_small.xml                  # Sample input data
├── HECATE_small.rdf                  # Generated RDF output
└── README.md                         # Documentation
```
