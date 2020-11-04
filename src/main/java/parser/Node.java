package parser;

import java.util.ArrayList;

public class Node {
    private String type;
    private Node parent = null;
    private int lineNumber;
    private ArrayList<Node> children = new ArrayList<Node>();

    public Node() { }

    public Node(String type) {
        this.type = type;
    }

    public void addChild(Node node) {
        this.children.add(node);
        node.setParent(this);
    }

    public void addParent(Node node) {
        node.addChild(this);
    }

    public void splitParent(Node node) {
        if (!isRoot()) {
            int index = parent.getChildren().indexOf(this);
            parent.getChildren().set(index, node);
            node.setParent(parent);
        }
        addParent(node);
    }

    public void replaceParentWithSelf() {
        if (isRoot()) 
            return;
        if (parent.isRoot()) {
            parent.getChildren().remove(this);
            parent.setParent(null);

            parent = null;
        } else {
            Node grandparent = parent.getParent();
            int index = grandparent.getChildren().indexOf(parent);
            grandparent.getChildren().set(index, this);
            
            parent.getChildren().remove(this);
            parent.setParent(null);

            setParent(grandparent);
        }
    }

    public void setParent(Node node) {
        parent = node;
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

    public String getType() {
        return this.type;
    }

    public int getLineNumber() {
        return this.lineNumber;
    }

    public ArrayList<Node> getChildren() {
        return this.children;
    }

    public boolean hasType() {
        return this.type != null;
    }

    public boolean hasSiblings() {
        return this.parent.getChildren().size() > 1;
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

    public int getLevel() {
        int level = 0;
        Node currentNode = this;
        while (!currentNode.isRoot()) {
            currentNode = currentNode.parent;
            level++;
        }
        return level;
    }

    public Node getRoot() {
        Node currentNode = this;
        while (!currentNode.isRoot()) {
            currentNode = currentNode.parent;
        }
        return currentNode;
    }

    public void printNode() {
        printNode(2);
    }

    public void printNode(int offset) {
        System.out.printf("type=%s\n", this.type);
        for (Node child : children) {
            for (int i = 0; i < offset; i++)
                System.out.printf(" ");
            child.printNode(offset + 2);
        }
    }

    public void printTree() {
        getRoot().printNode();
    }

    public static void main(String[] args) {
        Node main = new Node("Bola");
        Node child = new Node("Elevador");
        Node grandchild = new Node("Horace");

        main.addChild(new Node("Carro"));
        main.addChild(new Node("Dado"));
        main.addChild(child);

        child.addChild(new Node("Fato"));
        child.splitParent(new Node("Gato"));
        
        child.addChild(grandchild);
        grandchild.replaceParentWithSelf();

        main.printTree();
    }
    
    @Override
    public String toString() {
        return String.format("<Node type=%s>", type);
    }
}
