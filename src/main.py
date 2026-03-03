import sys
from lexer import lex
from parser import Parser
from interpreter import Interpreter

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Provide input file")
    with open(sys.argv[1], "r") as f:
        if not f:
            raise Exception("Couldn't find input file")
        source = f.read()

    try:
        Interpreter(Parser(lex(source)).parse()).run()
    except KeyboardInterrupt:
        pass