package parser;

import java.util.ArrayList;

public class Symbol {
    private String type;
    private String name;
    private boolean assigned = false;
    private ArrayList<Integer> dim = new ArrayList<Integer>();

    public Symbol(String type, String name, ArrayList<Integer> dim) {
        this.type = type;
        this.name = name;
        this.dim = dim;    
    }

    public Symbol(String name) {
        this.name = name;
        this.dim = new ArrayList<Integer>();    
    }

    public String getName() { return this.name }
}
