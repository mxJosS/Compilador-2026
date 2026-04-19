#!/usr/bin/env python3
"""
Master Architect of Intermediate Code - Generador de Triplos
Basado en la metodología de la Dra. María Italia Jiménez Ochoa
"""

import sys
import os
from core.lexer import Lexer
from core.parser import Parser
from core.intermediate import TriploGenerator
from models.symbol_table import SymbolTable
from models.error_handler import ErrorHandler

def procesar_codigo(codigo, necesita_estar_bien_compilado=False):
    """
    Procesa código fuente y genera triplos.

    Args:
        codigo: String con el código fuente
        necesita_estar_bien_compilado: Si True, solo genera triplos sin errores

    Returns:
        tuple: (triplos, errores, exito)
    """
    st = SymbolTable()
    eh = ErrorHandler()
    triplos_gen = TriploGenerator()

    # Fase 1: Lexer
    lexer = Lexer(st, eh)
    lexer.tokenize(codigo)

    tokens = lexer.tokens

    # Fase 2: Parser (genera triplos)
    if tokens:
        parser = Parser(tokens, st, eh, triplos_gen)
        parser.parse()

    # Verificar errores
    errores = eh.get_all()
    hay_errores = len(errores) > 0

    if necesita_estar_bien_compilado and hay_errores:
        return triplos_gen.get_all(), errores, False

    return triplos_gen.get_all(), errores, True

def imprimir_tabla_triplos(triplos):
    """Imprime tabla de triplos en formato Markdown."""
    print("\n" + "="*60)
    print("TABLA DE TRIPLOS")
    print("="*60)
    print(f"| # | Dato Objeto | Dato Fuente | Operador |")
    print(f"|---|-------------|-------------|----------|")
    for t in triplos:
        print(f"| {t['ID']} | {t['Objeto']:<11} | {t['Fuente']:<11} | {t['Operador']:<8} |")
    print("="*60)

def imprimir_errores(errores):
    """Imprime tabla de errores."""
    if not errores:
        print("[OK] No se detectaron errores")
        return
    print("\n[ALERTA] ERRORES DETECTADOS:")
    print(f"| Token | Lexema | Renglón | Descripción |")
    print(f"|-------|--------|---------|-------------|")
    for e in errores:
        print(f"| {e['Token']:<5} | {e['Lexema']:<6} | {e['Renglón']:<7} | {e['Descripción']:<11} |")

def guardar_csv(triplos, filepath="salida/triplos.csv"):
    """Guarda los triplos en archivo CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("Renglon,Dato Objeto,Dato Fuente,Operador\n")
        for t in triplos:
            f.write(f"{t['ID']},{t['Objeto']},{t['Fuente']},{t['Operador']}\n")
    print(f"[OK] Triplos guardados en: {filepath}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python procesar_triplos.py <archivo.txt> [necesita_estar_bien_compilado]")
        print("  necesita_estar_bien_compilado: true o false (default: false)")
        sys.exit(1)

    archivo = sys.argv[1]
    necesita_compilado = sys.argv[2].lower() == 'true' if len(sys.argv) > 2 else False

    if not os.path.exists(archivo):
        print(f"✗ Error: El archivo '{archivo}' no existe")
        sys.exit(1)

    with open(archivo, 'r', encoding='utf-8') as f:
        codigo = f.read()

    print(f"\n[ARCHIVO] Procesando: {archivo}")
    print(f"[CONFIG] necesita_estar_bien_compilado = {necesita_compilado}")
    print("\n--- CODIGO FUENTE ---")
    print(codigo)
    print("--- FIN CODIGO ---")

    triplos, errores, exito = procesar_codigo(codigo, necesita_compilado)

    if not exito:
        print("\n[ERROR] COMPILACION FALLIDA - Errores de sintaxis detectados")
        imprimir_errores(errores)
        sys.exit(1)

    imprimir_tabla_triplos(triplos)
    imprimir_errores(errores)
    guardar_csv(triplos)

    print(f"\n[OK] Procesamiento completado - {len(triplos)} triplos generados")

if __name__ == "__main__":
    main()
