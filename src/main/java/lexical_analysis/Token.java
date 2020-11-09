package lexical_analysis;

import java.util.Set;
/**
 * Token
 */
public class Token {

    private String type;
    private String value;

    private final Set<String> TYPES = Set.of("identifier", "keyword", "separator", "operator", "literal", "comment");

    public static void main(String[] args) {
        Token token = new Token("operator", "Valor teste");
        System.out.println(token);
    }

    public Token(String type, String value) {
        setType(type);
        setValue(value);
    }

    public void setType(String type) {
        if (TYPES.contains(type))
            this.type = type;
        else
            System.out.println("Invalid type");
    }

    public void setValue(String value) {
        this.value = value;
    }

    public String getType() {
        return this.type;
    }

    public String getValue() {
        return this.value;
    }

    public String toString() {
        return String.format("<Token type=\"%s\" value=\"%s\">", this.type, this.value);
    }
}
