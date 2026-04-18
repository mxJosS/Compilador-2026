import re

class Lexer:
    def __init__(self, symbol_table, error_handler):
        self.st = symbol_table
        self.eh = error_handler
        self.tokens = [] # <--- NUEVO: Para guardar los tokens para el Parser
        self.tipos_declaracion = ["One", "Two", "Tree"]

    def tokenize(self, codigo):
        self.tokens = [] # <--- NUEVO: Limpiar la lista en cada análisis
        patrones = [
            ('CADENA', '["\u201c\u201d][^"\u201c\u201d]*["\u201c\u201d]'),
            ('REAL', r'\b\d+\.\d+\b'),
            ('ENTERO', r'\b\d+\b'),
            ('TIPO', r'\b(?:One|Two|Tree)\b'),
            ('FOR', r'\bfor\b'),
            ('RETURN', r'\b[Rr]eturn\b'),
            ('FUNC', r'\$[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()'),
            ('ID', r'\$[A-Za-z0-9]+'),
            ('PALABRA_ERR', r'[a-zA-ZñÑáéíóúÁÉÍÓÚ_][a-zA-ZñÑáéíóúÁÉÍÓÚ0-9_]*'),
            ('OP_LOG', r'&&|\|\|'),
            ('OP_REL', r'==|!=|<=|>=|<|>'),
            ('OP_ARIT', r'[\+\-\*\/\%]'),
            ('ASIGNACION', r'='),
            ('MISC', r'[\(\)\{\}\;\,]'),
            ('ESPACIO', r'\s+'),
            ('ERROR', r'.'),
        ]
        regex_unida = '|'.join(f'(?P<{nombre}>{patron})' for nombre, patron in patrones)
        lineas = codigo.split('\n')
        tipo_actual = ""

        for num_linea, linea in enumerate(lineas, 1):
            for match in re.finditer(regex_unida, linea):
                tipo_token = match.lastgroup
                lexema = match.group(tipo_token)
                
                if tipo_token == 'ESPACIO' or tipo_token == 'ERROR':
                    continue
                
                # --- NUEVO: Guardamos el token para el Parser ---
                self.tokens.append({
                    "lexema": lexema, 
                    "tipo": tipo_token, 
                    "linea": num_linea
                })

                # Lógica existente para la tabla de símbolos
                if tipo_token == 'TIPO':
                    self.st.add(lexema, "")
                    tipo_actual = lexema    
                elif lexema == ';':
                    self.st.add(lexema, "")
                    tipo_actual = ""
                elif tipo_token in ['RETURN', 'FOR', 'OP_ARIT', 'OP_REL', 'OP_LOG', 'ASIGNACION', 'MISC']:
                    self.st.add(lexema, "")
                elif tipo_token == 'FUNC':
                    tipo_a_guardar = f"{tipo_actual}" if tipo_actual else ""
                    self.st.add(lexema, tipo_a_guardar)
                elif tipo_token == 'PALABRA_ERR':
                    self.st.add(lexema, "")
                    self.eh.add(lexema, num_linea, "Variable indefinida (sin $)")
                elif tipo_token == 'ID':
                    tipo_a_guardar = f"{tipo_actual}" if tipo_actual else ""
                    self.st.add(lexema, tipo_a_guardar)
                elif tipo_token == 'ENTERO':
                    self.st.add(lexema, "One") 
                elif tipo_token == 'REAL':
                    self.st.add(lexema, "Two") 
                elif tipo_token == 'CADENA':
                    self.st.add(lexema, "Tree")