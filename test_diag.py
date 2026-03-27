import re
from models.symbol_table import SymbolTable
from models.error_handler import ErrorHandler
from core.lexer import Lexer
from core.semantic import SemanticAnalyzer

# Probar con DIFERENTES tipos de comillas
print("=== TEST DE COMILLAS ===")
cadena_pattern = '["\\u201c\\u201d][^"\\u201c\\u201d]*["\\u201c\\u201d]'

# Comillas normales
test1 = '$Dos = "Pene"'
# Smart quotes (left/right)
test2 = '$Dos = \u201cPene\u201d'
# Comillas simples
test3 = "$Dos = 'Pene'"

for t in [test1, test2, test3]:
    matches = list(re.finditer(cadena_pattern, t))
    if matches:
        print("OK    : {} -> match: {}".format(repr(t), matches[0].group()))
    else:
        print("FALLO : {} -> NO HAY MATCH".format(repr(t)))

# Probar lo que el textbox puede generar
print("\n=== CARACTERES DE COMILLAS UNICODE COMUNES ===")
quote_chars = ['"', '\u201c', '\u201d', '\u201e', '\u201f', '\u00ab', '\u00bb', '\u2018', '\u2019', "'"]
for q in quote_chars:
    print("  {} U+{:04X} - Match en patron: {}".format(repr(q), ord(q), bool(re.match(cadena_pattern.split(']')[0] + ']', q))))
