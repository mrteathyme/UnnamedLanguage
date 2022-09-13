from ast import Expression
from lib2to3.pgen2.token import tok_name
import string


TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_LSPAREN = 'LSPAREN'
TT_RSPAREN = 'RSPAREN'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'
TT_EOF = 'EOF'
TT_STRING = 'STRING'
TT_OPERATOR = 'OPERATOR'
TT_COMMA = 'COMMA'
TT_INDENTS ='INDENTS'
TT_BOOLEAN = 'BOOLEAN'
OPERATOR_COMPONENTS = '+=-<>:!/.*'
OPERATORS = {
    '+': 'PLUS',
    '==': 'EQUALTO',
    '-': 'MINUS',
    '*': 'MUL',
    '/': 'DIV'}
KEYWORDS = ['Int32', 'exit', 'return', 'print', 'func', 'class', 'while', 'for', 'if', 'else', 'import', 'with', 'File', 'open', 'input', 'in','strip']
BOOLEAN_KEYWORDS = ['True', 'False']
class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt
    
    def advance(self, current_char):
        self.idx += 1
        self.col +=1

        if current_char == '\n':
            self.ln +=1
            self.col = 0
        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

class Error:
    def __init__(self, pos_start, pos_end,  error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f', File {self.pos_start.fn}, line {self.pos_start.ln +1}'
        return result

class IllegalCharError(Error):
    def __init__(self,  pos_start, pos_end,details):
        super().__init__( pos_start, pos_end,'Illegal Character', details)

class IllegalOperatorError(Error):
    def __init__(self,  pos_start, pos_end,details):
        super().__init__( pos_start, pos_end,'Illegal Operator', details)

class InvalidSyntaxError(Error):
    def __init__(self,  pos_start, pos_end,details):
        super().__init__( pos_start, pos_end,'Illegal Syntax', details)

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value is not None: return f'"{self.type}":"{self.value}"'
        return f'"{self.type}"'

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []
        tokens.append(Token(TT_INDENTS,max(len(self.text) - len(self.text.lstrip()),0)))
        while self.current_char != None:
            if self.current_char in '0123456789':
                tokens.append(self.make_number())
            elif self.current_char in OPERATOR_COMPONENTS:
                tokens.append(self.make_operator())
            elif self.current_char in string.ascii_letters:
                tokens.append(self.make_identifier())
            elif self.current_char in '\'\"':
                tokens.append(self.make_string())
            elif self.current_char in ' \t': # We count indents with an lstrip comparison before the loop so we dont actually want to count whitespaces
                self.advance()
            elif self.current_char in '(':
                    tokens.append(Token(TT_LPAREN))
                    self.advance()
            elif self.current_char in ')':
                    tokens.append(Token(TT_RPAREN))
                    self.advance()
            elif self.current_char in '[':
                    tokens.append(Token(TT_LSPAREN))
                    self.advance()
            elif self.current_char in ']':
                    tokens.append(Token(TT_RSPAREN))
                    self.advance()
            elif self.current_char in ',':
                tokens.append(Token(TT_COMMA))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos,char)
        return tokens, None

    def make_operator(self):
        operator = ''
        pos_start = self.pos.copy()
        while self.current_char != None and self.current_char in OPERATOR_COMPONENTS:
            operator += self.current_char
            self.advance()
        if operator not in OPERATORS:
            return [], IllegalOperatorError(pos_start, self.pos, operator)
        return Token(OPERATORS[operator])#, pos_start, self.pos)

    def make_string(self):
        string = ''
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {
            'n':'\n',
            't':'\t'
            }

        while self.current_char != None and self.current_char not in '\'\"' or escape_character == True:
            if escape_character:
                escape_character = False
                string += escape_characters[self.current_char]
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()
        self.advance()
        return Token(TT_STRING, string)#, pos_start, self.pos)
    def make_identifier(self):
        id_str = ""
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in string.ascii_letters + '0123456789' + '_':
            id_str += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_BOOLEAN if id_str in BOOLEAN_KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_str)#, pos_start, self.pos)




    def make_number(self):
        num_str = ''
        dot_count = 0
        while self.current_char != None and self.current_char in '0123456789' + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = 0
        self.current_tok = None
        self.advance()
        

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expression()
        return res, res.value if res else res, None

    def factor(self):
        tok = self.current_tok

        if tok.type in(OPERATORS['+'], OPERATORS['-']):
            self.advance()
            factor = self.factor()
            return UnaryOpNode(tok, factor)
        
        if tok.type == TT_LPAREN:
            self.advance()
            expression = self.expression()
            if self.current_tok.type == TT_RPAREN:
                self.advance()
                return expression
            else:
                InvalidSyntaxError(0, 0, "Expected ')'")

        elif tok.type in (TT_INT, TT_FLOAT):
            self.advance()
            return NumberNode(tok)
    
    def term(self):
        return self.bin_op(self.factor, (OPERATORS['*'], OPERATORS['/']))

    def expression(self):
        return self.bin_op(self.term, (OPERATORS['+'], OPERATORS['-']))


    def bin_op(self, func, ops):
        left = func()
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            self.advance()
            right = func()
            left = BinOpNode(left, op_tok, right)
        return left
class NumberNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'

    @property
    def value(self):
        return self.tok

class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
    
    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'
    
    @property
    def value(self):
        return [self.left_node, [self.op_tok, self.right_node]]

class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node
    
    def __repr__(self):
        return f'({self.op_tok}, {self.node})'
    
    @property
    def value(self):
        return [self.op_tok, self.node]

def run(fn,text):
    lexer = Lexer(fn,text)
    tokens, error = lexer.make_tokens()
    parser = Parser(tokens)
    return tokens, error, parser.parse()
