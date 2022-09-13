import lexer

#while True:
#    text = input()
#    result, error = lexer.run('<stdin>',text)
#    if error: print(error.as_string())
#    else: print(result)

while True:
    with open(input()) as file:
        for line in file:
            #text = open(input(), "r").readlines()
            #text = input()
            result, error = lexer.run('<stdin>',line.rstrip())
            if error: print(error.as_string())
            else: print(result)