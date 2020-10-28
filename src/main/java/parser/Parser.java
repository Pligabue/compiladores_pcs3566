package parser;

import java.util.ArrayList;
import java.util.Set;

import lexical_analysis.LexicalAnalyser;
import lexical_analysis.Token;


public class Parser {

    private String filename = "sample_text.txt";
    private ArrayList<Token> tokenList;
    private int currentTokenIndex = 0;
    private final Set<String> TYPES = Set.of("program", "assign", "read", "data", "print", 
                                             "goto", "if", "for", "next", "dim", "def",
                                             "gosub", "return", "remark", "+", "-", 
                                             "*", "/");
    private Node root = new Node("program", 0);

    private Node currentNode = root;
    private Token currentToken;
    private int currentLineNumber;
    private int parenthesesCount = 0;

    private ArrayList<String> idList = new ArrayList<String>();

    public Parser() { setUp(); }
    public Parser(String filename) { 
        this.filename = filename;
        setUp();
    }

    private void setUp() {
        LexicalAnalyser lexicalAnalyser = new LexicalAnalyser(filename);
        tokenList = lexicalAnalyser.analyseText();
        currentToken = tokenList.get(currentTokenIndex);
    }

    private void getNextToken() {
        this.currentToken = this.tokenList.get(++currentTokenIndex);
    }

    private void getPreviousToken() {
        this.currentToken = this.tokenList.get(--currentTokenIndex);
    }

    public Node buildAST() {
        try {
            while (currentTokenIndex < tokenList.size()) {
                setLineNumber();
                handleKeyword(this.currentToken.getValue());
            }
            return this.root;
        } catch (Exception e) {
            System.out.println(e);
            return this.root;
        }
    }

    private void setLineNumber() throws Exception {
        try {
            this.currentLineNumber = Integer.parseInt(currentToken.getValue());
            getNextToken();
        } catch (Exception e) {
            throw new Exception("Número da linha inválido.\n");
        }
    }

    private void handleKeyword(String keyword) throws Exception {
        switch (keyword) {
            case "LET":
                Node newNode = new Node("assign");
                newNode.setLineNumber(this.currentLineNumber);
                currentNode.addChild(newNode);
                currentNode = newNode;

                getNextToken();
                String tokenName = currentToken.getName();
                String tokenValue = currentToken.getValue();

                if (!tokenName.equals("identifier"))
                    throw new Exception("Must assign to identifier.\n");
                if (!idList.contains(tokenValue))
                    idList.add(tokenValue);

                getNextToken();
                tokenName = currentToken.getName();
                tokenValue = currentToken.getValue();

                if (!tokenName.equals("operator") || !tokenValue.equals("="))
                    throw new Exception("Assignment must have equals sign.\n");

                getNextToken();
                handleExpression();   
                
                break;
            default:
                break;
        }
    }

    private void handleExpression() throws Exception {
        currentNode.addChild(getSubExpression());
        if (this.parenthesesCount > 0)
            throw new Exception("Erro nos parênteses.\n");
    }

    private Node getSubExpression() throws Exception {
        Node leftNode = new Node();
        Node operation = new Node();
        Node rightNode = new Node();

        if (currentToken.getName().equals("identifier") || currentToken.getName().equals("literal")) {
            leftNode.setType(currentToken.getValue());
            getNextToken();
        } else if (currentToken.getName().equals("separator") && currentToken.getValue().equals("(")) {
            getNextToken();
            this.parenthesesCount++;
            leftNode = getSubExpression();
        } else 
            throw new Exception("Must be assigned to something.\n");

        if (currentToken.getName().equals("separator") && currentToken.getValue().equals(")")) {
            getNextToken();
            this.parenthesesCount--;
            return leftNode;
        } else if (currentToken.getName().equals("operator")) {
            operation.setType(currentToken.getValue());
            getNextToken();
        } else {
            return leftNode;
        }
        
        rightNode = getSubExpression();

        operation.addChild(leftNode);
        operation.addChild(rightNode);
        return operation;
    }
}