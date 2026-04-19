#!/usr/bin/env python3
"""Test script para validar la generación de triples"""

from core.lexer import Lexer
from core.parser import Parser
from models.symbol_table import SymbolTable
from models.error_handler import ErrorHandler
from core.intermediate import TriploGenerator

def print_triplos(triplos_list):
    """Imprime los triples en formato tabla"""
    print("\n" + "="*80)
    print(f"{'#':>3} | {'Dato Objeto':>15} | {'Dato Fuente':>20} | {'Operador':<20}")
    print("="*80)
    for t in triplos_list:
        print(f"{t['ID']:>3} | {str(t['Objeto']):>15} | {str(t['Fuente']):>20} | {t['Operador']:<20}")
    print("="*80)

def test_exercise():
    """Test del ejercicio principal con funciones y Do-While"""
    code = '''One $i3, $res, $b, $c = 3;

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
}'''

    st = SymbolTable()
    eh = ErrorHandler()
    triplos = TriploGenerator()
    lexer = Lexer(code, st, eh)
    tokens = lexer.tokenize()
    parser = Parser(tokens, st, eh, triplos)
    parser.parse()
    
    print("\n✓ EJERCICIO PRINCIPAL")
    print_triplos(triplos.get_all())
    return triplos.get_all()

def test_simple_assignment():
    """Test: asignación simple"""
    code = "One $x = 10;"
    
    st = SymbolTable()
    eh = ErrorHandler()
    triplos = TriploGenerator()
    lexer = Lexer(code, st, eh)
    tokens = lexer.tokenize()
    parser = Parser(tokens, st, eh, triplos)
    parser.parse()
    
    print("\n✓ TEST SIMPLE: One $x = 10;")
    print_triplos(triplos.get_all())
    return triplos.get_all()

def test_expression():
    """Test: expresión"""
    code = "One $x = 5 + 3;"
    
    st = SymbolTable()
    eh = ErrorHandler()
    triplos = TriploGenerator()
    lexer = Lexer(code, st, eh)
    tokens = lexer.tokenize()
    parser = Parser(tokens, st, eh, triplos)
    parser.parse()
    
    print("\n✓ TEST EXPRESIÓN: One $x = 5 + 3;")
    print_triplos(triplos.get_all())
    return triplos.get_all()

def test_for_simple():
    """Test: for simple"""
    code = '''For ($i = 1; $i <= 5; $i = $i + 1)
{
    $x = $i * 2;
}'''
    
    st = SymbolTable()
    eh = ErrorHandler()
    triplos = TriploGenerator()
    lexer = Lexer(code, st, eh)
    tokens = lexer.tokenize()
    parser = Parser(tokens, st, eh, triplos)
    parser.parse()
    
    print("\n✓ TEST FOR SIMPLE")
    print_triplos(triplos.get_all())
    return triplos.get_all()

def test_dowhile_simple():
    """Test: do-while simple"""
    code = '''Do
{
    $x = $x + 1;
} While ($x < 10);'''
    
    st = SymbolTable()
    eh = ErrorHandler()
    triplos = TriploGenerator()
    lexer = Lexer(code, st, eh)
    tokens = lexer.tokenize()
    parser = Parser(tokens, st, eh, triplos)
    parser.parse()
    
    print("\n✓ TEST DO-WHILE SIMPLE")
    print_triplos(triplos.get_all())
    return triplos.get_all()

if __name__ == "__main__":
    try:
        test_simple_assignment()
        test_expression()
        test_for_simple()
        test_dowhile_simple()
        test_exercise()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
