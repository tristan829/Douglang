from abc import ABC as Abstract, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any
from lexer import AddSetToken, BaldToken, BelieversToken, BreakToken, ComparisonEqualToken, ComparisonGreaterEqualToken, ComparisonGreaterToken, ComparisonLessEqualToken, ComparisonLessToken, ComparisonNotEqualToken, DivSetToken, DoubtersToken, DougToken, LParenToken, LSquareToken, LiteralToken, LoopToken, ModSetToken, MulSetToken, PredictionToken, RParenToken, RSquareToken, SetToken, SubSetToken, TTSToken, Token, WinToken

class BooleanOp(Enum):
    Equal        = auto()
    NotEqual     = auto()
    Greater      = auto()
    Less         = auto()
    GreaterEqual = auto()
    LessEqual    = auto()

class SetOp(Enum):
    Set = auto()
    Add = auto()
    Sub = auto()
    Mul = auto()
    Div = auto()
    Mod = auto()

SET_TOKEN_TO_OP = {
    SetToken:    SetOp.Set,
    AddSetToken: SetOp.Add,
    SubSetToken: SetOp.Sub,
    MulSetToken: SetOp.Mul,
    DivSetToken: SetOp.Div,
    ModSetToken: SetOp.Mod,
}

class AstNode: pass

class Expression: pass

@dataclass
class Literal(Expression):
    value: Any

@dataclass
class DougChain:
    count: int

@dataclass
class DougSequenceExpression(Expression):
    chains: list[DougChain]

# Different from Doug expression
# Expressions evaluate to the value stored at the selected index, a chain moves the selected index
@dataclass
class DougNode(AstNode):
    chains: list[DougChain]
    reset: bool

@dataclass
class TTSNode(AstNode):
    msg: Expression
    use_index: bool = False

@dataclass
class SetNode(AstNode):
    value: Expression
    op: SetOp

@dataclass
class LoopNode(AstNode):
    body: list[AstNode]

class BreakNode(AstNode): pass

@dataclass
class Condition:
    left: Expression
    op: BooleanOp
    right: Expression

COMPARISON_OPS = {
    ComparisonEqualToken:        BooleanOp.Equal,
    ComparisonNotEqualToken:     BooleanOp.NotEqual,
    ComparisonGreaterToken:      BooleanOp.Greater,
    ComparisonGreaterEqualToken: BooleanOp.GreaterEqual,
    ComparisonLessToken:         BooleanOp.Less,
    ComparisonLessEqualToken:    BooleanOp.LessEqual,
}

@dataclass
class PredictionNode(AstNode):
    believers_body: list[AstNode]
    doubters_body: list[AstNode]
    condition: Condition

class ParseError(Exception):
    def __init__(self, line: int, column: int, msg: str):
        self.msg = f"You are literally trolling. {msg} on line {line}, column {column}"
        super().__init__(self.msg)

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.i = -1
        self.length = len(tokens)

    def consume(self):
        self.i += 1
        return self.tokens[self.i] if self.i < self.length else False

    def peek(self):
        next_index = self.i + 1
        return self.tokens[next_index] if next_index < self.length else False

    def parse(self):
        # Top-level parse just calls parse_block with is_top=True
        return self.parse_block(is_top=True)

    def parse_block(self, is_top=False) -> list[AstNode]:
        nodes: list[AstNode] = []

        while token := self.consume():
            match token:
                case TTSToken():
                    token2 = self.peek()
                    match token2:
                        case LiteralToken():
                            self.consume()
                            nodes.append(TTSNode(Literal(token2.value)))
                        case LParenToken():
                            self.consume()
                            dougs = self.parse_doug_expr()
                            nodes.append(TTSNode(DougSequenceExpression(dougs)))
                        case _:
                            nodes.append(TTSNode(None, use_index=True))

                case SetToken() | AddSetToken() | SubSetToken() | MulSetToken() | DivSetToken() | ModSetToken():
                    op = SET_TOKEN_TO_OP[type(token)]
                    token2 = self.consume()
                    match token2:
                        case LiteralToken():
                            nodes.append(SetNode(Literal(token2.value), op))
                        case LParenToken():
                            dougs = self.parse_doug_expr()
                            nodes.append(SetNode(DougSequenceExpression(dougs), op))

                case BaldToken() | DougToken():
                    nodes.append(self.parse_doug_node(token))

                case LoopToken():
                    token2 = self.consume()
                    if not isinstance(token2, LSquareToken):
                        raise ParseError(token2.line, token2.column, f"Expected '[', got {type(token2).__name__}")
                    body = self.parse_block()
                    nodes.append(LoopNode(body))

                case PredictionToken():
                    condition = self.parse_condition()

                    # Expect outer prediction [
                    l_bracket = self.consume()
                    if not isinstance(l_bracket, LSquareToken):
                        raise ParseError(l_bracket.line, l_bracket.column,
                                        f"Expected '[', got {type(l_bracket).__name__}")

                    # First branch (Believers or Doubters)
                    first_branch_token = self.consume()
                    if not isinstance(first_branch_token, (DoubtersToken, BelieversToken)):
                        raise ParseError(first_branch_token.line, first_branch_token.column,
                                        "Expected BelieversToken or DoubtersToken at start of prediction block")

                    wins_token = self.consume()
                    if not isinstance(wins_token, WinToken):
                        raise ParseError(wins_token.line, wins_token.column,
                                        f"Expected `wins`, got {type(wins_token).__name__}")

                    first_body = self.parse_block()

                    first_is_doubters = isinstance(first_branch_token, DoubtersToken)
                    doubters_body: list[AstNode] = first_body if first_is_doubters else []
                    believers_body: list[AstNode] = first_body if not first_is_doubters else []

                    # Optional second branch (must be opposite)
                    second_branch_token = self.peek()
                    if isinstance(second_branch_token, (DoubtersToken, BelieversToken)):
                        self.consume()

                        if type(second_branch_token) == type(first_branch_token):
                            raise ParseError(second_branch_token.line, second_branch_token.column,
                                            "Second branch must be opposite of first in prediction")

                        wins_token = self.consume()
                        if not isinstance(wins_token, WinToken):
                            raise ParseError(wins_token.line, wins_token.column,
                                            f"Expected `wins`, got {type(wins_token).__name__}")

                        second_body = self.parse_block()

                        if isinstance(second_branch_token, BelieversToken):
                            believers_body = second_body
                        else:
                            doubters_body = second_body

                    # Consume closing ] of prediction block
                    closing = self.consume()
                    if not isinstance(closing, RSquareToken):
                        raise ParseError(closing.line, closing.column,
                                        "Expected ']' to close prediction block")

                    nodes.append(PredictionNode(
                        believers_body=believers_body,
                        doubters_body=doubters_body,
                        condition=condition
                    ))

                case BreakToken():
                    nodes.append(BreakNode())

                case RSquareToken():
                    if is_top:
                        raise ParseError(token.line, token.column, "Unexpected ']'")
                    return nodes

        if not is_top:
            raise ParseError(self.i, 0, "Expected ']' to close block")

        return nodes

    def parse_doug_node(self, token):
        chains: list[DougChain] = [] if isinstance(token, BaldToken) else [DougChain(count=token.count)]
        reset = isinstance(token, BaldToken)

        while isinstance(self.peek(), DougToken):
            next_token = self.consume()
            chains.append(DougChain(count=next_token.count))

        return DougNode(chains=chains, reset=reset)

    def parse_doug_expr(self):
        dougs: list[DougChain] = []
        while token := self.consume():
            match token:
                case DougToken():
                    dougs.append(DougChain(count=token.count))
                case RParenToken():
                    return dougs
                case _:
                    raise ParseError(token.line, token.column, f"Expected DougToken or ')', got {type(token).__name__}")

    def parse_condition(self):
        token = self.consume()
        left: Expression
        
        match token:
            case LParenToken():
                left = DougSequenceExpression(self.parse_doug_expr())
            case LiteralToken():
                left = Literal(token.value)
            case _:
                raise ParseError(token.line, token.column, f"Expected expression, got {type(token).__name__}")

        token_op = self.consume()
        op = COMPARISON_OPS.get(type(token_op))
        if not op:
            raise ParseError(token_op.line, token_op.column, f"Expected comparison operator, got {type(token_op).__name__}")

        token_right = self.consume()
        match token_right:
            case LParenToken():
                right = DougSequenceExpression(self.parse_doug_expr())
            case LiteralToken():
                right = Literal(token_right.value)
            case _:
                raise ParseError(token_right.line, token_right.column, f"Expected expression, got {type(token_right).__name__}")

        return Condition(left, op, right)