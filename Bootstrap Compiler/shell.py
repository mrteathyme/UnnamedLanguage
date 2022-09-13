import lexer

#while True:
#    text = input()
#    result, error = lexer.run('<stdin>',text)
#    if error: print(error.as_string())
#    else: print(result)


while True:
    with open(input()) as file:
        result, error, expression = lexer.run('<stdin>',file.read())
        if error:
            print(error.as_string())
        else:
            print(f'Tokens: {result}\nExpression: {expression[0]}')
