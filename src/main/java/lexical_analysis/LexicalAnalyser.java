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
    private static final Set<String> separators = Set.of(" ", "(", ")", ".", ",");

    private ArrayList<Token> tokenList = new ArrayList<Token>();

    public LexicalAnalyser() { }
    public LexicalAnalyser(String filename) { this.filename = filename; }

    private boolean isStringLiteral(String word) {
        return word.matches("\".*\"");
    }

    private void buildToken(String word) {
        if (operators.contains(word)) {
            tokenList.add(new Token("operator", word));
        } else if (keywords.contains(word)) {
            tokenList.add(new Token("keyword", word));
        } else if (separators.contains(word)) {
            tokenList.add(new Token("separator", word));
        } else if (word.matches("[0-9]+|[0-9]*\\.[0-9]+") || isStringLiteral(word)) {
            tokenList.add(new Token("literal", word));
        } else {
            tokenList.add(new Token("identifier", word));
        }
    }

    private String[] separateOnSubString(String word, String subString) {
        if (isStringLiteral(word)) {
            return new String[]{ word };
        } else if (subString.equals(" ")) {
            return word.split(subString);
        }
        return word.split(String.format("(?<=\\Q%s\\E)|(?=\\Q%s\\E)", subString, subString));
    }

    private ArrayList<String> separateStringLiterals(String line) { ////// Separa cadeias fixas

        String[] splitOnQuotes = line.split("(?<=(?:[^\\\\]|^)\")|(?<!\\\\)(?=\")");
        ArrayList<String> wordList = new ArrayList<String>();

        for (int i = 0; i < splitOnQuotes.length; i++) {
            if (splitOnQuotes[i].equals("\"")) {
                wordList.add(String.format("\"%s\"", splitOnQuotes[i+1]));
                i += 2;
            } else {
                wordList.add(splitOnQuotes[i]);
            }
        }

        return wordList;
    }

    private void buildTokens(String line) {

        ArrayList<String> wordList = separateStringLiterals(line);
        
        for (String separator : separators) {
            ArrayList<String> tempList = new ArrayList<String>();
            for (String word : wordList) {
                for (String newWord : separateOnSubString(word, separator)) {
                    tempList.add(newWord);
                }
            }
            wordList = tempList;
        }
        for (String operator : operators) {
            ArrayList<String> tempList = new ArrayList<String>();
            for (String word : wordList) {
                for (String newWord : separateOnSubString(word, operator)) {
                    tempList.add(newWord);
                }
            }
            wordList = tempList;
        }
        for (String word : wordList) {
            buildToken(word);
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