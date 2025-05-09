import java.io.*;
import java.util.regex.*;

// Used to rewrite the links in the original mapping file so they match

public class MeasurementUriRewriter {
    public static void main(String[] args) {
        String inputFile = "parsec_mapping_2.ttl";
        String outputFile = "updated_parsec_mapping.ttl";

        try (BufferedReader reader = new BufferedReader(new FileReader(inputFile));
             BufferedWriter writer = new BufferedWriter(new FileWriter(outputFile))) {

            String line;
            Pattern pattern = Pattern.compile(
                "rr:template\\s+\"https://hecate\\.ia\\.forth\\.gr/measurement/([A-Za-z0-9_]+)/\\{PGC}.*?\""
            );

            while ((line = reader.readLine()) != null) {
                Matcher matcher = pattern.matcher(line);

                if (matcher.find()) {
                    String column = matcher.group(1);
                    String replacement = "rr:template \"https://parsec.forth.gr/celestial_body/galaxy_{PGC}/column/" +
                            column + "/measurement/galaxy_{PGC}_" + column + "\"";
                    line = matcher.replaceAll(replacement);
                }

                writer.write(line);
                writer.newLine();
            }

            System.out.println(" Rewrite complete! Output saved to: " + outputFile);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
