"""
core/optimizer.py
-----------------
Módulo de Optimización de Código (Fase Placeholder).

Por ahora NO aplica ninguna transformación real.
Simplemente devuelve el código fuente tal como llega,
simulando que la etapa de optimización ya fue ejecutada.

Cuando se implemente la optimización real, basta con reemplazar
el cuerpo de `optimize()` sin cambiar la firma pública.
"""


class CodeOptimizer:
    """Optimizador de código (implementación temporal / mockup)."""

    def __init__(self):
        self._codigo_optimizado: str = ""

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def optimize(self, codigo_fuente: str) -> str:
        """
        Recibe el código fuente y lo retorna sin alterarlo.

        Parámetros
        ----------
        codigo_fuente : str
            El texto del programa a 'optimizar'.

        Retorna
        -------
        str
            El mismo texto de entrada (sin modificaciones, por ahora).
        """
        # TODO: implementar optimizaciones reales (eliminación de código
        #       muerto, propagación de constantes, etc.)
        self._codigo_optimizado = codigo_fuente
        return self._codigo_optimizado

    def get_resultado(self) -> str:
        """Devuelve el último resultado de optimización generado."""
        return self._codigo_optimizado

    def clear(self):
        """Limpia el estado interno para una nueva ejecución."""
        self._codigo_optimizado = ""
