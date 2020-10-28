package parser;

import java.util.ArrayList;

public class Node {
    private String type;
    private int level;
    private int lineNumber;
    private Node parent = null;
    private ArrayList<Node> children = new ArrayList<Node>();

    public Node() { }

    public Node(String type) {
        this.type = type;
    }

    public Node(String type, int level) {
        this.type = type;
        this.level = level;
    }

    public void addChild(Node node) {
        this.children.add(node);
        node.setParent(this);
        node.setLevel(this.level + 1);
    }

    public void setParent(Node node) {
        this.parent = node;
    }

    public void setLevel(int level) {
        this.level = level;
    }

    public void setType(String type) {
        this.type = type;
    }

    public void setLineNumber(int lineNumber) {
        this.lineNumber = lineNumber;
    }

    public Node getParent() {
        return this.parent;
    } 

    public int getLevel() {
        return this.level;
    }

    public ArrayList<Node> getChildren() {
        return this.children;
    }

    public boolean isRoot() {
        return this.parent == null;
    }

    public boolean isInner() {
        return this.children.size() > 0;
    }

    public boolean isOuter() {
        return !isInner();
    }
}
