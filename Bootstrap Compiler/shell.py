import lexer

while True:
    with open(input()) as file:
        for line in file:
            result, error, expression = lexer.run('<stdin>',line.rstrip())
            if error:
                print(error.as_string())
            else:
                print(f'Tokens: {result}\nExpression: {expression[0]}')
