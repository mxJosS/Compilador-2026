import re

class SemanticAnalyzer:
    def __init__(self, symbol_table, error_handler):
        self.st = symbol_table
        self.eh = error_handler
        self.variables_declaradas = set()
        self.funciones_declaradas = {} 
        self.funcion_actual = None 

    def analyze(self, codigo):
        lineas = codigo.split('\n')
        patrones = [
            ('CADENA', r'\"[^\"]*\"'),
            ('REAL', r'\b\d+\.\d+\b'),
            ('ENTERO', r'\b\d+\b'),
            ('TIPO', r'\b(?:One|Two|Tree)\b'),
            ('FOR', r'\bfor\b'),  # CORRECCIÓN 1: FOR agregado a los patrones
            ('RETURN', r'\breturn\b'),
            ('FUNC', r'\$[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()'), # CORRECCIÓN 2: $ estricto
            ('ID', r'\$[A-Za-z0-9]+'),
            ('PALABRA_ERR', r'[a-zA-ZñÑáéíóúÁÉÍÓÚ_][a-zA-ZñÑáéíóúÁÉÍÓÚ0-9_]*'),
            ('ASIGNACION', r'='),
        ]
        regex_unida = '|'.join(f'(?P<{nombre}>{patron})' for nombre, patron in patrones)

        for num_linea, linea in enumerate(lineas, 1):
            tokens_linea = []
            for match in re.finditer(regex_unida, linea):
                tipo_token = match.lastgroup
                lexema = match.group(tipo_token)
                tokens_linea.append((tipo_token, lexema))

            tipo_declaracion = None
            hubo_asignacion = False
            id_izquierdo = None
            hubo_return = False

            for tipo_token, lexema in tokens_linea:
                if tipo_token == 'TIPO':
                    tipo_declaracion = lexema
                
                elif tipo_token == 'RETURN':
                    hubo_return = True
                    
                # CORRECCIÓN 3: Eliminado el "elif tipo_token == 'FOR'". 
                # No necesitamos hacer nada con él en el semántico.
                    
                elif tipo_token == 'FUNC':
                    if tipo_declaracion:
                        if lexema in self.funciones_declaradas or lexema in self.variables_declaradas:
                            self.eh.add(lexema, num_linea, "Variable duplicada")
                        else:
                            self.funciones_declaradas[lexema] = tipo_declaracion
                            self.funcion_actual = lexema
                    else:
                        if lexema not in self.funciones_declaradas:
                            self.eh.add(lexema, num_linea, "Función indefinida")
                            
                elif tipo_token == 'ID':
                    tipo_en_tabla = self._obtener_tipo(lexema)
                    
                    if tipo_declaracion:
                        if lexema in self.variables_declaradas or lexema in self.funciones_declaradas:
                            self.eh.add(lexema, num_linea, "Variable duplicada")
                        else:
                            self.variables_declaradas.add(lexema)
                    else:
                        if tipo_en_tabla == "":
                            self.eh.add(lexema, num_linea, "Variable indefinida")
                            
                    if not hubo_asignacion and not hubo_return:
                        id_izquierdo = lexema

                elif tipo_token == 'PALABRA_ERR':
                    self.eh.add(lexema, num_linea, "Variable indefinida (sin $)")

                elif tipo_token == 'ASIGNACION':
                    hubo_asignacion = True
                
                elif (hubo_asignacion and id_izquierdo) or hubo_return:
                    tipo_del_id = ""
                    
                    if hubo_return:
                        tipo_del_id = self.funciones_declaradas.get(self.funcion_actual, "")
                    else:
                        tipo_del_id = self._obtener_tipo(id_izquierdo)
                        
                    tipo_del_valor = ""
                    
                    if tipo_token == 'ENTERO': tipo_del_valor = "One"
                    elif tipo_token == 'REAL': tipo_del_valor = "Two"
                    elif tipo_token == 'CADENA': tipo_del_valor = "Tree"
                    elif tipo_token == 'ID': tipo_del_valor = self._obtener_tipo(lexema)
                    elif tipo_token == 'FUNC': tipo_del_valor = self.funciones_declaradas.get(lexema, "")
                    
                    if tipo_del_id and tipo_del_valor and tipo_del_id != tipo_del_valor:
                        nombres_tipos = {
                            "One": "One (entero)", 
                            "Two": "Two (real)", 
                            "Tree": "Tree (cadena)"
                        }
                        tipo_desc = nombres_tipos.get(tipo_del_id, tipo_del_id)
                        self.eh.add(lexema, num_linea, f"Incompatibilidad de tipos, {tipo_desc}")
                        hubo_return = False 

    def _obtener_tipo(self, lexema):
        for sim in self.st.get_all():
            if sim["Lexema"] == lexema:
                return sim["Tipo"].replace("-", "") 
        return ""