import re
from token import Token

import sys

class LexicalAnalyser:

    OPERATORS = {"+", "-", "*", "/", "^", ">=", ">", "<>", "<", "<=", "=", "=="}
    KEYWORDS = {"END", "LET", "FN", "SIN", "COS", "TAN", "ATN", "EXP", "ABS",
                "LOG", "SQR", "INT", "RND", "READ", "DATA", "PRINT", "GOTO",
                "GO", "TO", "IF", "THEN", "FOR", "STEP", "NEXT", "DIM", "DEF FN",
                "GOSUB", "RETURN", "REM", "E"}
    SEPARATORS = {"(", ")", ",", "[", "]", "\n", "{", "}"}

    LITERAL = "(?P<literal>\".*(?<!\\\\)\"|[\\+-]?[0-9]+|[\\+=]?[0-9]*\.[0-9]+)"
    IDENTIFIER = "(?P<identifier>[_a-zA-Z][_a-zA-Z0-9]*)"
    SEPARATOR = "(?P<separator>\\(|\\)|,|\\[|\\]|{|})"
    OPERATOR = "(?P<operator><>|<=|>=|==|>|<|\\+|-|\\*|/|=)"
    KEYWORD = "(?P<keyword>NEXT|PRINT|TO|FOR|RETURN|STEP|INT|EXP|RND|IF|ABS|DATA|THEN|COS|LET|END|SQR|LOG|THEN|REM|TAN|SIN|GOSUB|GO|DEF FN|GOTO|DIM|ATN|FN|READ)"
    WHITESPACE = "(?P<whitespace> +)|(?P<newline>\\n)\\n*"

    TOKEN_RE = re.compile(f"{KEYWORD}|{OPERATOR}|{SEPARATOR}|{LITERAL}|{IDENTIFIER}|{WHITESPACE}")

    def __init__(self, filename="./sample_text.txt") -> None:
        self.token_list = []
        self.filename = filename

    def build_tokens(self, text):
        pos = 0
        while pos < len(text):
            match = self.TOKEN_RE.match(text, pos)
            if not match: 
                break
            pos = match.end()

            name = match.lastgroup
            value = match.group(name)

            if name == "whitespace":
                continue
            elif name == "newline":
                name = "separator"

            self.token_list.append(Token(name, value))

    def analyse_text(self):
        try:
            print(self.filename)
            f = open(self.filename, "r")
            self.build_tokens(f.read())
            f.close()
        except IOError:
            print("File does no exist.\n")         

        if self.token_list[-1].value != "\n":
            self.token_list.append(Token("separator", "\n"))

        return self.token_list


if __name__ == "__main__":

    filename = "sample_text.txt"
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    token_list = LexicalAnalyser(filename=filename).analyse_text()
    for token in token_list:
        print(token)