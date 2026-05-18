#!/usr/bin/env python3
from core.lexer import Lexer
from models.symbol_table import SymbolTable
from models.error_handler import ErrorHandler

codigo = """One $Res = $Suma($A, $B);"""

st = SymbolTable()
eh = ErrorHandler()
lexer = Lexer(st, eh)
lexer.tokenize(codigo)

print("TOKENS GENERADOS:")
for i, token in enumerate(lexer.tokens):
    print(f"  {i}: tipo={token['tipo']}, lexema={token['lexema']}, linea={token['linea']}")
