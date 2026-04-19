#!/usr/bin/env python3
from core.lexer import Lexer
from core.parser import Parser
from core.intermediate import TriploGenerator
from models.symbol_table import SymbolTable
from models.error_handler import ErrorHandler

codigo = """One $i3, $res, $b, $c = 3;

Two $opera (One $a, Two $w)
{
    $a = $a + 1;
    Do
    {
        $i3 = $w * $a;
        $w = $w + 1;
    } While ($i3 != 1 || $i3 > 1);

    return $i3;
}

For ($a = 1; $a * 2 > $res; $a = $a + 1)
{
    $res = $opera($b, $c);
}
"""

st = SymbolTable()
eh = ErrorHandler()
triplos_gen = TriploGenerator()

lexer = Lexer(st, eh)
lexer.tokenize(codigo)

tokens = lexer.tokens
if tokens:
    parser = Parser(tokens, st, eh, triplos_gen)
    parser.parse()

print("=== ERRORES ===")
errores = eh.get_all()
if not errores:
    print("No hay errores")
else:
    for e in errores:
        print(f"  {e}")

print("\n=== TRIPLOS ===")
for t in triplos_gen.get_all():
    print(f"  {t['ID']}: {t['Objeto']} | {t['Fuente']} | {t['Operador']}")

print(f"\nTotal triplos: {len(triplos_gen.get_all())}")
