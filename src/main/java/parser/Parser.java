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
    private Node root = new Node("program");

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
        currentTokenIndex++;
        if (currentTokenIndex < tokenList.size())
            this.currentToken = this.tokenList.get(currentTokenIndex);
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
                Node assignNode = new Node("assign");
                assignNode.setLineNumber(this.currentLineNumber);
                currentNode.addChild(assignNode);

                getNextToken();
                String tokenType = currentToken.getType();
                String tokenValue = currentToken.getValue();

                if (!tokenType.equals("identifier"))
                    throw new Exception("Must assign to identifier.\n");
                if (!idList.contains(tokenValue))
                    idList.add(tokenValue);

                Node identifierNode = new Node(tokenValue);
                assignNode.addChild(identifierNode);

                getNextToken();
                tokenType = currentToken.getType();
                tokenValue = currentToken.getValue();

                if (!tokenType.equals("operator") || !tokenValue.equals("="))
                    throw new Exception("Assignment must have equals sign.\n");

                getNextToken();
                Node expressionNode = handleExpression();   
                assignNode.addChild(expressionNode);

                break;
            default:
                break;
        }
    }

    private Node handleExpression() throws Exception {
        Node expressionNode = getExpressions();
        if (this.parenthesesCount > 0)
            throw new Exception("Parentheses error.\n");
        return expressionNode;
    }

    private enum ExpStates {S0, S1, S2, S3}

    private Node getExpressions() throws Exception {

        Node mainNode, tempNode;
        boolean automatonDone = false;
        ExpStates state = ExpStates.S0;

        mainNode = new Node();

        while (!automatonDone) {    
            switch (state) {
                case S0:
                    if (currentToken.getType().equals("identifier") || currentToken.getType().equals("literal")) {
                        mainNode.setType(currentToken.getValue());
                        if (mainNode.hasSiblings())
                            mainNode = mainNode.getParent();
                        state = ExpStates.S1;
                    } else if (currentToken.getType().equals("separator") && currentToken.getValue().equals("(")) {
                        this.parenthesesCount++;
                        tempNode = new Node();
                        mainNode.addChild(tempNode);
                        mainNode = tempNode;

                        state = ExpStates.S2;
                    } else 
                        throw new Exception("Must be assigned to something.\n");
                    break;
            
                case S1:
                    if (currentToken.getType().equals("operator")) {
                        tempNode = new Node(currentToken.getValue());
                        mainNode.splitParent(tempNode);

                        mainNode = new Node();
                        tempNode.addChild(mainNode);

                        state = ExpStates.S0;
                    } else {
                        automatonDone = true;
                    }
                    break;
            
                case S2:
                    if (currentToken.getType().equals("identifier") || currentToken.getType().equals("literal")) {
                        mainNode.setType(currentToken.getValue());
                        if (mainNode.hasSiblings()) {
                            mainNode = mainNode.getParent();
                        }
                        state = ExpStates.S3;
                    } else if (currentToken.getType().equals("separator") && currentToken.getValue().equals("(")) {
                        this.parenthesesCount++;
                        tempNode = new Node();
                        mainNode.addChild(tempNode);
                        mainNode = tempNode;

                        state = ExpStates.S2;
                    } else 
                        throw new Exception("Must be assigned to something.\n");
                    break;
            
                case S3:
                    if (currentToken.getType().equals("operator")) {
                        tempNode = new Node(currentToken.getValue());
                        mainNode.splitParent(tempNode);

                        mainNode = new Node();
                        tempNode.addChild(mainNode);

                        state = ExpStates.S2;
                    } else if (currentToken.getType().equals("separator") && currentToken.getValue().equals(")")) {
                        this.parenthesesCount--;
                        tempNode = mainNode.getParent();
                        if (!tempNode.hasType()) {
                            mainNode.replaceParentWithSelf();
                        } else {
                            mainNode = tempNode;
                        }

                        if (this.parenthesesCount == 0)
                            state = ExpStates.S1;
                    } else
                        throw new Exception("Expected operator or closing parenthesis");
                    break;

                default:
                    throw new Exception("Invalid state.");
            }   
            if (!automatonDone)
                getNextToken(); 
        }   
        return mainNode.getRoot(); 
    }

    public static void main(String[] args) {
        Parser parser = new Parser();
        Node ast = parser.buildAST();
        ast.printTree();
    }
}