import csv

class SymbolTable:
    def __init__(self):
        self.simbolos = {}
        
    def add(self, lexema, tipo=""):
        if lexema not in self.simbolos:
            self.simbolos[lexema] = tipo
        elif tipo != "" and self.simbolos[lexema] == "":
            self.simbolos[lexema] = tipo
            
    def get_all(self):
        return [{"Lexema": k, "Tipo": v} for k, v in self.simbolos.items()]
        
    def clear(self):
        self.simbolos.clear()
        
    def export_csv(self, filename="salida/tabla_simbolos.csv"):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Lexema", "Tipo de dato"])
            for lexema, tipo in self.simbolos.items():
                writer.writerow([lexema, tipo])