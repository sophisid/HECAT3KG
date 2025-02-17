package gr.forth;

import gr.forth.ics.isl.x3ml.X3MLGeneratorPolicy.CustomGenerator;
import gr.forth.ics.isl.x3ml.X3MLGeneratorPolicy.CustomGeneratorException;
import lombok.extern.log4j.Log4j2;

/**
 * Custom generator for computing 2.78 * 10 ^ (-4 + flag_value)
 */
@Log4j2
public class MathExpressionGenerator implements CustomGenerator {

    private Double flagValue;

    @Override
    public void setArg(String name, String value) throws CustomGeneratorException {
        if ("flag_value".equals(name)) {
            try {
                flagValue = Double.parseDouble(value);
            } catch (NumberFormatException e) {
                throw new CustomGeneratorException("Invalid flag_value: " + value);
            }
        } else {
            throw new CustomGeneratorException("Unrecognized argument name: " + name);
        }
    }

    @Override
    public String getValue() throws CustomGeneratorException {
        if (flagValue == null) {
            throw new CustomGeneratorException("Missing flag_value argument");
        }
        // Compute the mathematical expression
        double result = 2.78 * Math.pow(10, -4 + flagValue);
        return String.valueOf(result);
    }

    @Override
    public String getValueType() throws CustomGeneratorException {
        return "Literal"; // Returning the computed value as a literal
    }

    @Override
    public boolean mergeMultipleValues() {
        return false; // Does not support merging values from similar elements
    }

    @Override
    public void usesNamespacePrefix() {
        log.error("The " + this.getClass().getName() + " custom generator does not support injecting prefix yet");
    }
}
