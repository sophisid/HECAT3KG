# HECAT3KG

This repository contains tools and mapping configurations to convert data from the [HECATE galaxy catalogue](https://hecate.ia.forth.gr/) into RDF format using both RML and X3ML approaches.

---

## Directory Structure

```

HECAT3KG/
├── rml_mappings                       
├── MappingAppender.java               # used for the mappings
├── MeasurementUriRewriter.java        # a normilization 
├── methodology.txt                    # the methodlogy for the mappings
├── PreprocessingHecate.java           # a normalization
├── readme.txt                         # info on how to run the mappings without the script
├── run_rml_mappings.py                # run the mappings for all smaller csv
├── split_hecate.py                    # splits csv in smaller csv
├── updated_parsec_mapping.ttl         # mapping files
├── x3ml_mappings
│ └── gr                               # has a custom generator for the version 1
│ ├── mappings_v1
│ │ ├── generator-policies.xml         # URI generators
│ │ ├── mappings_data_source.x3ml      # mappings for HECATE & header column names
│ │ └── mappings_galaxy.x3ml           # mappings for galaxies (the non-efficient approach)
│ ├── mappings_v2
│ │ ├── generator-policies.xml         # URI generators
│ │ ├── mappings_data_source.x3ml      # mappings for HECATE & header column names
│ │ ├── mappings_galaxy.x3ml           # mappings for galaxies (the optimal approach)
│ ├── csv_to_xml.py                    # preprocess the csv to xml for the first approach
│ ├── preprocessing.py                 # preprocess the csv to xml with structure (second approach)
│ └── run_hecate.sh                    # runs the x3ml engine for each smaller csv 
├── .gitignore
└── docb.ttl                           # custom ontology
````

---

## How to Run

### 1. **Download the HECATE Dataset**

You can download the full HECATE dataset from the official site: 
https://hecate.ia.forth.gr/

---

### 2. **Run the RML Pipeline**

This pipeline uses the `split_hecate.py` and `run_rml_mappings.py` script to apply the RML mappings. It requires JAVA >= 17

```bash
python split_hecate.py
python run_rml_mappings.py
````

This will:

* Separate `HECATE.csv` as input
* Apply mappings from `rml_mappings/`
* Generate RDF in `output_rdf/`

---

### 3. **Run the X3ML Pipeline**

#### ⚠️ Version 1: Without Preprocessing

```bash
python csv_to_xml.py
sh run_hecate.sh
```

> **Note:** Version 1 uses direct mappings without any preprocessing and is **not recommended for more than 10 galaxies**, due to structure limitations and missing data.
It requires JAVA >= 11

#### ✅ Version 2: With Preprocessing (Recommended)

```bash
python preprocessing.py
python csv_to_xml.py
sh run_hecate.sh
```

This version preprocesses the CSV to enrich and clean the data before mapping it to RDF using the PARSEC ontology.It requires JAVA >= 11

---

## Notes

* Ensure required Python libraries and Java version are installed.
* You can download X3ML engine .jar from [here](https://github.com/isl/x3ml/releases)
* You can download the RMLMapper .jar from [here](https://github.com/RMLio/rmlmapper-java/releases)

