import pandas as pd
import xml.etree.ElementTree as ET
import math

CLASSIFICATION_MAP = {
    "RA": "Right Ascension",
    "DEC": "Declination",
    "F_ASTROM": "Astrometric Precision Flag",
    "R1": "D25 semi-major axis",
    "R2": "D25 semi-minor axis",
    "PA": "D25 positional angle",
    "T": "Numerical Hubble-type",
    "E_T": "Uncertainty in Hubble-type",
    "D": "Distance",
    "E_D": "Uncertainty in Distance",
    "D_LO68": "Distance Lower bound (68% CI)",
    "D_HI68": "Distance Upper bound (68% CI)",
    "UT": "Total U-band magnitude",
    "BT": "Total B-band magnitude",
}


UNIT_MAP = {
    "RA":          "degrees",
    "DEC":         "degrees",
    "F_ASTROM":    "",             # dimensionless or special
    "R1":          "arcmin",
    "R2":          "arcmin",
    "PA":          "degrees",
    "RSOURCE":     "",             # dimensionless flag
    "RFLAG":       "",             # dimensionless
    "T":           "",             # dimensionless
    "E_T":         "",             # dimensionless
    "INCL":        "degrees",      # if it's an inclination angle
    "V":           "km/s",
    "E_V":         "km/s",
    "V_VIR":       "km/s",
    "E_V_VIR":     "km/s",
    "NDIST":       "",             # integer count
    "EDIST":       "",             # boolean/flag
    "D":           "Mpc",
    "E_D":         "Mpc",
    "D_LO68":      "Mpc",
    "D_HI68":      "Mpc",
    "D_LO95":      "Mpc",
    "D_HI95":      "Mpc",
    "DMETHOD":     "",             # distance method code
    "UT":          "mag",
    "BT":          "mag",
    "VT":          "mag",
    "IT":          "mag",
    "E_UT":        "mag",
    "E_BT":        "mag",
    "E_VT":        "mag",
    "E_IT":        "mag",
    "AG":          "mag",
    "AI":          "mag",
    "S12":         "Jy",
    "S25":         "Jy",
    "S60":         "Jy",
    "S100":        "Jy",
    "Q12":         "",             # dimensionless
    "Q25":         "",             # dimensionless
    "Q60":         "",             # dimensionless
    "Q100":        "",             # dimensionless
    "WF1":         "mag",
    "WF2":         "mag",
    "WF3":         "mag",
    "WF4":         "mag",
    "E_WF1":       "mag",
    "E_WF2":       "mag",
    "E_WF3":       "mag",
    "E_WF4":       "mag",
    "WFPOINT":     "",             # boolean flag
    "WFTREAT":     "",             # boolean flag
    "J":           "mag",
    "H":           "mag",
    "K":           "mag",
    "E_J":         "mag",
    "E_H":         "mag",
    "E_K":         "mag",
    "FLAG_2MASS":  "",             # dimensionless
    "U":           "mag",
    "G":           "mag",
    "R":           "mag",
    "I":           "mag",
    "Z":           "mag",
    "E_U":         "mag",
    "E_G":         "mag",
    "E_R":         "mag",
    "E_I":         "mag",
    "E_Z":         "mag",
    "logL_TIR":    "log10(L_sun)",
    "logL_FIR":    "log10(L_sun)",
    "logL_60u":    "log10(L_sun)",
    "logL_12u":    "log10(L_sun)",
    "logL_22u":    "log10(L_sun)",
    "logL_K":      "log10(L_sun)",
    "ML_RATIO":    "",             # dimensionless ratio
    "logSFR_TIR":  "log10(M_sun/yr)",
    "logSFR_FIR":  "log10(M_sun/yr)",
    "logSFR_60u":  "log10(M_sun/yr)",
    "logSFR_12u":  "log10(M_sun/yr)",
    "logSFR_22u":  "log10(M_sun/yr)",
    "logSFR_HEC":  "log10(M_sun/yr)",
    "FLAG_SFR_HEC":"",             # dimensionless/flag
    "logM_HEC":    "log10(M_sun)",
    "logSFR_GSW":  "log10(M_sun/yr)",
    "logM_GSW":    "log10(M_sun)",
    "MIN_SNR":     "",             # dimensionless
    "METAL":       "dex",          # 12+log(O/H) gas-phase metallicity
    "FLAG_METAL":  "",             # dimensionless
    "CLASS_SP":    "",             # dimensionless classification
    "AGN_S17":     "",             # dimensionless classification
    "AGN_HEC":     "",             # dimensionless classification
}

ERROR_MAP = {
    "T":      "E_T",
    "D":      "E_D",
    "UT":     "E_UT",
    "BT":     "E_BT",
    "VT":     "E_VT",
    "IT":     "E_IT",
    "WF1":    "E_WF1",
    "WF2":    "E_WF2",
    "WF3":    "E_WF3",
    "WF4":    "E_WF4",
    "J":      "E_J",
    "H":      "E_H",
    "K":      "E_K",
    "U":      "E_U",
    "G":      "E_G",
    "R":      "E_R",
    "I":      "E_I",
    "Z":      "E_Z",
    "V":      "E_V",
    "V_VIR":  "E_V_VIR",
    "RA":     None,  
    "DEC":    None,
    "S12":    None,
    "S25":    None,
    "S60":    None,
    "S100":   None,
    "logL_TIR": None,
    "logL_FIR": None,
    # etc...
}


#F_ASTROM=flag_value, then error in RA/DEC = 2.78 * 10^( -4 + flag_value )
def compute_astrom_error(flag_value):
    if pd.isna(flag_value):
        return None
    return 2.78 * (10 ** (-4 + float(flag_value)))


# -----------------------------------------------------------------------------
# 2) MAIN FUNCTION
# -----------------------------------------------------------------------------
def create_xml_from_csv(csv_file, xml_file):
    df = pd.read_csv(csv_file)
    
    root = ET.Element("data_table")
    
    for i, row in df.iterrows():
        galaxy = ET.SubElement(root, "galaxy")
        
        # 2.1) NAME
        name = ET.SubElement(galaxy, "name")
        name.text = f"galaxy_{i}"
        
        # 2.2) IDENTIFIERS
        identifiers = ET.SubElement(galaxy, "identifiers")
        id_elements = ["ID_NED", "ID_NEDD", "ID_IRAS", "ID_2MASS", "SDSS_PHOTID", "SDSS_SPECID"]
        for col_id in id_elements:
            if col_id in df.columns and pd.notna(row[col_id]):
                id_element = ET.SubElement(identifiers, "id")
                val = ET.SubElement(id_element, "value")
                val.text = str(row[col_id])
                source_elem = ET.SubElement(id_element, "source")
                source_elem.text = col_id
        
        # 2.3) MEASUREMENTS
        measurements = ET.SubElement(galaxy, "measurements")
        
        # Example measurement columns (add whichever you want processed)
        measurement_columns = [
            "RA", "DEC", "F_ASTROM",
            "R1", "R2", "PA", "RSOURCE", "RFLAG",
            "T", "E_T", "INCL",
            "V", "E_V", "V_VIR", "E_V_VIR",
            "NDIST", "EDIST",
            "D", "E_D", "D_LO68", "D_HI68", "D_LO95", "D_HI95", "DMETHOD",
            "UT", "BT", "VT", "IT",
            "E_UT", "E_BT", "E_VT", "E_IT",
            "AG", "AI",
            "S12", "S25", "S60", "S100",
            "Q12", "Q25", "Q60", "Q100",
            "WF1", "WF2", "WF3", "WF4",
            "E_WF1", "E_WF2", "E_WF3", "E_WF4",
            "WFPOINT", "WFTREAT",
            "J", "H", "K",
            "E_J", "E_H", "E_K",
            "FLAG_2MASS",
            "U", "G", "R", "I", "Z",
            "E_U", "E_G", "E_R", "E_I", "E_Z",
            "logL_TIR", "logL_FIR", "logL_60u", "logL_12u", "logL_22u",
            "logL_K", "ML_RATIO",
            "logSFR_TIR", "logSFR_FIR", "logSFR_60u", "logSFR_12u", "logSFR_22u",
            "logSFR_HEC", "FLAG_SFR_HEC",
            "logM_HEC",
            "logSFR_GSW", "logM_GSW",
            "MIN_SNR", "METAL", "FLAG_METAL",
            "CLASS_SP", "AGN_S17", "AGN_HEC"
        ]

        
        for col in measurement_columns:
            # Skip if column is not in the DataFrame
            if col not in df.columns:
                continue
            
            # Skip if the cell is NaN
            if pd.isna(row[col]):
                continue
            
            # Create <measurement>
            measurement = ET.SubElement(measurements, "measurement")
            
            # column
            column_elem = ET.SubElement(measurement, "column")
            column_elem.text = col
            
            # value
            value_elem = ET.SubElement(measurement, "value")
            value_elem.text = str(row[col])
            
            # estimation_method
            estimation_method = ET.SubElement(measurement, "estimation_method")
            # e.g., if col == 'D' => check 'DMETHOD'
            if col == "D" and "DMETHOD" in df.columns and pd.notna(row["DMETHOD"]):
                estimation_method.text = str(row["DMETHOD"])
            else:
                estimation_method.text = ""
            
            # unit
            unit_elem = ET.SubElement(measurement, "unit")
            unit_elem.text = UNIT_MAP.get(col, "")
            
            # classification
            class_elem = ET.SubElement(measurement, "classification")
            class_elem.text = CLASSIFICATION_MAP.get(col, "")
            
            # 2.3.6) Lower / Upper Error Margins
            lower_err_elem = ET.SubElement(measurement, "lower_error_margin")
            upper_err_elem = ET.SubElement(measurement, "upper_error_margin")
            
            # default blank
            low_err_str = ""
            up_err_str = ""
            
            # If there's a symmetrical error column
            if col in ERROR_MAP and ERROR_MAP[col] in df.columns:
                err_col = ERROR_MAP[col]
                if pd.notna(row[err_col]):
                    low_err_str = str(row[err_col])
                    up_err_str  = str(row[err_col])
            
            # If RA or DEC, apply the F_ASTROM logic
            if col in ("RA", "DEC"):
                if "F_ASTROM" in df.columns and pd.notna(row["F_ASTROM"]):
                    astrom_err = compute_astrom_error(row["F_ASTROM"])
                    if astrom_err is not None:
                        low_err_str = f"{astrom_err:.6g}"
                        up_err_str  = f"{astrom_err:.6g}"
            
            lower_err_elem.text = low_err_str
            upper_err_elem.text = up_err_str
            
            # If this is the main distance column 'D', we check for D_LO68, D_HI68, D_LO95, D_HI95
            # or do the same for other columns if relevant in your CSV
            if col == "D":
                ci_lower_68_elem = ET.SubElement(measurement, "ci_lower_bound_68")
                ci_upper_68_elem = ET.SubElement(measurement, "ci_upper_bound_68")
                ci_lower_95_elem = ET.SubElement(measurement, "ci_lower_bound_95")
                ci_upper_95_elem = ET.SubElement(measurement, "ci_upper_bound_95")
                # 68% lower
                if "D_LO68" in df.columns and pd.notna(row["D_LO68"]):
                    ci_lower_68_elem.text = str(row["D_LO68"])
                # 68% upper
                if "D_HI68" in df.columns and pd.notna(row["D_HI68"]):
                    ci_upper_68_elem.text = str(row["D_HI68"])
                
                # 95% lower
                if "D_LO95" in df.columns and pd.notna(row["D_LO95"]):
                    ci_lower_95_elem.text = str(row["D_LO95"])
                # 95% upper
                if "D_HI95" in df.columns and pd.notna(row["D_HI95"]):
                    ci_upper_95_elem.text = str(row["D_HI95"])
    
    # Save XML
    tree = ET.ElementTree(root)
    tree.write(xml_file, encoding='utf-8', xml_declaration=True)

# Example usage
# create_xml_from_csv("galaxies.csv", "galaxies.xml")
# Example usage:
create_xml_from_csv("HECATE_small.csv", "galaxies.xml")
