#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test suite with multiple exercises to validate triple generation"""

import sys
sys.path.insert(0, 'c:\\Users\\lssal\\OneDrive\\Escritorio\\Tecnm\\Septimo\\AutoII\\Compilador-2026')

from core.lexer import Lexer
from core.parser import Parser
from models.symbol_table import SymbolTable
from models.error_handler import ErrorHandler
from core.intermediate import TriploGenerator

def print_triplos(title, triplos_list):
    """Imprime los triples en formato tabla"""
    print("\n" + "="*90)
    print(f"{title}")
    print("="*90)
    print(f"{'#':>3} | {'Dato Objeto':>15} | {'Dato Fuente':>20} | {'Operador':<20}")
    print("="*90)
    for t in triplos_list:
        print(f"{t['ID']:>3} | {str(t['Objeto']):>15} | {str(t['Fuente']):>20} | {t['Operador']:<20}")
    print("="*90)

def test_code(title, code):
    """Procesa código y retorna los triples"""
    st = SymbolTable()
    eh = ErrorHandler()
    triplos = TriploGenerator()
    lexer = Lexer(st, eh)
    tokens = lexer.tokenize(code)
    parser = Parser(tokens, st, eh, triplos)
    parser.parse()
    
    triplos_list = triplos.get_all()
    print_triplos(title, triplos_list)
    return triplos_list

# Test 1: Simple variable assignment
print("\n" + "="*90)
print("TEST 1: Simple Assignment")
print("="*90)
test_code("One $x = 10;", """One $x = 10;""")

# Test 2: Arithmetic expression
print("\n" + "="*90)
print("TEST 2: Arithmetic Expression")
print("="*90)
test_code("One $x = 5 + 3;", """One $x = 5 + 3;""")

# Test 3: Multiple operations
print("\n" + "="*90)
print("TEST 3: Multiple Operations")
print("="*90)
test_code("One $x = 10 + 5 * 2;", """One $x = 10 + 5 * 2;""")

# Test 4: For loop simple
print("\n" + "="*90)
print("TEST 4: Simple For Loop")
print("="*90)
test_code("Simple For Loop", """For ($i = 1; $i <= 5; $i = $i + 1)
{
    $x = $i * 2;
}""")

# Test 5: While loop
print("\n" + "="*90)
print("TEST 5: While Loop")
print("="*90)
test_code("While Loop", """One $i = 1;
While ($i < 10)
{
    $i = $i + 1;
}""")

# Test 6: Do-While loop (CRITICAL TEST)
print("\n" + "="*90)
print("TEST 6: Do-While Loop (CRITICAL)")
print("="*90)
test_code("Do-While Loop", """Do
{
    $x = $x + 1;
} While ($x < 10);""")

# Test 7: If condition
print("\n" + "="*90)
print("TEST 7: If Condition")
print("="*90)
test_code("If Condition", """If ($x > 5)
{
    $y = $x * 2;
}""")

# Test 8: Function definition and call
print("\n" + "="*90)
print("TEST 8: Function Definition and Call")
print("="*90)
test_code("Function Call", """One $result;

One $add(One $a, One $b)
{
    $result = $a + $b;
    return $result;
}

$result = $add(3, 4);""")

# Test 9: Complex Do-While with OR (Original Exercise - Key Test)
print("\n" + "="*90)
print("TEST 9: ORIGINAL EXERCISE - Do-While with OR condition")
print("="*90)
test_code("Original Exercise", """One $i3, $res, $b, $c = 3;

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
}""")

# Test 10: Nested loops
print("\n" + "="*90)
print("TEST 10: Nested Loops")
print("="*90)
test_code("Nested Loops", """For ($i = 1; $i <= 3; $i = $i + 1)
{
    For ($j = 1; $j <= 3; $j = $j + 1)
    {
        $result = $i * $j;
    }
}""")

# Validation checks
print("\n" + "="*90)
print("VALIDATION CHECKS")
print("="*90)

print("\n✓ Checking Test 9 (Original Exercise) for T1-only usage...")
triplos_9 = test_code("VALIDATION: Original Exercise", """One $i3, $res, $b, $c = 3;

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
}""")

# Check for T1-only
temps_used = set()
for t in triplos_9:
    if str(t['Objeto']).startswith('T'):
        temps_used.add(t['Objeto'])
    if str(t['Fuente']).startswith('T'):
        temps_used.add(t['Fuente'])

print(f"\nTemporaries used: {sorted(temps_used)}")
if temps_used == {'T1'}:
    print("✅ PASS: Only T1 is used!")
else:
    print(f"❌ FAIL: Multiple temporaries used: {temps_used}")

# Check for TRUE/FALSE format
print("\nChecking TRUE/FALSE format...")
issues = 0
for t in triplos_9:
    if t['Operador'] in ['TRUE', 'FALSE']:
        print(f"  ❌ Line {t['ID']}: {t['Operador']} is in Operador column (should be in Fuente)")
        issues += 1
    if t['Fuente'] in ['TRUE', 'FALSE']:
        if t['Operador'] != 'TRUE' and t['Operador'] != 'FALSE':
            # This is correct format
            pass

if issues == 0:
    print("✅ PASS: TRUE/FALSE format is correct!")
else:
    print(f"❌ FAIL: {issues} formatting issues found")

# Check JMP format
print("\nChecking JMP format...")
for t in triplos_9:
    if t['Operador'] == 'JMP':
        if t['Objeto'] == 'VACÍO':
            print(f"  ✓ Line {t['ID']}: JMP with VACÍO objeto")
        else:
            print(f"  ❌ Line {t['ID']}: JMP with non-VACÍO objeto: {t['Objeto']}")

print("\n" + "="*90)
print("TEST SUITE COMPLETE")
print("="*90)
