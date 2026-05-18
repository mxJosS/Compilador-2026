"""
core/code_gen.py
----------------
Módulo de Generación de Código Objeto (Fase Placeholder).

Flujo que ejecuta este módulo:
  1. Recibe el código optimizado (o fuente) como entrada.
  2. Vuelve a ejecutar, de forma secuencial, los tres procesos ya
     existentes: Tabla de Símbolos, Tabla de Errores y Tríplos.
  3. Expone la función `ensamblador()` que, por ahora, devuelve
     un bloque de código ensamblador hardcoded a modo de ejemplo.

Cuando se implemente la generación real, basta con:
  - Reemplazar el cuerpo de `ensamblador()` con la traducción real
    de tríplos a instrucciones de bajo nivel.
  - El método `reprocesar()` ya deja listos los objetos actualizados.
"""

from core.lexer import Lexer
from core.parser import Parser
from core.semantic import SemanticAnalyzer
from models.symbol_table import SymbolTable
from models.error_handler import ErrorHandler
from core.intermediate import TriploGenerator


# Texto hardcoded de ejemplo en ensamblador
_ASM_PLACEHOLDER = """\
; ============================================================
;  Código Ensamblador  –  EJEMPLO (placeholder)
; ============================================================

        .MODEL SMALL
        .STACK 100h
        .DATA
        .CODE

MAIN    PROC
        ; ejemplo en ensamblador
        Mov Ax, H

        MOV AH, 4Ch
        INT 21h
MAIN    ENDP
        END MAIN
"""


class CodeGenerator:
    """Generador de código objeto (implementación temporal / mockup)."""

    def __init__(self):
        # Instancias internas para el reprocesamiento
        self._st = SymbolTable()
        self._eh = ErrorHandler()
        self._triplos = TriploGenerator()

        self._asm_output: str = ""

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def reprocesar(self, codigo_fuente: str) -> dict:
        """
        Vuelve a ejecutar –de forma secuencial– Lexer → Parser → Semántico
        sobre el código recibido (que ya pasó por la etapa de optimización).

        Parámetros
        ----------
        codigo_fuente : str
            El código a reprocesar (salida del optimizador).

        Retorna
        -------
        dict con claves:
            'simbolos'  → lista de símbolos  (igual que st.get_all())
            'errores'   → lista de errores   (igual que eh.get_all())
            'triplos'   → lista de tríplos   (igual que triplos.get_all())
        """
        # Limpiar estado previo
        self._st.clear()
        self._eh.clear()
        self._triplos.clear()

        # 1. Análisis léxico
        lexer_obj = Lexer(self._st, self._eh)
        lexer_obj.tokenize(codigo_fuente)

        # 2. Análisis sintáctico + generación de tríplos
        tokens = lexer_obj.tokens
        if tokens:
            parser_obj = Parser(tokens, self._st, self._eh, self._triplos)
            parser_obj.parse()

        # 3. Análisis semántico
        semantic_obj = SemanticAnalyzer(self._st, self._eh)
        semantic_obj.analyze(codigo_fuente)

        self._eh.sort_errors()

        return {
            "simbolos": self._st.get_all(),
            "errores":  self._eh.get_all(),
            "triplos":  self._triplos.get_all(),
        }

    def ensamblador(self) -> str:
        """
        Genera (o retorna) el código ensamblador resultante.

        Por ahora devuelve un bloque hardcoded de ejemplo.

        TODO: implementar la traducción real de tríplos a instrucciones
              de ensamblador x86 / MIPS / o el target deseado.

        Retorna
        -------
        str
            Texto con el código ensamblador.
        """
        # TODO: recorrer self._triplos.get_all() y traducir cada tríplo
        self._asm_output = _ASM_PLACEHOLDER
        return self._asm_output

    def get_asm(self) -> str:
        """Devuelve el último código ensamblador generado."""
        return self._asm_output

    def clear(self):
        """Limpia el estado interno para una nueva ejecución."""
        self._st.clear()
        self._eh.clear()
        self._triplos.clear()
        self._asm_output = ""
