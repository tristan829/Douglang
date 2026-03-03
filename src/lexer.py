from dataclasses import dataclass
import sys
import time
from typing import Any

@dataclass
class Token:
    line: int
    column: int

# Doug notation
@dataclass
class DougToken(Token):
    count: int

@dataclass
class BaldToken(Token): pass

# Keywords
@dataclass
class TTSToken(Token): pass

class SetToken(Token): pass
class AddSetToken(Token): pass
class SubSetToken(Token): pass
class MulSetToken(Token): pass
class DivSetToken(Token): pass
class ModSetToken(Token): pass

class LoopToken(Token): pass
class BreakToken(Token): pass

@dataclass
class LiteralToken(Token):
    value: Any

class LParenToken(Token): pass
class RParenToken(Token): pass 
    
class LSquareToken(Token): pass
class RSquareToken(Token): pass

class PredictionToken(Token): pass
class BelieversToken(Token): pass
class DoubtersToken(Token): pass
class WinToken(Token): pass

class ComparisonEqualToken(Token): pass
class ComparisonNotEqualToken(Token): pass
class ComparisonGreaterToken(Token): pass
class ComparisonLessToken(Token): pass
class ComparisonGreaterEqualToken(Token): pass
class ComparisonLessEqualToken(Token): pass

# Keyword mapping. And symbols, too.
KEYWORDS = {
    "tts": TTSToken,
    "set": SetToken,
    "+set": AddSetToken,
    "-set": SubSetToken,
    "*set": MulSetToken,
    "/set": DivSetToken,
    "%set": ModSetToken,
    "loop": LoopToken,
    "break": BreakToken,
    "prediction": PredictionToken,
    "Believers": BelieversToken,
    "Doubters": DoubtersToken,
    "win": WinToken,
    "(": LParenToken,
    ")": RParenToken,
    "[": LSquareToken,
    "]": RSquareToken,
    "=": ComparisonEqualToken,
    "!=": ComparisonNotEqualToken,
    ">": ComparisonGreaterToken,
    ">=": ComparisonGreaterEqualToken,
    "<": ComparisonLessToken,
    "<=": ComparisonLessEqualToken,
}

# Ensure the dictionary is sorted in the order of most characters first
KEYWORDS = dict(
    sorted(KEYWORDS.items(), key=lambda item: len(item[0]), reverse=True)
)

class LexError(Exception):
    def __init__(self, line: int, column: int, msg: str):
        self.msg = f"You are literally trolling. {msg} on line {line}, column {column}"
        super().__init__(self.msg)

def lex(source: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    line = 1
    column = 1
    length = len(source)

    while i < length:
        c = source[i]

        # Newline
        if c == '\n':
            i += 1
            line += 1
            column = 1
            continue

        # Whitespace (space or tab)
        if c.isspace():
            i += 1
            column += 1
            continue

        # Comments
        if source.startswith("//", i):
            while i < length and source[i] != '\n':
                i += 1
                column += 1
            if i < length and source[i] == '\n':
                i += 1
                line += 1
                column = 1
            continue

        # Doug/Bald notation
        if source.startswith("Bald", i):
            tokens.append(BaldToken(line, column))
            i += 4
            column += 4
            continue

        if source.startswith("Doug", i):
            start_column = column
            count = 0
            while source.startswith("Doug", i):
                count += 1
                i += 4
                column += 4
            tokens.append(DougToken(line, start_column, count))
            continue

        # Keywords
        matched = False
        for keyword, token_class in KEYWORDS.items():
            if source.startswith(keyword, i):
                tokens.append(token_class(line, column))
                i += len(keyword)
                column += len(keyword)
                matched = True
                break
        if matched:
            continue

        # Strings (handle multi-line)
        if c in ('"', "'"):
            quote_char = c
            start_i = i
            start_line = line
            start_column = column
            i += 1
            column += 1
            string_content = ""
            while i < length:
                if source[i] == '\\' and i + 1 < length:
                    string_content += source[i:i+2]
                    i += 2
                    column += 2
                elif source[i] == quote_char:
                    i += 1
                    column += 1
                    break
                else:
                    if source[i] == '\n':
                        string_content += '\n'
                        line += 1
                        column = 1
                        i += 1
                    else:
                        string_content += source[i]
                        i += 1
                        column += 1
            else:
                raise LexError(start_line, start_column, "Unterminated string literal")
            tokens.append(LiteralToken(start_line, start_column, string_content))
            continue

        # Numbers
        if c.isdigit() or c == '.':
            start_i = i
            start_column = column
            has_decimal_point = c == '.'
            while i < length and (source[i].isdigit() or source[i] == '.'):
                if source[i] == '.':
                    if has_decimal_point:
                        raise LexError(line, column, "Malformed number")
                    has_decimal_point = True
                i += 1
                column += 1
            tokens.append(LiteralToken(line, start_column, float(source[start_i:i]) if has_decimal_point else int(source[start_i:i])))
            continue

        # Unknown token
        raise LexError(line, column, "Unknown token")

    return tokens

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Provide input file")
    with open(sys.argv[1], "r") as f:
        if not f:
            raise Exception("Couldn't find input file")
        source = f.read()
    start_time = time.perf_counter()
    result = lex(source)
    end_time = time.perf_counter()
    print(f"Took {end_time - start_time:.6f} seconds")
    for t in result:
        print(t)