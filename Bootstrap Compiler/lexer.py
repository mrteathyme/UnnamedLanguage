import string


TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'
TT_EOF = 'EOF'
TT_STRING = 'STRING'
TT_OPERATOR = 'OPERATOR'
TT_COMMA = 'COMMA'
TT_INDENTS ='INDENTS'

OPERATOR_COMPONENTS = '+=-<>:!/'
KEYWORDS = ['Int32', 'exit', 'return', 'print', 'func', 'class']
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

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value is not None: return f'{self.type}:{self.value}'
        return f'{self.type}'

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
        return Token(TT_OPERATOR, operator)#, pos_start, self.pos)

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

        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
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

def run(fn,text):
    lexer = Lexer(fn,text)
    tokens, error = lexer.make_tokens()

    return tokens, error
