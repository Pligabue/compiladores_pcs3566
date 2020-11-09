package lexical_analysis;

import java.util.Set;

import java.io.File; // Import the File class
import java.io.FileNotFoundException; // Import this class to handle errors
import java.util.ArrayList;
import java.util.Scanner; // Import the Scanner class to read text files

/**
 * LexicalAnalyser
 */
public class LexicalAnalyser {

    private String filename = "sample_text.txt";

    private static final Set<String> operators = Set.of("+", "-", "*", "/", ">=", ">", "<>", "<", "<=", "=");
    private static final Set<String> keywords = Set.of("END", "LET", "FN", "SIN", "COS", "TAN", "ATN", "EXP", "ABS",
                                                       "LOG", "SQR", "INT", "RND", "READ", "DATA", "PRINT", "GOTO",
                                                       "GO", "TO", "IF", "THEN", "FOR", "STEP", "NEXT", "DIM", "DEF FN",
                                                       "GOSUB", "RETURN", "REM", "E");
    private static final Set<String> separators = Set.of("(", ")", ",");

    private ArrayList<Token> tokenList = new ArrayList<Token>();
    private String token = "";

    public LexicalAnalyser() { }
    public LexicalAnalyser(String filename) { this.filename = filename; }

    private boolean isLiteral(String token) {
        return token.matches("[0-9]+") || token.matches("[0-9]*\\.[0-9]+") || token.matches("\".*\"");
    }

    private String getTokenType(String token) {
        if (operators.contains(token)) {
            return "operator";
        } else if (separators.contains(token)) {
            return "separator";
        } else if (keywords.contains(token)) {
            return "keyword";
        } else if (isLiteral(token)) {
            return "literal";
        } else {
            return "identifier";
        }
    }

    private void addToken(String token) {
        if (!token.isBlank()) {
            tokenList.add(new Token(getTokenType(token), token));
        }
        this.token = "";
    }

    private void buildTokens(String line) {
        String currentChar;

        for (int i = 0; i < line.length(); i++) {
            currentChar = String.valueOf(line.charAt(i));

            if (currentChar.isBlank()) {
                addToken(this.token);
            } else if (operators.contains(currentChar)) {
                addToken(token);
                if (operators.contains(currentChar + line.charAt(i + 1))) {
                    addToken(currentChar + line.charAt(i + 1));
                    i = i + 1;
                } else {
                    addToken(currentChar);
                }
            } else if (separators.contains(currentChar)) {
                addToken(this.token);
                addToken(currentChar);
            } else if (currentChar.equals("\"")) {
                addToken(this.token);
                int j;
                String stringLiteral = "\"";

                for (j = i + 1; j < line.length(); j++) {
                    currentChar = String.valueOf(line.charAt(j));
                    stringLiteral = stringLiteral + currentChar;

                    if (currentChar.equals("\"") && line.charAt(j - 1) != '\\') {
                        System.out.println(stringLiteral);
                        break;
                    }
                }
                addToken(stringLiteral);
                i = j;
            } else {
                this.token = this.token + currentChar;
                if (i == line.length() - 1)
                    addToken(this.token);
            }
        }
    }

    public ArrayList<Token> analyseText() {
        try {
            File textFile = new File(this.filename);
            Scanner scanner = new Scanner(textFile);
            while (scanner.hasNextLine()) {
                String line = scanner.nextLine();
                buildTokens(line);
            }
            scanner.close();
        } catch (FileNotFoundException e) {
            System.out.println("Arquivo não existe");
            e.printStackTrace();
        }
        return tokenList;
    }

    public static void main(String[] args) {
        LexicalAnalyser lexicalAnalyser = new LexicalAnalyser();   
        ArrayList<Token> res = lexicalAnalyser.analyseText();
        for (Token token : res) {
            System.out.println(token);
        }     
    }
}