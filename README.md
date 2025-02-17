# **PARSEC-Mappings**

This repository contains mappings and configurations for transforming structured data into RDF using the [X3ML Engine](https://github.com/isl/x3ml). The mappings are specifically designed for the **PARSEC project**, supporting the generation of RDF data for celestial bodies and related entities.

---

## **Contents**
Here’s the folder structure of the repository:

```
HECATE-Mappings/
├── HECATE/
│   ├── HECATE_small.csv                # Input CSV file for celestial body data
│   ├── HECATE_small.trig               # Generated RDF output in TriG format
│   ├── HECATE_small.xml                # XML version of the input data
│   ├── csv_to_xml.py                   # Python script for converting CSV to XML
│   ├── mappings/
│   │   ├── generator-policies.xml      # Policy file for IRI & label generation
│   │   ├── mappings_data_source.x3ml   # X3ML mapping for data source (columns)
│   │   ├── mappings_galaxy.x3ml        # X3ML mapping for celestial bodies (rows)
│   ├── run_hecate.sh                   # Shell script to automate the X3ML transformation process
├── parsec_version5_1.ttl               # Ontology file in Turtle format
```

---

## **Custom Generator - MathExpressionGenerator**
This repository includes a **custom generator** located at:

```
gr/forth/MathExpressionGenerator.java
```

### **What does this generator do?**
- It calculates the mathematical expression:  
  \[
  2.78 \times 10^{(-4 + \text{flag_value})}
  \]
- The `flag_value` is provided dynamically as an **XPath parameter** in the **X3ML mappings**.
- This generator is declared in `generator-policies.xml` and can be used in X3ML mappings to perform transformations on data dynamically.

---

## **Understanding the X3ML Mapping Files**
This repository contains two key **X3ML** mapping files:

1. **`mappings_data_source.x3ml`**  
   - **Purpose:** Defines what the **columns** of the dataset represent.
   - **Usage:** This mapping ensures that each column is correctly associated with the appropriate RDF properties and classes.
   - **Example:** If a column represents the mass of a celestial body, this mapping ensures that it is linked to the correct ontology property.

2. **`mappings_galaxy.x3ml`**  
   - **Purpose:** Defines how the **rows** (data instances) are transformed into RDF.
   - **Usage:** This mapping creates instances of celestial bodies and links them to their properties.
   - **Example:** If a row in the CSV represents a specific galaxy, this mapping generates an RDF resource for that galaxy and assigns it properties.

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
2. Before building the project, add the `MathExpressionGenerator` to the following path:
   ```
   src/main/java/gr/forth/MathExpressionGenerator.java
   ```
3. Build the project using Maven:
   ```bash
   mvn clean install
   ```
4. After building, locate the executable JAR file in the `target/` directory:
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
--x3ml mappings/mappings_galaxy.x3ml, mappings/mappings_data_source.x3ml \
--policy mappings/generator-policies.xml \
--output HECATE_small.rdf \
--format text/turtle \
--reportProgress
```

### **Options Explained**
- `--input`: Specifies the XML input file (e.g., `HECATE_small.xml`).
- `--x3ml`: Points to the mapping file (`mappings_galaxy.x3ml` and `mappings_data_source.x3ml` separated with ",").
- `--policy`: Specifies the IRI generator policy file (`generator-policies.xml`).
- `--output`: Specifies the output RDF file (e.g., `HECATE_small.rdf`).
- `--format`: Defines the RDF output format (`text/turtle`, `application/trig`, etc.).
- `--reportProgress`: Outputs progress information to the console (optional).

---