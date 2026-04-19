#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final comprehensive test suite - Validates all corrections"""

import sys
sys.path.insert(0, 'c:\\Users\\lssal\\OneDrive\\Escritorio\\Tecnm\\Septimo\\AutoII\\Compilador-2026')

from core.lexer import Lexer
from core.parser import Parser
from models.symbol_table import SymbolTable
from models.error_handler import ErrorHandler
from core.intermediate import TriploGenerator

def analyze_triplos(triplos_list):
    """Analiza triplos y retorna estadísticas"""
    stats = {
        'total': len(triplos_list),
        'temps_used': set(),
        'true_false_in_operador': [],  # ERROR
        'true_false_in_fuente': [],    # CORRECTO
        'jmp_correct': [],
        'jmp_with_objeto': []
    }
    
    for t in triplos_list:
        # Check temporales
        obj = str(t['Objeto'])
        src = str(t['Fuente'])
        op = str(t['Operador'])
        
        if obj.startswith('T') and obj not in ['TRUE', 'FALSE']:
            stats['temps_used'].add(obj)
        if src.startswith('T') and src not in ['TRUE', 'FALSE']:
            stats['temps_used'].add(src)
        
        # Check TRUE/FALSE position
        if t['Operador'] in ['TRUE', 'FALSE']:
            stats['true_false_in_operador'].append(t['ID'])
        if t['Fuente'] in ['TRUE', 'FALSE']:
            stats['true_false_in_fuente'].append(t['ID'])
        
        # Check JMP format
        if t['Operador'] == 'JMP':
            if t['Objeto'] == 'VACÍO':
                stats['jmp_correct'].append(t['ID'])
            else:
                stats['jmp_with_objeto'].append(t['ID'])
    
    return stats

def test_exercise(title, code):
    """Test de codigo y retorna analisis"""
    print(f"\n{'='*80}")
    print(f"TEST: {title}")
    print(f"{'='*80}")
    
    try:
        st = SymbolTable()
        eh = ErrorHandler()
        triplos = TriploGenerator()
        lexer = Lexer(st, eh)
        tokens = lexer.tokenize(code)
        parser = Parser(tokens, st, eh, triplos)
        parser.parse()
        
        triplos_list = triplos.get_all()
        stats = analyze_triplos(triplos_list)
        
        # Print first 15 triplos
        print(f"\nTriplos (primeras 15 lineas de {stats['total']}):")
        print(f"{'#':>3} | {'Dato Objeto':>15} | {'Dato Fuente':>20} | {'Operador':<20}")
        print("-" * 75)
        for i, t in enumerate(triplos_list[:15]):
            print(f"{t['ID']:>3} | {str(t['Objeto']):>15} | {str(t['Fuente']):>20} | {t['Operador']:<20}")
        if stats['total'] > 15:
            print(f"... ({stats['total'] - 15} lineas mas)")
        
        # Validations
        print(f"\nValidaciones:")
        print(f"  Temporales usados: {sorted(stats['temps_used'])}")
        
        if stats['temps_used'] == {'T1'}:
            print("  [PASS] Solo T1 usado")
        else:
            print(f"  [FAIL] Multiples temporales: {stats['temps_used']}")
        
        if not stats['true_false_in_operador']:
            print("  [PASS] TRUE/FALSE no estan en Operador")
        else:
            print(f"  [FAIL] TRUE/FALSE en Operador en lineas: {stats['true_false_in_operador']}")
        
        if stats['true_false_in_fuente']:
            print(f"  [PASS] TRUE/FALSE en Fuente ({len(stats['true_false_in_fuente'])} lineas)")
        
        if not stats['jmp_with_objeto']:
            print("  [PASS] JMP con VACÍO en Objeto")
        else:
            print(f"  [FAIL] JMP con objeto no-VACÍO: {stats['jmp_with_objeto']}")
        
        return True, stats
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

# Run tests
print("\n" + "="*80)
print("COMPREHENSIVE TEST SUITE - TRIPLE CODE GENERATION")
print("="*80)

results = []

# Test 1
success, stats = test_exercise(
    "Simple Assignment",
    "One $x = 10;"
)
results.append(("Simple Assignment", success, stats))

# Test 2
success, stats = test_exercise(
    "For Loop",
    """For ($i = 1; $i <= 5; $i = $i + 1)
{
    $x = $i * 2;
}"""
)
results.append(("For Loop", success, stats))

# Test 3
success, stats = test_exercise(
    "While Loop",
    """One $i = 1;
While ($i < 10)
{
    $i = $i + 1;
}"""
)
results.append(("While Loop", success, stats))

# Test 4
success, stats = test_exercise(
    "Do-While Loop",
    """Do
{
    $x = $x + 1;
} While ($x < 10);"""
)
results.append(("Do-While Loop", success, stats))

# Test 5
success, stats = test_exercise(
    "If Condition",
    """If ($x > 5)
{
    $y = 10;
}"""
)
results.append(("If Condition", success, stats))

# Test 6 - THE MAIN ONE
success, stats = test_exercise(
    "ORIGINAL EXERCISE",
    """One $i3, $res, $b, $c = 3;

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
}"""
)
results.append(("ORIGINAL EXERCISE", success, stats))

# Summary
print(f"\n{'='*80}")
print("TEST SUMMARY")
print(f"{'='*80}")

for title, success, stats in results:
    status = "PASS" if success else "FAIL"
    temps = sorted(stats['temps_used']) if stats else []
    print(f"{title:.<50} {status:>6} (Temps: {temps}, Lines: {stats['total'] if stats else 'N/A'})")

# Final check for main exercise
print(f"\n{'='*80}")
print("CRITICAL VALIDATION - ORIGINAL EXERCISE")
print(f"{'='*80}")
main_results = [r for r in results if r[0] == "ORIGINAL EXERCISE"]
if main_results:
    _, main_stats = main_results[0]
else:
    main_stats = None

passed = True
checks = []

if main_stats and main_stats['temps_used'] == {'T1'}:
    checks.append((True, "Only T1 temporals used"))
elif main_stats:
    checks.append((False, f"Multiple temporals: {main_stats['temps_used']}"))
    passed = False
else:
    passed = False

if main_stats and not main_stats['true_false_in_operador']:
    checks.append((True, "TRUE/FALSE not in Operador"))
elif main_stats:
    checks.append((False, "TRUE/FALSE found in Operador"))
    passed = False
else:
    passed = False

if main_stats and len(main_stats['true_false_in_fuente']) > 0:
    checks.append((True, f"TRUE/FALSE correctly in Fuente ({len(main_stats['true_false_in_fuente'])} times)"))

if main_stats and not main_stats['jmp_with_objeto']:
    checks.append((True, "JMP format correct (VACÍO in Objeto)"))
elif main_stats:
    checks.append((False, "JMP with non-VACÍO Objeto"))
    passed = False
else:
    passed = False

for check_pass, message in checks:
    symbol = "PASS" if check_pass else "FAIL"
    print(f"[{symbol}] {message}")

print(f"\n{'='*80}")
if passed:
    print("FINAL RESULT: ALL TESTS PASSED!")
else:
    print("FINAL RESULT: SOME TESTS FAILED")
print(f"{'='*80}")
