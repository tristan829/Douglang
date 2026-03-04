import time
from typing import Any

from dougterface import Dougterface
from parser import AstNode, BooleanOp, BreakNode, Condition, DougChain, DougNode, DougSequenceExpression, Expression, Literal, LoopNode, PredictionNode, SetNode, SetOp, TTSNode
from tts import TTS

class Break(Exception): pass # Not a real error. Used to propagate breaking up to the deepest loop

class Interpreter:
    def __init__(self, nodes: list[AstNode]):
        self.nodes = nodes
        self.tts = TTS()
        self.values_left = [] # negative indices
        self.values_right = [0] # 0 and positive indices
        self.values_i = 0
    
    def get_value(self, i: int):
        if i < 0:
            idx = abs(i) - 1
            l = self.values_left
        else:
            idx = i
            l = self.values_right
        if idx >= len(l):
            return 0
        return l[idx]

    def set_value(self, i: int, value: Any):
        if i < 0:
            idx = abs(i) - 1
            l = self.values_left
        else:
            idx = i
            l = self.values_right
        length = len(l)
        if idx > length:
            raise RuntimeError(f"You are literally trolling. Do you know how to count? {idx} before {length}?")
        elif idx == length:
            l.append(value)
        else:
            l[idx] = value

    def print_state(self):
        for i, v in enumerate(self.values_left):
            print(f"-{i+1}: {v}")
        for i, v in enumerate(self.values_right):
            print(f"{i}: {v}")

    def get_doug_notation_index(self, chains: list[DougChain], start_i: int):
        result_i = start_i
        
        for i, chain in enumerate(chains):
            value = 1 << (chain.count - 1) # 2^(count-1)

            if i % 2 == 0:
                result_i += value
            else:
                result_i -= value
        
        return result_i
    
    def eval_expression(self, expr: Expression):
        match expr:
            case Literal():
                return expr.value
            case DougSequenceExpression():
                return self.get_value(self.get_doug_notation_index(expr.chains, 0))
            case _:
                raise RuntimeError(f"Unknown expression type {type(expr).__name__}")

    def eval_condition(self, condition: Condition):
        match condition.op:
            case BooleanOp.Equal:
                return self.eval_expression(condition.left) == self.eval_expression(condition.right)
            case BooleanOp.NotEqual:
                return self.eval_expression(condition.left) != self.eval_expression(condition.right)
            case BooleanOp.Less:
                return self.eval_expression(condition.left) < self.eval_expression(condition.right)
            case BooleanOp.LessEqual:
                return self.eval_expression(condition.left) <= self.eval_expression(condition.right)
            case BooleanOp.Greater:
                return self.eval_expression(condition.left) > self.eval_expression(condition.right)
            case BooleanOp.GreaterEqual:
                return self.eval_expression(condition.left) >= self.eval_expression(condition.right)

    def interpret_block(self, nodes: list[AstNode]):
        for node in nodes:
            match node:
                case SetNode():
                    match node.op:
                        case SetOp.Set:
                            self.set_value(self.values_i, self.eval_expression(node.value))
                        case SetOp.Add:
                            left = self.get_value(self.values_i)
                            right = self.eval_expression(node.value)
                            
                            if isinstance(left, str) or isinstance(right, str):
                                # Convert to strings and concatenate
                                self.set_value(self.values_i, str(left) + str(right))
                            else:
                                self.set_value(self.values_i, left + right)
                        case SetOp.Sub:
                            self.set_value(self.values_i, self.get_value(self.values_i) - self.eval_expression(node.value))
                        case SetOp.Mul:
                            self.set_value(self.values_i, self.get_value(self.values_i) * self.eval_expression(node.value))
                        case SetOp.Div:
                            self.set_value(self.values_i, self.get_value(self.values_i) / self.eval_expression(node.value))
                        case SetOp.Mod:
                            self.set_value(self.values_i, self.get_value(self.values_i) % self.eval_expression(node.value))
                        case _:
                            raise RuntimeError(f"Unknown set operation {node.op}")

                case TTSNode():
                    while self.tts.speaking:
                        time.sleep(0.1)
                    
                    if node.use_index:
                        self.tts.speak(str(self.get_value(self.values_i)))
                    else:
                        self.tts.speak(str(self.eval_expression(node.msg)))
                
                case DougNode():
                    self.values_i = self.get_doug_notation_index(node.chains, 0 if node.reset else self.values_i)
                
                case LoopNode():
                    while True:
                        try:
                            self.interpret_block(node.body)
                        except Break:
                            break
                
                case BreakNode():
                    raise Break()
        
                case PredictionNode():
                    # print("\n")
                    # self.print_state()
                    if self.eval_condition(node.condition):
                        self.interpret_block(node.believers_body)
                    else:
                        self.interpret_block(node.doubters_body)
                
                case _:
                    raise RuntimeError(f"Unknown AST node {type(node).__name__}")

        return True

    def run(self):
        Dougterface(self.tts).start()
        self.interpret_block(self.nodes)