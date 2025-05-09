import java.io.*;

public class PreprocessingHecate {
    public static void main(String[] args) {
        String inputFile = "hecate_test_100.csv";
        String outputFile = "hecate_test_100_with_errors.csv";

        try (BufferedReader br = new BufferedReader(new FileReader(inputFile));
             BufferedWriter bw = new BufferedWriter(new FileWriter(outputFile))) {

            String headerLine = br.readLine();
            if (headerLine == null) {
                System.out.println("Empty file.");
                return;
            }

            // Append new headers
            bw.write(headerLine + ",E_DEC,E_RA,Reliability_Status,Q12_Description,Q25_Description,Q60_Description,Q100_Description,Metallicity_Status,Source_Label,D_Estimation_Method\n");

            String line;
            while ((line = br.readLine()) != null) {
                String[] values = line.split(",");

                // Extract required values
                double fAstrom = parseDouble(values[10]); // F_ASTROM
                String rFlag = values[15];                // RFlag
                String flagMetal = values[96];
                String rSource = values[14]; // RSOURCE column (update if index is different)
                String dMethodCode = values[31];


                // Q indices (update if needed)
                String q12 = getValue(values, 46); // Q12
                String q25 = getValue(values, 47); // Q25
                String q60 = getValue(values, 48); // Q60
                String q100 = getValue(values, 49); // Q100
                


                // Compute margins
                double eDec = computeMargin(fAstrom);
                double eRa = computeMargin(fAstrom);

                // Map flags
                String reliabilityStatus = mapRFlag(rFlag);
                String metallicityStatus = mapFlagMetal(flagMetal);
                String sourceLabel = mapRSource(rSource);
                String q12Desc = mapQFlag(q12);
                String q25Desc = mapQFlag(q25);
                String q60Desc = mapQFlag(q60);
                String q100Desc = mapQFlag(q100);
                String dEstimationMethod = mapDMethod(dMethodCode);

                // Write result
                bw.write(line + "," + eDec + "," + eRa + "," + reliabilityStatus + "," +
                        q12Desc + "," + q25Desc + "," + q60Desc + "," + q100Desc + "," + 
                        metallicityStatus + "," + sourceLabel + "," + dEstimationMethod + "\n");
            }
            System.out.println("Processing complete. Output saved to " + outputFile);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static double parseDouble(String value) {
        try {
            return Double.parseDouble(value);
        } catch (NumberFormatException e) {
            return Double.NaN;
        }
    }

    private static String getValue(String[] values, int index) {
        return (index < values.length) ? values[index].trim() : "";
    }

    private static double computeMargin(double flagValue) {
        if (Double.isNaN(flagValue)) return Double.NaN;
        return 2.78 * Math.pow(10, -4 + flagValue);
    }

    private static String mapRFlag(String value) {
        if (value == null) return "Unknown";
        value = value.trim();

        return switch (value) {
            case "1" -> "Reliable";
            case "2" -> "Set to 0. Some data was missing galaxy treated as circular isophote ";
            default -> "Unknown";
        };
    }

    private static String mapQFlag(String value) {
        if (value == null || value.isEmpty()) return "Unknown";
        return switch (value.trim()) {
            case "0" -> "not in IRAS";
            case "1" -> "upper limit";
            case "2" -> "moderate";
            case "3" -> "high";
            case "4" -> "flux from IRAS-RBGS";
            default -> "Unknown";
        };
    }

    private static String mapFlagMetal(String value) {
    if (value == null) return "Unknown";
    value = value.trim();
    return switch (value) {
        case "-1" -> "Missing";
        case "0" -> "Reliable";
        case "1" -> "O3N2 ratio >2 (outside PP04 range)";
        case "2" -> "Low S/N ratio (<3 for weakest line)";
        default -> "Unknown";
    };
}

    private static String mapRSource(String value) {
    if (value == null) return "Unknown";

    value = value.trim().toUpperCase();

    return switch (value) {
        case "H" -> "HYPERLEDA";
        case "S" -> "SDSS";
        case "2" -> "2MASS";
        case "6" -> "2dFGS";
        case "W" -> "WINGS";
        case "Y" -> "SkyMapper";
        case "A" -> "Amiga-CIG";
        case "K" -> "UNGC";
        case "V" -> "VIII/77";
        case "1" -> "KKH2001";
        case "7" -> "KKH2007";
        case "N" -> "NED";
        default -> "Unknown";
    };
}

    private static String mapDMethod(String value) {
        if (value == null || value.isEmpty()) return "Unknown";
        return switch (value.trim()) {
        case "N" -> "using NED-D distance measurements";
        case "Z" -> "regression";
        case "ZV" -> "regression for Virgo Cluster members";
        case "C" -> "distance from NED-D measurements but uncertainty from regression";
        case "CV" -> "distance from NED-D measurements but uncertainty from Virgo Cluster regressor";
        default -> "Unknown";
        };
    }


}
