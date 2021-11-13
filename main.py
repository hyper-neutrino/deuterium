from lexer import lex

print(lex("""
"hello\\U00010000"
"""))
