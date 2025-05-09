import java.io.*;
import java.util.*;


public class MappingAppender {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Get user inputs
        System.out.print("Enter column name (e.g., RA): ");
        String column = scanner.nextLine().trim();

        System.out.print("Does this column have error margins? (yes/no): ");
        boolean hasErrorMargins = scanner.nextLine().trim().equalsIgnoreCase("yes");

        String errorColumn = "";
        if (hasErrorMargins) {
            System.out.print("Enter the column name for the error margins (e.g., E_RA): ");
            errorColumn = scanner.nextLine().trim();
        }

        System.out.print("Does this column have reliability status? (yes/no): ");
        boolean hasReliability = scanner.nextLine().trim().equalsIgnoreCase("yes");

        String reliabilityColumn = "";
        if (hasReliability) {
            System.out.print("Enter the column name for the reliability flag (e.g., RFlag): ");
            reliabilityColumn = scanner.nextLine().trim();
        }

        String mappingFile = "parsec_mapping_2.ttl";
        List<String> lines = new ArrayList<>();

        try (BufferedReader reader = new BufferedReader(new FileReader(mappingFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                lines.add(line);
            }
        } catch (IOException e) {
            System.err.println("Error reading TTL file: " + e.getMessage());
            return;
        }

        // Create the galaxy link line
        String galaxyLink = "    rr:predicateObjectMap [ rr:predicate parsec:P1_has_measurement ; rr:objectMap [ rr:parentTriplesMap <#Measurement" + column + "> ] ; ] ;";

        // Insert galaxy link at line 125 (before the ".")
        for (int i = 124; i < lines.size(); i++) {
            if (lines.get(i).trim().equals(".")) {
                lines.add(i, galaxyLink);
                break;
            }
        }

        // Prepare measurement and column blocks
        StringBuilder measurement = new StringBuilder();
        measurement.append("\n### --- AUTO-GENERATED MAPPING FOR COLUMN:").append(column).append(" --- ###")
                .append("\n<#Measurement").append(column).append("> a rr:TriplesMap ;\n")
                  .append("    rml:logicalSource <#HekateCSV> ;\n")
                  .append("    rr:subjectMap [ rr:template \"https://hecate.ia.forth.gr/measurement/").append(column).append("/{PGC}\" ; rr:class parsec:E8_Measurement ] ;\n")
                  .append("    rr:predicateObjectMap [ rr:predicate parsec:P02_has_value ; rr:objectMap [ rml:reference \"").append(column).append("\" ; rr:datatype xsd:float ] ; ] ;\n")
                  .append("    rr:predicateObjectMap [ rr:predicate parsec:P21_is_measurement_from_column ; rr:objectMap [ rr:parentTriplesMap <#Column").append(column).append("> ] ; ] ;\n");

        if (hasErrorMargins) {
            measurement.append("    rr:predicateObjectMap [ rr:predicate parsec:P05_has_lower_margin_value ; rr:objectMap [ rml:reference \"")
                      .append(errorColumn).append("\" ; rr:datatype xsd:float ] ; ] ;\n")
                      .append("    rr:predicateObjectMap [ rr:predicate parsec:P06_has_upper_margin_value ; rr:objectMap [ rml:reference \"")
                      .append(errorColumn).append("\" ; rr:datatype xsd:float ] ; ] ;\n");
        }

        if (hasReliability) {
            measurement.append("    rr:predicateObjectMap [ rr:predicate parsec:P29_has_reliability_status ; rr:objectMap [ rml:reference \"")
                      .append(reliabilityColumn).append("\" ; ] ; ] ;\n");
        }

        measurement.append(".\n");

        String columnBlock = "\n<#Column" + column + "> a rr:TriplesMap ;\n" +
                             "    rml:logicalSource <#HekateCSV> ;\n" +
                             "    rr:subjectMap [ rr:template \"https://hecate.ia.forth.gr/column/" + column + "\" ; rr:class parsec:E16_Column ] .\n";

        // Append at the end
        lines.add(measurement.toString());
        lines.add(columnBlock);

        // Write back the TTL file
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(mappingFile))) {
            for (String l : lines) {
                writer.write(l);
                writer.newLine();
            }
            System.out.println("Mapping inserted successfully.");
        } catch (IOException e) {
            System.err.println("Error writing to TTL file: " + e.getMessage());
        }
    }
}
