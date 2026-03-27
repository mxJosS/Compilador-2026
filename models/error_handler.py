import csv
import os

class ErrorHandler:
    def __init__(self):
        self.errores = []
        self.contador = 1

    def add(self, lexema, renglon, descripcion):
        # CORRECCIÓN: Ahora comparamos también la descripción.
        # Solo omitimos si es EXACTAMENTE el mismo error, lexema y línea.
        for e in self.errores:
            if (e['Lexema'] == lexema and 
                e['Renglón'] == renglon and 
                e['Descripción'] == descripcion):
                return

        token_error = f"ES{self.contador}"
        
        self.errores.append({
            "Token": token_error,
            "Lexema": lexema,
            "Renglón": renglon,
            "Descripción": descripcion
        })
        
        self.contador += 1

    def sort_errors(self):
        """Ordena los errores por número de renglón y reasigna tokens ES1, ES2..."""
        self.errores.sort(key=lambda e: e['Renglón'])
        for i, e in enumerate(self.errores, 1):
            e['Token'] = f"ES{i}"

    def get_all(self):
        return self.errores

    def clear(self):
        self.errores.clear()
        self.contador = 1

    def export_csv(self, filename="salida/tabla_errores.csv"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Token", "Lexema", "Renglón", "Descripción"])
            for e in self.errores:
                writer.writerow([e["Token"], e["Lexema"], e["Renglón"], e["Descripción"]])