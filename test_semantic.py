from core.lexer import Lexer
from models.symbol_table import SymbolTable
from models.error_handler import ErrorHandler
from core.semantic import SemanticAnalyzer

# Test completo con todos los tipos de error
codigo = '''One  $Uno, $Dos, $Tres;
Two  $Cuatro, $Cinco, $Seis;
Tree  $Msj, $Whts, $Saludo;

Tree $Operas(){
	One $Opera;
	Return $Opera;
}

$Uno = 3.14;
$Cuatro = "Hola";
$Msj = 42;
$Uno = $Cuatro + 5;
$NoExiste = 10;
$Dos = $OtraInexistente + 1;
$Msj = $FuncNoExiste() + 2;
'''

st = SymbolTable()
eh = ErrorHandler()
lexer = Lexer(st, eh)
lexer.tokenize(codigo)
sem = SemanticAnalyzer(st, eh)
sem.analyze(codigo)

with open('test_output.txt', 'w', encoding='utf-8') as f:
    f.write('=== ERRORES ===\n')
    for e in eh.get_all():
        f.write(f"{e['Token']} | {e['Lexema']} | Linea {e['Renglón']} | {e['Descripción']}\n")
    f.write(f'Total: {len(eh.get_all())}\n')
