package lexical_analysis;

import java.util.Set;
/**
 * Token
 */
public class Token {

    private String name;
    private String value;

    private final Set<String> NAMES = Set.of("identifier", "keyword", "separator", "operator", "literal", "comment");

    public static void main(String[] args) {
        Token token = new Token("operator", "Valor teste");
        System.out.println(token);
    }

    public Token(String name, String value) {
        setName(name);
        setValue(value);
    }

    public void setName(String name) {
        if (NAMES.contains(name))
            this.name = name;
        else
            System.out.println("Invalid name");
    }

    public void setValue(String value) {
        this.value = value;
    }

    public String getName() {
        return this.name;
    }

    public String getValue() {
        return this.value;
    }

    public String toString() {
        return String.format("<Token name=\"%s\" value=\"%s\">", this.name, this.value);
    }
}
