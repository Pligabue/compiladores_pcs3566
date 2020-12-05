import re
from token import Token
from typing import NewType

import sys

class LexicalAnalyser:

    OPERATORS = {"+", "-", "*", "/", ">=", ">", "<>", "<", "<=", "=", "=="}
    KEYWORDS = {"END", "LET", "FN", "SIN", "COS", "TAN", "ATN", "EXP", "ABS",
                "LOG", "SQR", "INT", "RND", "READ", "DATA", "PRINT", "GOTO",
                "GO", "TO", "IF", "THEN", "FOR", "STEP", "NEXT", "DIM", "DEF FN",
                "GOSUB", "RETURN", "REM", "E"}
    SEPARATORS = {"(", ")", ",", "[", "]", "\n", "{", "}"}

    def __init__(self, filename="./sample_text.txt") -> None:
        self.token_list = []
        self.filename = filename
        self.token = ""

    def is_literal(self, token) -> bool:
        return bool(re.fullmatch(r'[+-]?[0-9]+|[+-]?[0-9]*\.[0-9]+|".*"', token))

    def get_token_type(self, token):
        if token in self.OPERATORS:
            return "operator"
        elif token in self.SEPARATORS:
            return "separator"
        elif token in self.KEYWORDS:
            return "keyword"
        elif self.is_literal(token):
            return "literal"
        return "identifier"

    def add_token(self, token):
        if token.strip() or token == "\n":
            token_type = self.get_token_type(token)
            new_token = Token(token_type, token)
            self.token_list.append(new_token)
        self.token = ""

    def build_tokens(self, line):
        
        enum_line = enumerate(line)
        
        for i, char in enum_line:
            if not char.strip():
                self.add_token(self.token)
                if char == "\n":
                    self.add_token(char)
            elif char in self.OPERATORS:
                self.add_token(self.token)
                current_and_next = char + line[i+1]
                if current_and_next in self.OPERATORS:
                    self.add_token(current_and_next)
                    next(enum_line, None)
                else:
                    self.add_token(char)
            elif char in self.SEPARATORS:
                self.add_token(self.token)
                self.add_token(char)
            elif char == '"':
                self.add_token(self.token)
                
                token = '"'

                for j in range(i+1, len(line)):

                    i, char = next(enum_line, None)
                    token = token + char

                    if char == '"' and line[j-1] != "\\":
                        break
                    
                self.add_token(token)
                
            else:
                self.token = self.token + char
                if i == len(line) - 1:
                    self.add_token(self.token)

    def analyse_text(self):
        try:
            print(self.filename)
            f = open(self.filename, "r")
            for line in f:
                if not line.strip():
                    continue
                self.build_tokens(line)
            f.close()
        except IOError:
            print("File does no exist.\n")
        
        new_line_token = Token("separator", "\n")
        while True:
            last_token = self.token_list[-1]
            if last_token.type == "separator" and last_token.value == "\n":
                self.token_list.pop()
            else:
                break
        self.token_list.append(new_line_token)
            
        for i, token in enumerate(self.token_list):
            if (token.type == "literal" and
               self.token_list[i-1].type == "operator" and 
               self.token_list[i-1].value == "-" and
               self.token_list[i-2].type not in ["literal", "identifier"]):

               literal_token = self.token_list.pop(i)
               literal_token.value = "-" + literal_token.value

               self.token_list[i-1] = literal_token

        for i, token in enumerate(self.token_list):
            if (token.type == "identifier" and
               self.token_list[i-1].type == "operator" and 
               self.token_list[i-1].value == "-" and
               self.token_list[i-2].type not in ["literal", "identifier"]):

               self.token_list[i-1].value = "*"
               self.token_list.insert(i-1, Token(type="literal", value="-1"))

        return self.token_list

if __name__ == "__main__":

    filename = "sample_text.txt"
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    token_list = LexicalAnalyser(filename=filename).analyse_text()
    for token in token_list:
        print(token)